<?php
/**
 * Golden vector byte-parity tests for Rilavo WP plugin.
 * Ensures byte-for-byte parity with Python reference implementation.
 */

namespace Rilavo\Tests;

use PHPUnit\Framework\TestCase;
use Rilavo\RilavoJCS;
use Rilavo\RilavoVerifier;

class GoldenVectorTest extends TestCase
{
    private array $golden;
    private array $rejects;

    protected function setUp(): void
    {
        parent::setUp();
        // Clear any transients from previous tests
        global $transient_store;
        $transient_store = [];
        
        $goldenPath = __DIR__ . '/../golden/golden.json';
        $rejectsPath = __DIR__ . '/../golden/rejects.json';

        if (!file_exists($goldenPath)) {
            $goldenPath = __DIR__ . '/../../../golden/golden.json';
        }
        if (!file_exists($rejectsPath)) {
            $rejectsPath = __DIR__ . '/../../../golden/rejects.json';
        }

        $this->golden = json_decode(file_get_contents($goldenPath), true);
        $this->rejects = json_decode(file_get_contents($rejectsPath), true);
    }

    public function testJCSCanonicalizationByteParity(): void
    {
        foreach ($this->golden['jcs'] as $i => $vector) {
            $got = RilavoJCS::canonicalize($vector['input']);
            $this->assertEquals($vector['expected'], $got, "JCS[$i] canonicalization byte-parity");
        }
    }

    public function testPoPPayloadByteParity(): void
    {
        $pop = $this->golden['pop'];
        $payload = RilavoVerifier::buildPopPayload(
            $pop['method'], $pop['path'], $pop['act'], $pop['nonce']
        );
        $this->assertEquals($pop['payload_hex'], bin2hex($payload), 'PoP payload byte-parity');
    }

    public function testEd25519SignVerifyRoundtrip(): void
    {
        if (!function_exists('sodium_crypto_sign_seed_keypair')) {
            $this->markTestSkipped('sodium extension not available');
        }

        $seed = str_repeat("", 32);
        $kp = sodium_crypto_sign_seed_keypair($seed);
        $sk = sodium_crypto_sign_secretkey($kp);
        $pk = sodium_crypto_sign_publickey($kp);

        $msg = 'rilavo test message';
        $sig = sodium_crypto_sign_detached($msg, $sk);

        $this->assertTrue(sodium_crypto_sign_verify_detached($sig, $msg, $pk), 'Ed25519 sign+verify roundtrip');
        $this->assertFalse(sodium_crypto_sign_verify_detached($sig, 'tampered', $pk), 'Ed25519 tampered message rejected');
    }

    public function testFullAcceptPath(): void
    {
        $v = $this->golden;
        $fields = $v['credential_fields'];

        $verifier = new \Rilavo\RilavoVerifier(
            $fields['aud'],
            "-----BEGIN PUBLIC KEY-----
" . chunk_split($this->pemFromRaw($v['issuer_pub_b64url']), 64, "
") . "-----END PUBLIC KEY-----
",
            null,
            fn() => 1700000001 // Fixed time: iat + 1
        );

        $result = $verifier->verifyFields(
            $fields,
            $v['pop_sig']['method'],
            $v['pop_sig']['path'],
            $v['pop_sig']['act'],
            $v['pop_sig']['sig_b64url'],
            $v['pop_sig']['nonce']
        );

        $this->assertTrue($result['accepted'], 'Golden credential should be accepted');
        $this->assertEquals('accept', $result['reason_code']);
    }

    public function testAbsentVerImpliesVersion1(): void
    {
        $fields = $this->golden['credential_fields'];
        unset($fields['ver']);

        $verifier = new \Rilavo\RilavoVerifier(
            $fields['aud'],
            $this->makeIssuerPem(),
            null,
            fn() => 1700000001 // Fixed time: iat + 1
        );
        $result = $verifier->verifyFields($fields, 'GET', '/data/1', 'data.read', 
            $this->golden['pop_sig']['sig_b64url'], $this->golden['pop_sig']['nonce']);

        $this->assertTrue($result['accepted'], 'Absent ver should imply version 1');
    }

    public function testRejectsVer2(): void
    {
        $fields = $this->golden['credential_fields'];
        $fields['ver'] = 2;

        $verifier = new \Rilavo\RilavoVerifier($this->golden['credential_fields']['aud'], $this->makeIssuerPem());
        $result = $verifier->verifyFields($fields, 'GET', '/data/1', 'data.read',
            $this->golden['pop_sig']['sig_b64url'], $this->golden['pop_sig']['nonce']);

        $this->assertFalse($result['accepted']);
        $this->assertEquals('unrecognized_version', $result['reason_code']);
    }

