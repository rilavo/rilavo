<?php
/**
 * Bootstrap file for PHPUnit tests.
 * Loads the plugin classes and test helpers.
 */

// Define ABSPATH for standalone testing
if (!defined('ABSPATH')) {
    define('ABSPATH', '/tmp/wp/');
}

// Load Composer autoloader if available
$autoload = __DIR__ . '/../vendor/autoload.php';
if (file_exists($autoload)) {
    require_once $autoload;
}

// Load plugin classes
// require_once __DIR__ . '/../includes/class-rilavo-jcs.php'; // loaded via autoloader
// require_once __DIR__ . '/../includes/class-rilavo-verifier.php'; // loaded via autoloader
// require_once __DIR__ . '/../includes/class-rilavo-gate.php'; // loaded via autoloader

// Test helper functions
function assert_eq($label, $got, $want) {
    global $pass, $fail, $total;
    $total++;
    if ($got === $want) {
        $pass++;
        echo "[PASS] $label
";
    } else {
        $fail++;
        echo "[FAIL] $label
";
        echo "       Got:      " . var_export($got, true) . "
";
        echo "       Want:     " . var_export($want, true) . "
";
    }
}

function assert_not_eq($label, $got, $want) {
    global $pass, $fail, $total;
    $total++;
    if ($got !== $want) {
        $pass++;
        echo "[PASS] $label
";
    } else {
        $fail++;
        echo "[FAIL] $label
";
        echo "       Got:      " . var_export($got, true) . "
";
        echo "       Want:     " . var_export($want, true) . "
";
    }
}

// Load golden vectors
function load_golden_vectors(): array {
    $path = __DIR__ . '/../../golden/golden.json';
    if (!file_exists($path)) {
        $path = __DIR__ . '/../../../golden/golden.json';
    }
    return json_decode(file_get_contents($path), true);
}

function load_reject_vectors(): array {
    $path = __DIR__ . '/../../golden/rejects.json';
    if (!file_exists($path)) {
        $path = __DIR__ . '/../../../golden/rejects.json';
    }
    return json_decode(file_get_contents($path), true);
}

// Global counters
$pass = 0;
$fail = 0;
$total = 0;

function report_results(): void {
    global $pass, $fail, $total;
    echo "
$total total: $pass pass, $fail fail
";
    if ($fail > 0) {
        exit(1);
    }
}
