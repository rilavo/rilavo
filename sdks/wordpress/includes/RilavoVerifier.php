<?php
namespace Rilavo;

/**
 * PSR-4 shim: credential verifier with the full fail-closed gate pipeline
 * The canonical implementation lives in class-rilavo-verifier.php (global namespace).
 * This shim loads it and aliases the class into the Rilavo namespace
 * so composer-autoloaded tests use the REAL, fail-closed implementation.
 */

if (!defined('ABSPATH')) {
    define('ABSPATH', '/tmp/wp/');
}

require_once __DIR__ . '/class-rilavo-verifier.php';

if (!class_exists('Rilavo\RilavoVerifier', false)) {
    class_alias('\\RilavoVerifier', 'Rilavo\RilavoVerifier');
}
