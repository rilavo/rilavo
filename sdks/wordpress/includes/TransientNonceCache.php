<?php
namespace Rilavo;

/**
 * WordPress transient-based nonce cache.
 *
 * @package RilavoMU
 */

if (!defined('ABSPATH')) {
    exit;
}

use Rilavo\NonceCacheInterface;

final class TransientNonceCache implements NonceCacheInterface {
    
    public function check(string $nonce): bool {
        return get_transient('rilavo_nonce_' . $nonce) !== false;
    }
    
    public function add(string $nonce, int $ttl): void {
        set_transient('rilavo_nonce_' . $nonce, true, $ttl);
    }
}
