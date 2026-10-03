<?php
/**
 * Plugin Name: Rilavo Agent Verification
 * Description: Fail-closed Rilavo gate for WordPress (P2-B5).
 * Version: 0.1.0
 * Author: Rilavo Contributors
 * License: Apache-2.0
 * Requires at least: 5.9
 * Requires PHP: 8.1
 * Text Domain: rilavo-verification
 */

// Exit if accessed directly
if (!defined('ABSPATH')) {
    exit;
}

// Require the Rilavo SDK (assumes composer install in plugin dir)
require_once __DIR__ . '/vendor/autoload.php';

use Rilavo\Verifier;
use Rilavo\KeyDirectory;
use Rilavo\RevocationLog;
use Rilavo\NonceCache;

class Rilavo_Verification {

    private $verifier;
    private $audience;

    public function __construct() {
        $this->audience = get_option('rilavo_audience', 'YOUR_AUDIENCE_HERE');

        // Initialize trust sources
        $directory = new KeyDirectory();
        // $directory->publish(...) // Add your issuer key entry

        $revocationLog = new RevocationLog();
        $nonceCache = new NonceCache();

        $this->verifier = new Verifier($directory, $revocationLog, $nonceCache);

        // Hook into WordPress
        add_action('init', [$this, 'register_hooks']);
        add_action('admin_menu', [$this, 'admin_menu']);
        add_action('admin_init', [$this, 'register_settings']);

        // REST API gate
        add_filter('rest_pre_dispatch', [$this, 'gate_rest_request'], 10, 3);
        // Admin gate (optional)
        // add_action('admin_init', [$this, 'gate_admin_request']);
    }

    public function register_hooks() {
        // Register AJAX endpoints for PoP
        add_action('wp_ajax_nopriv_rilavo_pop', [$this, 'pop_endpoint']);
    }

    public function admin_menu() {
        add_options_page(
            'Rilavo Verification',
            'Rilavo Verification',
            'manage_options',
            'rilavo-verification',
            [$this, 'settings_page']
        );
    }

    public function register_settings() {
        register_setting('rilavo_options', 'rilavo_audience');
        register_setting('rilavo_options', 'rilavo_issuer_key');
    }

    public function settings_page() {
        ?>
        <div class="wrap">
            <h1>Rilavo Verification Settings</h1>
            <form method="post" action="options.php">
                <?php settings_fields('rilavo_options'); ?>
                <table class="form-table">
                    <tr>
                        <th scope="row">Audience</th>
                        <td><input type="text" name="rilavo_audience" value="<?php echo esc_attr(get_option('rilavo_audience')); ?>" class="regular-text"></td>
                    </tr>
                    <tr>
                        <th scope="row">Issuer Public Key (PEM)</th>
                        <td><textarea name="rilavo_issuer_key" class="large-text code"><?php echo esc_textarea(get_option('rilavo_issuer_key')); ?></textarea></td>
                    </tr>
                </table>
                <?php submit_button(); ?>
            </form>
        </div>
        <?php
    }

    public function gate_rest_request($dispatch_result, $request, $route) {
        // Skip non-REST or public routes
        if (is_wp_error($dispatch_result) || $this->is_public_route($request)) {
            return $dispatch_result;
        }

        // Get credential from header
        $cred_header = $request->get_header('X-Rilavo-Credential');
        if (!$cred_header) {
            return new WP_Error('no_credentials', 'Missing credential', ['status' => 401]);
        }

        // Decode credential
        $fields = json_decode(base64_decode($cred_header), true);
        if (!$fields) {
            return new WP_Error('malformed_credential', 'Invalid credential encoding', ['status' => 401]);
        }

        // Build PoP request
        $pop = [
            'method' => $request->get_method(),
            'path' => $request->get_route(),
            'requestedAction' => $request->get_header('X-Rilavo-Action') ?? '',
            'signature' => $request->get_header('X-Rilavo-Pop-Signature') ?? '',
            'requestNonce' => $request->get_header('X-Rilavo-Request-Nonce') ?? '',
        ];

        try {
            $result = $this->verifier->verify($fields, $pop, [
                'issuerDirectory' => $directory,
                'revocationLog' => $revocationLog,
                'nonceCache' => $nonceCache,
                'verifierAudience' => $this->audience,
            ]);
        } catch (Exception $e) {
            return new WP_Error('verification_failed', $e->getMessage(), ['status' => 401]);
        }

        if (!$result['accepted']) {
            return new WP_Error($result['reasonCode'], 'Verification failed', ['status' => 401]);
        }

        return $dispatch_result;
    }

    private function is_public_route($request) {
        $public = ['/wp-json/wp/v2/', '/wp-json/oembed/'];
        $route = $request->get_route();
        foreach ($public as $p) {
            if (strpos($route, $p) === 0) return true;
        }
        return false;
    }
}

// Initialize
new Rilavo_Verification();
