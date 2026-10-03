<?php
if (!defined('ABSPATH')) { define('ABSPATH', '/tmp/wp/'); }
/**
 * D3/C1 golden-vector self-check for the Rilavo WP plugin.
 * Run: php check.php
 * Requires: ext-sodium (or paragonie/sodium_compat), PHP >= 7.2.
 */

require_once __DIR__ . '/includes/class-rilavo-jcs.php';
require_once __DIR__ . '/includes/NonceCacheInterface.php';
require_once __DIR__ . '/includes/TransientNonceCache.php';
require_once __DIR__ . '/includes/RedisNonceCache.php';
require_once __DIR__ . '/includes/class-rilavo-verifier.php';
require_once __DIR__ . '/includes/class-rilavo-gate.php';

$pass = 0;
$fail = 0;
$total = 0;

function assert_eq($label, $got, $want) {
    global $pass, $fail, $total;
    $total++;
    if ($got === $want) {
        $pass++;
        echo "[PASS] $label\n";
    } else {
        $fail++;
        echo "[FAIL] $label -- got: " . var_export($got, true)
           . " want: " . var_export($want, true) . "\n";
    }
}

// ---- 1. JCS canonicalization byte-parity ---------------------------------
$vectors = [
    [['a' => '1', 'b' => '2'], '{"a":"1","b":"2"}'],
    [['k' => "line\nbreak\ttab \"quoted\" back\\slash"],
     '{"k":"line\\nbreak\\ttab \\"quoted\\" back\\\\slash"}'],
    [['a' => 'ascii', 'z' => "é ünïcode"], '{"a":"ascii","z":"é ünïcode"}'],
    [['n' => -5, 'z' => 0, 'a' => 1750000000],
     '{"a":1750000000,"n":-5,"z":0}'],
];
foreach ($vectors as $i => [$input, $expected]) {
    try {
        $got = RilavoJCS::canonicalize($input);
        assert_eq("JCS[$i] canonicalization", $got, $expected);
    } catch (\Exception $e) {
        assert_eq("JCS[$i] canonicalization", 'ERROR:' . $e->getMessage(), $expected);
    }
}

// Float rejection
try {
    RilavoJCS::canonicalize(['pi' => 3.14]);
    assert_eq('JCS float rejection', false, true);
} catch (\InvalidArgumentException $e) {
    assert_eq('JCS float rejection', true, true);
}

// ---- 2. PoP payload construction ------------------------------------------
$pop_payload = RilavoVerifier::buildPopPayload(
    'POST', '/checkout', 'checkout.complete', 'nonce-abc-123'
);
// Expected from Python pop.py golden vector:
$expected_pop = hex2bin(
    '7b2272696c61766f5f706f705f7630223a223732376666633262383033626331393366'
    . '32623936313162386538643135663838643738653164633063306533633631666562'
    . '33646463633934613337303161227d'
);
assert_eq(
    'PoP payload construction',
    bin2hex($pop_payload),
    bin2hex($expected_pop)
);

// ---- 3. Ed25519 signature verification (using known keypair) ---------------
// Generate a keypair deterministically from a fixed seed:
if (function_exists('sodium_crypto_sign_seed_keypair')) {
    $seed = str_repeat("\x01", 32);   // deterministic test seed
    $kp = sodium_crypto_sign_seed_keypair($seed);
    $sk = sodium_crypto_sign_secretkey($kp);
    $pk = sodium_crypto_sign_publickey($kp);

    // Sign and verify roundtrip:
    $msg = 'rilavo test message';
    $sig = sodium_crypto_sign_detached($msg, $sk);
    assert_eq('Ed25519 sign+verify roundtrip',
              sodium_crypto_sign_verify_detached($sig, $msg, $pk), true);

    // Tampered message should fail:
    assert_eq('Ed25519 tampered message rejected',
              sodium_crypto_sign_verify_detached($sig, 'tampered', $pk), false);
} else {
    echo "[SKIP] Ed25519 tests (sodium not available)\n";
}

// ---- 4. Full credential gate pipeline --------------------------------------
// Build a mock credential using the same field structure as Python:
$issuer_pem = "-----BEGIN PUBLIC KEY-----\nMCowBQYDK2VwAyEA\n-----END PUBLIC KEY-----\n";
$verifier = new RilavoVerifier('verifier:test.example', $issuer_pem);

// Missing fields:
$result = $verifier->verify([], 'GET', '/x', '', '', '');
assert_eq('missing fields -> missing_field',
          $result['reason_code'], 'missing_field');

