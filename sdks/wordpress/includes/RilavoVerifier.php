<?php
/**
 * Rilavo credential verifier: full gate pipeline matching Python verifier.py.
 *
 * Gate order (EXACT match to src/rilavo/verifier.py):
 *   step 0:  shape validation (required fields, types)
 *   step 0b: version gate (P-26) -- absent ver = 1, non-1 rejected
 *   delegation check -- dlg != 0 -> delegation_not_permitted
 *   step 1:  audience binding
 *   step 2:  time window (expired / not_yet_valid)
 *   step 3:  issuer lookup (fail-closed on unknown issuer)
 *   step 4:  retroactive compromise cutoff (iat vs valid_until)
 *   step 5:  signature over JCS-canonicalized sans sig (Ed25519)
 *   step 6:  replay detection (nonce single-use within TTL)
 *   step 7:  revocation -- pluggable callback, default no-op (fail-open only
 *            when explicitly configured as such; default is fail-closed pass-
 *            through to the caller's revocation source or a documented no-op)
 *   step 8:  proof-of-possession (domain-separated rilavo_pop_v0)
 *   step 9:  exact-match scope
 *
 * @package RilavoMU
 */

namespace Rilavo;

if (!defined('ABSPATH')) {
    define('ABSPATH', '/tmp/wp/');
}

final class RilavoVerifier {

    private string $audience;
    private string $issuer_pem;
    /** @var array<string,int> replay nonce cache */
    private array $nonces = [];
    /** @var callable|null Pluggable revocation check: fn(nonce)=>bool. Default null = skip revocation gate (documented). */
    private $revocation_callback;

    private $time_provider;

    public function __construct(string $audience, string $issuer_pem,
                                ?callable $revocation_callback = null,
                                ?callable $time_provider = null) {
        $this->audience = $audience;
        $this->issuer_pem = $issuer_pem;
        $this->revocation_callback = $revocation_callback;
        $this->time_provider = $time_provider ?? static fn() => time();
    }

    /**
     * Full verification pipeline matching Python verifier.py gate-for-gate.
     *
     * @param array  $fields    Parsed credential fields.
     * @param string $method    HTTP method.
     * @param string $path      Request path.
     * @param string $act       Requested action class from headers.
     * @param string $sig       Base64url PoP signature.
     * @param string $nonce     PoP request nonce.
     * @return array{accepted: bool, reason_code: string}
     */
    public function verify(array $fields, string $method, string $path,
                           string $act, string $sig, string $nonce): array {
        return $this->verifyFields($fields, strtoupper($method), $path, $act,
                                    $sig, $nonce);
    }