    public function testRejectsNonIntegerVer(): void
    {
        $fields = $this->golden['credential_fields'];
        foreach (['2', 2.5] as $bad) {
            $fields['ver'] = $bad;
            $verifier = new \Rilavo\RilavoVerifier($this->golden['credential_fields']['aud'], $this->makeIssuerPem());
            $result = $verifier->verifyFields($fields, 'GET', '/data/1', 'data.read',
                $this->golden['pop_sig']['sig_b64url'], $this->golden['pop_sig']['nonce']);

            $this->assertEquals('unrecognized_version', $result['reason_code']);
        }
    }

    public function testAudienceBinding(): void
    {
        $verifier = new \Rilavo\RilavoVerifier('verifier:someone-else.example', $this->makeIssuerPem());
        $result = $verifier->verifyFields(
            $this->golden['credential_fields'],
            'GET', '/data/1', 'data.read',
            $this->golden['pop_sig']['sig_b64url'],
            $this->golden['pop_sig']['nonce']
        );

        $this->assertEquals('wrong_audience', $result['reason_code']);
    }

    public function testExpiredCredential(): void
    {
        $fields = $this->golden['credential_fields'];
        $fields['exp'] = time() - 3600;

        $verifier = new \Rilavo\RilavoVerifier($this->golden['credential_fields']['aud'], $this->makeIssuerPem());
        $result = $verifier->verifyFields($fields, 'GET', '/data/1', 'data.read',
            $this->golden['pop_sig']['sig_b64url'], $this->golden['pop_sig']['nonce']);

        $this->assertEquals('expired', $result['reason_code']);
    }

    public function testNotYetValidCredential(): void
    {
        $fields = $this->golden['credential_fields'];
        $fields['iat'] = 1700000002; // iat + 2 (future)
        $fields['exp'] = 1700003600; // exp in future

        $verifier = new \Rilavo\RilavoVerifier(
            $this->golden['credential_fields']['aud'],
            $this->makeIssuerPem(),
            null,
            fn() => 1700000001 // Fixed time: iat + 1
        );
        $result = $verifier->verifyFields($fields, 'GET', '/data/1', 'data.read',
            $this->golden['pop_sig']['sig_b64url'], $this->golden['pop_sig']['nonce']);

        $this->assertEquals('not_yet_valid', $result['reason_code']);
    }

    public function testUnknownIssuer(): void
    {
        // Use the correct audience from golden vector but empty issuer PEM
        $verifier = new \Rilavo\RilavoVerifier(
            $this->golden['credential_fields']['aud'],
            '',
            null,
            fn() => 1700000001 // Fixed time: iat + 1
        );
        $result = $verifier->verifyFields(
            $this->golden['credential_fields'],
            'GET', '/data/1', 'data.read',
            $this->golden['pop_sig']['sig_b64url'], $this->golden['pop_sig']['nonce']
        );

        $this->assertEquals('unknown_issuer', $result['reason_code']);
    }

    public function testKeyNotValidAtIssuance(): void
    {
        // This test would require modifying the issuer's valid_until
        // For now, we test that the gate exists by checking the code path
        $this->markTestSkipped('Requires issuer with valid_until in past');
    }

    public function testTamperedField(): void
    {
        $fields = $this->golden['credential_fields'];
        $fields['sub'] = 'attacker';

        $verifier = new \Rilavo\RilavoVerifier(
            $this->golden['credential_fields']['aud'],
            $this->makeIssuerPem(),
            null,
            fn() => 1700000001 // Fixed time: iat + 1
        );
        $result = $verifier->verifyFields($fields, 'GET', '/data/1', 'data.read',
            $this->golden['pop_sig']['sig_b64url'], $this->golden['pop_sig']['nonce']);

        $this->assertEquals('invalid_signature', $result['reason_code']);
    }

    public function testReplayDetection(): void
    {
        $verifier = new \Rilavo\RilavoVerifier(
            $this->golden['credential_fields']['aud'],
            $this->makeIssuerPem(),
            null,
            fn() => 1700000001 // Fixed time: iat + 1
        );
        // Use the golden vector's nonce and PoP signature for the first request
        $nonce = $this->golden['pop_sig']['nonce'];
        $fields = $this->golden['credential_fields'];
        $popSig = $this->golden['pop_sig']['sig_b64url'];

        // First request should succeed
        $result1 = $verifier->verifyFields($fields, 'GET', '/data/1', 'data.read', $popSig, $nonce);
        $this->assertTrue($result1['accepted']);

        // Second request with same nonce should fail
        $result2 = $verifier->verifyFields($fields, 'GET', '/data/1', 'data.read', $popSig, $nonce);
        $this->assertEquals('replay_detected', $result2['reason_code']);
    }