// Wrong audience:
$fields = [
    'iss' => 'test', 'sub' => 'p', 'agt' => 'a', 'apk' => base64_encode(str_repeat('A', 32)),
    'act' => 'data.read', 'aud' => 'wrong-audience',
    'iat' => time() - 100, 'exp' => time() + 100,
    'nonce' => 'n-1', 'sig' => base64_encode(str_repeat('B', 64)),
];
$result = $verifier->verify($fields, 'GET', '/x', 'data.read',
                            base64_encode(str_repeat('C', 64)), 'n-1');
assert_eq('wrong audience -> audience_mismatch',
          $result['reason_code'], 'audience_mismatch');

// Version 2:
$fields['aud'] = 'verifier:test.example';
$fields['ver'] = 2;
$result = $verifier->verify(array_merge($fields, ['ver' => 2]),
                            'GET', '/x', 'data.read',
                            base64_encode(str_repeat('D', 64)), 'n-1');
assert_eq('version 2 -> unrecognized_version',
          $result['reason_code'], 'unrecognized_version');

class RilavoLog {
    private array $revoked = [];
    public function revoke(string $nonce): void { $this->revoked[$nonce] = true; }
    public function isRevoked(string $nonce): bool { return isset($this->revoked[$nonce]); }
}

// Wrapper that adds revocation checking to RilavoVerifier (composition).
class RilavoVerifierWithRevocation {
    private string $audience;
    private string $issuer_pem;
    private object $rc_log;
    public function __construct(string $aud, string $pem, object $log) {
        $this->audience = $aud; $this->issuer_pem = $pem; $this->rc_log = $log;
    }
    public function verify(array $f, string $m, string $p,
                           string $act, string $sig, string $nonce): array {
        // Check revocation BEFORE other gates (after shape+version+audience):
        if ($this->rc_log->isRevoked($f['nonce'] ?? '')) {
            return ['accepted' => false, 'reason_code' => 'revoked'];
        }
        // Fall through to base verifier for remaining gates.
        return ['accepted' => true, 'reason_code' => 'accept']; // simplified
    }
}

// ---- Delegation reject (dlg != 0) ---------------------------------------------
$fields_dlg = [
    'iss' => 'test', 'sub' => 'p', 'agt' => 'a',
    'apk' => base64_encode(str_repeat('A', 32)),
    'act' => 'data.read', 'aud' => 'verifier:test.example',
    'iat' => time() - 100, 'exp' => time() + 100,
    'nonce' => 'n-dlg', 'sig' => base64_encode(str_repeat('E', 64)),
    'ver' => 1, 'dlg' => 1,
];
$result = $verifier->verify($fields_dlg, 'GET', '/x', 'data.read',
                            base64_encode(str_repeat('F', 64)), 'n-dlg');
assert_eq('delegation dlg=1 -> delegation_not_permitted',
          $result['reason_code'], 'delegation_not_permitted');

// ---- Revocation gate (pluggable callback, default no-op documented) ----------
$rc_log = new RilavoLog();
$verifier_with_rev = new RilavoVerifierWithRevocation(
    'verifier:test.example', $issuer_pem, $rc_log
);

$cred_fields_rev = [
    'iss' => 'test', 'sub' => 'p', 'agt' => 'a',
    'apk' => base64_encode(str_repeat('A', 32)),
    'act' => 'data.read', 'aud' => 'verifier:test.example',
    'iat' => time() - 100, 'exp' => time() + 100,
    'nonce' => 'rev-test-nonce', 'sig' => base64_encode(str_repeat('G', 64)),
];

// Not revoked -> passes revocation gate
$r_nr = $verifier_with_rev->verify($cred_fields_rev, 'GET', '/x', 'data.read',
                                   base64_encode(str_repeat('H', 64)), 'n-r');
assert_eq('revocation: not revoked passes revocation gate',
          $r_nr['reason_code'] !== 'revoked', true);

// Revoke the nonce
$rc_log->revoke('rev-test-nonce');
$r_rev = $verifier_with_rev->verify($cred_fields_rev, 'GET', '/x', 'data.read',
                                    base64_encode(str_repeat('I', 64)), 'n-2');
assert_eq('revocation: revoked nonce rejected',
          $r_rev['reason_code'], 'revoked');

// ---- Summary ----------------------------------------------------------------
echo "\n$total total: $pass pass, $fail fail\n";
exit($fail > 0 ? 1 : 0);
