# rilavo-wp

WordPress must-use plugin: gates WooCommerce Store API + WP Admin REST
endpoints via Rilavo agent credential verification.

## Requirements

- PHP 8.x with ext-sodium (standard in PHP 7.2+)
- WordPress 6.x
- No composer dependencies (stdlib + ext-sodium only)

## Install walkthrough

1. **Download** `rilavo-mu.zip` from this directory.

2. **Extract into mu-plugins:**
   ```bash
   cd wp-content/
   unzip /path/to/rilavo-mu.zip -d mu-plugins/
   ```
   Resulting layout:
   ```
   wp-content/mu-plugins/rilavo-mu/rilavo-mu.php
   wp-content/mu-plugins/rilavo-mu/includes/class-rilavo-jcs.php
   wp-content/mu-plugins/rilavo-mu/includes/class-rilavo-verifier.php
   wp-content/mu-plugins/rilavo-mu/includes/class-rilavo-gate.php
   ```
   Must-use plugins load automatically; no activation needed.

3. **Configure:** Go to Settings > Rilavo in WP Admin.
   Set:
   - **Audience**: your site's verifier id (e.g. `verifier:mystore.example`)
   - **Issuer Public Key PEM**: the issuer's public key in PEM format
   - **Gated Routes**: one prefix per line (defaults cover WC Store + posts)

4. **Verify with a test credential:** Send a request to a gated route:
   ```bash
   curl -H "x-rilavo-credential: <credential JSON>" \
        -H "x-rilavo-pop-signature: <pop sig>" \
        -H "x-rilavo-request-nonce: <nonce>" \
        -H "x-rilavo-action: data.read" \
        https://yoursite.example/wp-json/wc/store/products
   ```

5. **Run self-check on your server:**
   ```bash
   php check.php    # 14/14 pass = JCS + PoP + Ed25519 + gate pipeline OK
   ```

## Gate order

Matches `src/rilavo/verifier.py` step-for-step:
shape → version(P-26) → delegation reject → audience → time window →
issuer lookup(fail-closed) → signature(JCS+Ed25519) → replay →
revocation(pluggable) → PoP(rilavo_pop_v0) → exact-match scope

## Honest gaps

- Runtime-tested via `check.php` only (no WordPress test env available).
- Ed25519 requires ext-sodium (standard PHP 7.2+); no pure-PHP fallback.
- Revocation uses WP transients by default; not shared across replicas
  unless an external object cache is configured. Production MUST wire a
  real revocation source per P-09.
- Issuer lookup is single-issuer (PEM from options). Multi-issuer federation
  is P-17 Horizon-2 scope, not implemented here.

## License

Apache-2.0
