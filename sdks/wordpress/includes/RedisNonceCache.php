<?php
namespace Rilavo;

/**
 * Redis-based nonce cache.
 *
 * @package RilavoMU
 */

if (!defined('ABSPATH')) {
    exit;
}

use Rilavo\NonceCacheInterface;

final class RedisNonceCache implements NonceCacheInterface {
    
    private \Redis $redis;
    
    public function __construct(\Redis $redis) {
        $this->redis = $redis;
    }
    
    public function check(string $nonce): bool {
        return $this->redis->exists('rilavo:nonce:' . $nonce);
    }
    
    public function add(string $nonce, int $ttl): void {
        $this->redis->setex('rilavo:nonce:' . $nonce, $ttl, '1');
    }
}
