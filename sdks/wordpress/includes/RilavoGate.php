<?php
namespace Rilavo;

/**
 * Gate: verifies incoming WP REST requests against a Rilavo credential.
 * Returns WP_Error on reject, null on pass.
 *
 * @package RilavoMU
 */

if (!defined('ABSPATH')) {
    define('ABSPATH', '/tmp/wp/');
}

final class RilavoGate {

    private string $audience;
    private string $issuer_pem;
    private RilavoVerifier $verifier;

    public function __construct(string $audience, string $issuer_pem) {
        $this->audience = $audience;
        $this->issuer_pem = $issuer_pem;
        $this->verifier = new RilavoVerifier($audience, $issuer_pem);
    }

    public function verify_wp_request($request) {
        $cred_raw = $request->get_header('x-rilavo-credential');
        if (empty($cred_raw)) {
            return new WP_Error(
                'rilavo_no_credentials',
                'Rilavo verification failed: no_credentials',
                ['status' => 401]
            );
        }

        $fields = json_decode($cred_raw, true);
        if (!is_array($fields)) {
            return new WP_Error(
                'rilavo_malformed_credential',
                'Rilavo verification failed: malformed_credential',
                ['status' => 401]
            );
        }

        $method = $request->get_method();
        $path = $request->get_route();
        $act = $request->get_header('x-rilavo-action') ?? '';
        $sig = $request->get_header('x-rilavo-pop-signature') ?? '';
        $nonce = $request->get_header('x-rilavo-request-nonce') ?? '';

        $result = $this->verifier->verify(
            $fields, $method, $path, $act, $sig, $nonce
        );

        if (!$result['accepted']) {
            return new WP_Error(
                'rilavo_' . $result['reason_code'],
                'Rilavo verification failed: ' . $result['reason_code'],
                ['status' => 401]
            );
        }

        return null; // Pass through.
    }
}