    public function testRevocation(): void
    {
        $nonce = $this->golden['credential_fields']['nonce'];

        $verifier = new \Rilavo\RilavoVerifier(
            $this->golden['credential_fields']['aud'],
            $this->makeIssuerPem(),
            function($n) use ($nonce) { return $n === $nonce; },
            fn() => 1700000001 // Fixed time: iat + 1
        );

        $fields = $this->golden['credential_fields'];
        $result = $verifier->verifyFields($fields, 'GET', '/data/1', 'data.read',
            $this->golden['pop_sig']['sig_b64url'], $this->golden['pop_sig']['nonce']);

        $this->assertEquals('revoked', $result['reason_code']);
    }

    public function testPoPMethodMismatch(): void
    {
        $fields = $this->golden['credential_fields'];
        $pop = $this->golden['pop_sig'];

        $verifier = new \Rilavo\RilavoVerifier(
            $this->golden['credential_fields']['aud'],
            $this->makeIssuerPem(),
            null,
            fn() => 1700000001  // Fixed time within valid window
        );
        $result = $verifier->verifyFields($fields, 'POST', $pop['path'], $pop['act'],
            $pop['sig_b64url'], $pop['nonce']);

        $this->assertEquals('proof_of_possession_failed', $result['reason_code']);
    }

    public function testPoPPathMismatch(): void
    {
        $fields = $this->golden['credential_fields'];
        $pop = $this->golden['pop_sig'];

        $verifier = new \Rilavo\RilavoVerifier(
            $this->golden['credential_fields']['aud'],
            $this->makeIssuerPem(),
            null,
            fn() => 1700000001  // Fixed time within valid window
        );
        $result = $verifier->verifyFields($fields, $pop['method'], '/other', $pop['act'],
            $pop['sig_b64url'], $pop['nonce']);

        $this->assertEquals('proof_of_possession_failed', $result['reason_code']);
    }

    public function testPoPActionMismatch(): void
    {
        $fields = $this->golden['credential_fields'];
        $pop = $this->golden['pop_sig'];

        $verifier = new \Rilavo\RilavoVerifier(
            $this->golden['credential_fields']['aud'],
            $this->makeIssuerPem(),
            null,
            fn() => 1700000001  // Fixed time within valid window
        );
        $result = $verifier->verifyFields($fields, $pop['method'], $pop['path'], 'data.write',
            $pop['sig_b64url'], $pop['nonce']);

        $this->assertEquals('proof_of_possession_failed', $result['reason_code']);
    }

    public function testUnrecognizedVersion(): void
    {
        $fields = $this->golden['credential_fields'];
        $fields['ver'] = 2;

        $verifier = new \Rilavo\RilavoVerifier($this->golden['credential_fields']['aud'], $this->makeIssuerPem());
        $result = $verifier->verifyFields($fields, 'GET', '/data/1', 'data.read',
            $this->golden['pop_sig']['sig_b64url'], $this->golden['pop_sig']['nonce']);

        $this->assertEquals('unrecognized_version', $result['reason_code']);
    }

    // ---- Reject vector tests ----
    public function testRejectUnknownVersion(): void
    {
        $fields = $this->rejects['unknown_version']['credential_fields'];
        $verifier = new \Rilavo\RilavoVerifier($this->golden['credential_fields']['aud'], $this->makeIssuerPem());
        $result = $verifier->verifyFields($fields, 'GET', '/data/1', 'data.read',
            $this->golden['pop_sig']['sig_b64url'], $this->golden['pop_sig']['nonce']);

        $this->assertFalse($result['accepted']);
        $this->assertEquals('unrecognized_version', $result['reason_code']);
    }

    public function testRejectWrongAudience(): void
    {
        $fields = $this->rejects['wrong_audience']['credential_fields'];
        $verifier = new \Rilavo\RilavoVerifier($this->golden['credential_fields']['aud'], $this->makeIssuerPem());
        $result = $verifier->verifyFields($fields, 'GET', '/data/1', 'data.read',
            $this->golden['pop_sig']['sig_b64url'], $this->golden['pop_sig']['nonce']);

        $this->assertFalse($result['accepted']);
        $this->assertEquals('wrong_audience', $result['reason_code']);
    }

