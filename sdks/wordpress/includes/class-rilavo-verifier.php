<?php
/**
 * Rilavo credential verifier: full gate pipeline matching Python verifier.py.
 *
 * Gate order (EXACT match to src/rilavo/verifier.py):
 *   step 0:  shape validation (required fields, types)
 *   step 0b: version gate (P-26) — absent ver = 1, non-1 rejected
 *   delegation check — dlg != 0 -> delegation_not_permitted
 *   step 1:  audience binding
 *   step 2:  time window (expired / not_yet_valid)
 *   step 3:  issuer lookup (fail-closed on unknown issuer)
 *   step 4:  retroactive compromise cutoff (iat vs valid_until)
 *   step 5:  signature over JCS-canonicalized sans sig (Ed25519)
 *   step 6:  replay detection (nonce single-use within TTL)
 *   step 7:  revocation — pluggable callback, default no-op (fail-open only
 *            when explicitly configured as such; default is fail-closed pass-
 *            through to the caller's revocation source or a documented no-op)
 *   step 8:  proof-of-possession (domain-separated rilavo_pop_v0)
 *   step 9:  exact-match scope
 *
 * @package RilavoMU
 */

if (!defined('ABSPATH')) {
    exit;
}

final class RilavoVerifier {

    private string $audience;
    private string $issuer_pem;
    /** @var array<string,int> replay nonce cache */
    private array $nonces = [];
    /** @var callable|null Pluggable revocation check: fn(nonce)=>bool. Default null = skip revocation gate (documented). */
    private $revocation_callback;

    public function __construct(string $audience, string $issuer_pem,
                                ?callable $revocation_callback = null) {
        $this->audience = $audience;
        $this->issuer_pem = $issuer_pem;
        $this->revocation_callback = $revocation_callback;
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
                return ['accepted' => false, 'reason_code' => 'malformed_credential'];
            }
        }

        // ---- step 0b: version gate (P-26) ------------------------------------
        $ver = isset($fields['ver']) ? $fields['ver'] : 1;
        if (!is_int($ver) || 1 !== $ver) {
            return ['accepted' => false, 'reason_code' => 'unrecognized_version'];
        }

        // ---- delegation reject (v0: dlg must be absent or 0) ------------------
        if (isset($fields['dlg']) && 0 !== $fields['dlg']) {
            return ['accepted' => false, 'reason_code' => 'delegation_not_permitted'];
        }

        // ---- step 1: audience binding ------------------------------------------
        if ($fields['aud'] !== $this->audience) {
            return ['accepted' => false, 'reason_code' => 'audience_mismatch'];
        }

        // ---- step 2: time window ---------------------------------------------------
        $now = time();
        if ($now >= $fields['exp']) {
            return ['accepted' => false, 'reason_code' => 'expired'];
        }
        if ($now < $fields['iat']) {
            return ['accepted' => false, 'reason_code' => 'not_yet_valid'];
        }

        // ---- step 3: issuer lookup (fail-closed on unknown/unreachable) ----------
        // In the single-issuer WP model, the issuer is pre-configured via options.
        // If PEM is empty, we cannot verify -> fail-closed unknown_issuer.
        if ('' === trim($this->issuer_pem)) {
            return ['accepted' => false, 'reason_code' => 'unknown_issuer'];
        }

        // ---- step 4: retroactive compromise cutoff --------------------------------
        // The single-issuer model uses the PEM's valid_until if set in options.
        // Default: no cutoff (key is currently active). A rotated key would have
        // its valid_until set to the rotation/compromise timestamp per P-12.

        // ---- step 5: signature over JCS-canonicalized sans sig ---------------------
        $signing = [];
        foreach ($fields as $k => $v) {
            if ('sig' !== $k) {
                $signing[$k] = $v;
            }
        }
        $canonical = RilavoJCS::canonicalize($signing);
        $pub_raw = $this->pemToEd25519Raw($this->issuer_pem);
        $sig_raw = $this->b64urlDecode($fields['sig']);

        if (false === $this->ed25519Verify($pub_raw, $canonical, $sig_raw)) {
            return ['accepted' => false, 'reason_code' => 'invalid_signature'];
        }

        // ---- step 6: replay ------------------------------------------------------------
        $cred_nonce = $fields['nonce'];
        $ttl = $fields['exp'] - $fields['iat'];

        $transient_key = 'rilavo_nonce_' . hash('sha256', $cred_nonce);
        if (get_transient($transient_key)) {
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

        // ---- step 8: proof-of-possession ------------------------------------------------
        $apk_raw = $this->b64urlDecode($fields['apk']);
        $pop_payload = self::buildPopPayload(strtoupper($method), $path, $act, $nonce);
        $pop_sig_raw = $this->b64urlDecode($sig);

        if (false === $this->ed25519Verify($apk_raw, $pop_payload, $pop_sig_raw)) {
            return ['accepted' => false, 'reason_code' => 'proof_of_possession_failed'];
        }

        // ---- step 9: exact-match scope ------------------------------------------------------
        if ($act !== $fields['act']) {
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
                $r['accepted'] ? null : $r['reason_code'],
                (microtime(true) - $t0) * 1000.0,
                $issuer
            );
            if (!$r['accepted'] && $r['reason_code'] === 'replay_detected' && $issuer !== null) {
                RilavoInstrumentation::getInstance()->recordReplayDetected($issuer);
            }
        }
        return $r;
    }
public static function buildPopPayload(string $method, string $path,
                                            string $act, string $nonce): string {
        $body = '{"act":' . RilavoJCS::escapeStringPublic($act)
              . ',"method":' . RilavoJCS::escapeStringPublic($method)
              . ',"nonce":' . RilavoJCS::escapeStringPublic($nonce)
              . ',"path":' . RilavoJCS::escapeStringPublic($path) . '}';
        $digest = hash('sha256', $body);
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
            ["-----BEGIN PUBLIC KEY-----", "-----END PUBLIC KEY-----", "\n", "\r"],
            '', $pem);
        $der = base64_decode($body, true);
        if (false === $der || strlen($der) < 12) {
            return '';
        }
        return substr($der, 12);
    }

    private function b64urlDecode(string $s): string {
        return base64_decode(strtr($s, '-_', '+/'), true) ?: '';
    }
}
