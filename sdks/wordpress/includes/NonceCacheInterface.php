<?php
namespace Rilavo;

/**
 * Interface for nonce cache implementations.
 *
 * @package RilavoMU
 */

if (!defined('ABSPATH')) {
    exit;
}

interface NonceCacheInterface {
    
    public function check(string $nonce): bool;
    
    public function add(string $nonce, int $ttl): void;
}