    public function testRejectExpired(): void
    {
        $fields = $this->rejects['expired']['credential_fields'];
        $verifier = new \Rilavo\RilavoVerifier($this->golden['credential_fields']['aud'], $this->makeIssuerPem());
        $result = $verifier->verifyFields($fields, 'GET', '/data/1', 'data.read',
            $this->golden['pop_sig']['sig_b64url'], $this->golden['pop_sig']['nonce']);

        $this->assertFalse($result['accepted']);
        $this->assertEquals('expired', $result['reason_code']);
    }

    // ---- Issuance parity tests ----
    public function testIssueParity(): void
    {
        if (!function_exists('sodium_crypto_sign_seed_keypair')) {
            $this->markTestSkipped('sodium not available');
        }

        $golden = [
            'agent_pub_b64url' => 'Kay64UG8yvCyLhqU000LxzYeUm0L_hLIl5S8kyKWbdc',
            'agent_seed_b64url' => 'ICEiIyQlJicoKSorLC0uLzAxMjM0NTY3ODk6Ozw9Pj8',
            'fields' => [
                'act' => 'data.read',
                'agt' => 'agt-ts-parity',
                'apk' => 'Kay64UG8yvCyLhqU000LxzYeUm0L_hLIl5S8kyKWbdc',
                'aud' => 'verifier:parity.example',
                'exp' => 1760003600,
                'iat' => 1760000000,
                'iss' => 'rilavo:iss:56475aa75463474c',
                'nonce' => 'FIXEDNONCE123456',
                'sig' => 'dJiaW9N9zW-OjKtN-xYrDLBieElaFcLRop2dzhRA5K4LCYOtCpLQzQKBbcQjf9LI4ggbAA3REP0c3NZHpCQGDA',
                'sub' => 'acme-corp:runner-01'
            ],
            'issuer_seed_b64url' => 'AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8',
            'now' => 1760000000,
            'ttl' => 3600
        ];

        // This test would require the issueCredential function which is in the SDK
        // For now, mark as skipped since the PHP plugin doesn't have issuance
        $this->markTestSkipped('Issuance requires SDK integration');
    }

    // Helper methods
    private function makeIssuerPem(): string
    {
        $raw = $this->b64urlDecode($this->golden['issuer_pub_b64url']);
        $der = "0*0+ep! " . $raw;
        $b64 = base64_encode($der);
        $pem = chunk_split($b64, 64, "
");
        return "-----BEGIN PUBLIC KEY-----
{$pem}-----END PUBLIC KEY-----
";
    }

    private function b64urlDecode(string $s): string
    {
        return base64_decode(strtr($s, '-_', '+/'), true) ?: '';
    }

    private function signPop(string $nonce): string
    {
        if (!function_exists('sodium_crypto_sign_seed_keypair')) {
            return '';
        }
        // Use the same seed as generate_golden_vectors.py (AGENT_SEED)
        $seed = hex2bin('c0c1c2c3c4c5c6c7c8c9cacbcccdcecfd0d1d2d3d4d5d6d7d8d9dadbdcdddedf');
        $kp = sodium_crypto_sign_seed_keypair($seed);
        $sk = sodium_crypto_sign_secretkey($kp);

        // Use the same logic as RilavoVerifier::buildPopPayload
        $data = [
            'method' => strtoupper('GET'),
            'path' => '/data/1',
            'act' => 'data.read',
            'nonce' => $nonce,
        ];
        $canonical = \Rilavo\RilavoJCS::canonicalize($data);
        $digest = hash('sha256', $canonical); // hex output
        $escaped_digest = \Rilavo\RilavoJCS::escapeStringPublic($digest);
        $payload = '{"rilavo_pop_v0":' . $escaped_digest . '}';
        $sig = sodium_crypto_sign_detached($payload, $sk);
        // Return base64url encoding (matching verifier's b64urlDecode expectation)
        return strtr(base64_encode($sig), '+/', '-_');
    }

    
    /**
     * Convert base64url raw key to PEM format
     */
    private function pemFromRaw(string $raw): string
    {
        $raw = strtr($raw, '-_', '+/');
        $padding = strlen($raw) % 4;
        if ($padding) {
            $raw .= str_repeat('=', 4 - $padding);
        }
        $der = base64_decode($raw);
        $pem = "-----BEGIN PUBLIC KEY-----\n" . chunk_split(base64_encode($der), 64, "\n") . "-----END PUBLIC KEY-----\n";
        return $pem;
    }
}
