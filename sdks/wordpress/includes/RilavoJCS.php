<?php
namespace Rilavo;

/**
 * PSR-4 shim: JCS subset canonical JSON serializer (byte-compatible with Python/TS)
 * The canonical implementation lives in class-rilavo-jcs.php (global namespace).
 * This shim loads it and aliases the class into the Rilavo namespace
 * so composer-autoloaded tests use the REAL, fail-closed implementation.
 */

if (!defined('ABSPATH')) {
    define('ABSPATH', '/tmp/wp/');
}

require_once __DIR__ . '/class-rilavo-jcs.php';

if (!class_exists('Rilavo\RilavoJCS', false)) {
    class_alias('\\RilavoJCS', 'Rilavo\RilavoJCS');
}
