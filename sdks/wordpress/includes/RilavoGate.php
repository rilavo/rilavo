<?php
namespace Rilavo;

/**
 * PSR-4 shim: WordPress REST API gate
 * The canonical implementation lives in class-rilavo-gate.php (global namespace).
 * This shim loads it and aliases the class into the Rilavo namespace
 * so composer-autoloaded tests use the REAL, fail-closed implementation.
 */

if (!defined('ABSPATH')) {
    define('ABSPATH', '/tmp/wp/');
}

require_once __DIR__ . '/class-rilavo-gate.php';

if (!class_exists('Rilavo\RilavoGate', false)) {
    class_alias('\\RilavoGate', 'Rilavo\RilavoGate');
}