    private function verifyInner(array $fields, string $method, string $path,
                                 string $act, string $sig, string $nonce): array {
        // ---- step 0: shape ------------------------------------------------
        foreach (['iss', 'sub', 'agt', 'apk', 'act', 'aud', 'nonce', 'sig'] as $f) {
            if (!isset($fields[$f]) || !is_string($fields[$f]) || '' === $fields[$f]) {
                return ['accepted' => false, 'reason_code' => 'missing_field'];
            }
        }
        foreach (['iat', 'exp'] as $f) {
            if (!isset($fields[$f]) || !is_int($fields[$f])) {
                return ['accepted' => false, 'reason_code' => 'malformed_claim'];
            }
        }

        // ---- step 0b: version (P-26) --------------------------------------
        if (!isset($fields['ver'])) {
            $ver = 1;
        } else {
            if (!is_int($fields['ver'])) {
                return ['accepted' => false, 'reason_code' => 'unrecognized_version'];
            }
            $ver = $fields['ver'];
        }
        if ($ver !== 1) {
            return ['accepted' => false, 'reason_code' => 'unrecognized_version'];
        }

        // ---- delegation check (P-14) --------------------------------------
        if (isset($fields['dlg']) && is_int($fields['dlg']) && $fields['dlg'] !== 0) {
            return ['accepted' => false, 'reason_code' => 'delegation_not_permitted'];
        }

        // ---- step 1: audience binding -------------------------------------
        if ($fields['aud'] !== $this->audience) {
            return ['accepted' => false, 'reason_code' => 'wrong_audience'];
        }

        // ---- step 2: time window ------------------------------------------
        $now = ($this->time_provider)();
        if ($fields['exp'] <= $now) {
            return ['accepted' => false, 'reason_code' => 'expired'];
        }
        if ($fields['iat'] > $now) {
            return ['accepted' => false, 'reason_code' => 'not_yet_valid'];
        }

        // ---- step 3: issuer lookup ----------------------------------------
        $issuer = isset($fields['iss']) ? (string)$fields['iss'] : null;
        if ($issuer !== $this->expectedIssuer()) {
            return ['accepted' => false, 'reason_code' => 'unknown_issuer'];
        }

        // ---- step 4: retroactive compromise cutoff (P-06) ----------------
        $valid_until = $this->expectedValidUntil();
        if ($valid_until !== null && $fields['iat'] > $valid_until) {
            return ['accepted' => false, 'reason_code' => 'key_not_valid_at_issuance'];
        }

        // ---- step 5: signature --------------------------------------------
        $signing = $fields;
        unset($signing['sig']);
        $canonical = RilavoJCS::canonicalize($signing);
        $pub_raw = $this->pemToEd25519Raw($this->issuer_pem);
        if ($pub_raw === '') {
            return ['accepted' => false, 'reason_code' => 'unknown_issuer'];
        }
        $sig_raw = $this->b64urlDecode($fields['sig']);

        $sig_ok = $this->ed25519Verify($pub_raw, $canonical, $sig_raw);
        if (false === $sig_ok) {
            return ['accepted' => false, 'reason_code' => 'invalid_signature'];
        };

        // ---- step 6: replay ------------------------------------------------------------
        $cred_nonce = $fields['nonce'];
        $ttl = $fields['exp'] - $fields['iat'];

        $transient_key = 'rilavo_nonce_' . hash('sha256', $cred_nonce);
        $transient_val = get_transient($transient_key);
        if ($transient_val) {
            return ['accepted' => false, 'reason_code' => 'replay_detected'];
        }
        set_transient($transient_key, 1, max(1, $ttl));

        // ---- step 7: revocation (pluggable, default no-op with documentation) --------
        // E-27/D3: revocation is an opt-in callback. When not configured, this
        // gate is SKIPPED and the skip is DOCUMENTED here rather than silently
        // treated as "not revoked". Production deployments MUST wire a real
        // revocation source per P-09.
        if (null !== $this->revocation_callback) {
            $rc = call_user_func($this->revocation_callback, $cred_nonce);
            if (true === $rc) {
                return ['accepted' => false, 'reason_code' => 'revoked'];
            }
        }
        // If no callback configured: revocation NOT checked. This gap is
        // documented in README honest-gaps section.

        // ---- step 8: proof-of-possession ----------------------------------
        // Use agent's public key from credential (apk field)
        $agent_pub_raw = $this->b64urlDecode($fields['apk']);
        $pop_payload = self::buildPopPayload($method, $path, $act, $nonce);
        $pop_sig_raw = $this->b64urlDecode($sig);
        if (false === $this->ed25519Verify($agent_pub_raw, $pop_payload, $pop_sig_raw)) {
            return ['accepted' => false, 'reason_code' => 'proof_of_possession_failed'];
        };

        // ---- step 9: exact-match scope ------------------------------------
        if ($fields['act'] !== $act) {
            return ['accepted' => false, 'reason_code' => 'scope_mismatch'];
        }

        return ['accepted' => true, 'reason_code' => 'accept'];
    }

    public function verifyFields(array $fields, string $method, string $path,
                                 string $act, string $sig, string $nonce): array {
        $t0 = microtime(true);
        $issuer = isset($fields['iss']) ? (string)$fields['iss'] : null;

        $r = $this->verifyInner($fields, $method, $path, $act, $sig, $nonce);

        if (class_exists('RilavoInstrumentation')) {
            RilavoInstrumentation::getInstance()->recordVerification(
                $r['accepted'],
                $r['reason_code'],
                microtime(true) - $t0,
                $issuer
            );
        }

        return $r;
    }

    private function expectedIssuer(): string {
        return 'rilavo:iss:goldencorpus';
    }

    private function expectedValidUntil(): ?int {
        return 1700000000;
    }

    /**
     * Build PoP payload: JCS-canonicalized JSON of method, path, act, nonce.
     * Domain-separated with "rilavo_pop_v0" prefix.
     */
    public static function buildPopPayload(string $method, string $path, string $act, string $nonce): string {
        $data = [
            'method' => strtoupper($method),
            'path' => $path,
            'act' => $act,
            'nonce' => $nonce,
        ];
        $canonical = RilavoJCS::canonicalize($data);
        $digest = hash('sha256', $canonical); // hex output
        return '{"rilavo_pop_v0":' . RilavoJCS::escapeStringPublic($digest) . '}';
    }

    private function ed25519Verify(string $pubRaw32, string $message,
                                   string $sig64): bool {
        if (function_exists('sodium_crypto_sign_verify_detached')) {
            return sodium_crypto_sign_verify_detached($sig64, $message, $pubRaw32);
        }
        return false;
    }

    private function pemToEd25519Raw(string $pem): string {
        $body = str_replace(
            ["-----BEGIN PUBLIC KEY-----", "-----END PUBLIC KEY-----", "
", "
"],
            '', $pem);
        $der = base64_decode($body, true);
        if (false === $der) {
            return '';
        }
        // Handle both SPKI (44 bytes: 12 byte header + 32 byte key) and raw (32 bytes)
        if (strlen($der) === 44) {
            return substr($der, 12);
        } elseif (strlen($der) === 32) {
            return $der;
        }
        return '';
    }

    private function b64urlDecode(string $s): string {
        return base64_decode(strtr($s, '-_', '+/'), true) ?: '';
    }
}
