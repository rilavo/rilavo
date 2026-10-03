---
title: WordPress Plugin API Reference
description: Complete API reference for the Rilavo WordPress Plugin
---

# WordPress Plugin API Reference (rilavo/rilavo-wp)

> **Quick test:** [Interactive Playground](../../playground/index.md) — try credential issuance and verification in your browser.


Complete API reference for the Rilavo WordPress Plugin. A must-use plugin for credential verification in WordPress.

## Installation

```bash
composer require rilavo/rilavo-wp
```

Or add to your `composer.json`:

```json
{
  "require": {
    "rilavo/rilavo-wp": "^0.1.0"
  }
}
```

The plugin is a **must-use plugin** (mu-plugin) - it auto-loads and requires no activation.

## Core Classes

### `Rilavo\Verifier`

Main verification class. Implements the full Rilavo verification gate pipeline matching Python verifier.py.

```php
use Rilavo\Verifier;

$verifier = new Verifier([
    'audience' => 'mysite.example.com',
    'issuer_directory' => $directory,
    'revocation_log' => $revocationLog,
    'nonce_cache' => $nonceCache,  // optional, defaults to TransientNonceCache
]);
```

#### Constructor

```php
public function __construct(
    string $audience,
    string $issuer_pem,
    ?callable $revocation_callback = null,
    ?NonceCacheInterface $nonce_cache = null
)
```

**Parameters:**
- `$audience`: The audience this site expects on credentials (e.g., `mysite.example.com`)
- `$issuer_pem`: The issuer's public key in PEM format
- `$revocation_callback`: Optional callable `fn(string $nonce): bool` for revocation checking
- `$nonce_cache`: Optional `NonceCacheInterface` (defaults to `TransientNonceCache`)

#### `verify()`

Full verification pipeline matching Python verifier.py gate-for-gate.

```php
public function verify(array $fields, string $method, string $path,
                       string $act, string $sig, string $nonce): array
```

**Parameters:**
- `$fields`: Parsed credential fields array
- `$method`: HTTP method (GET, POST, etc.)
- `$path`: Request path
- `$act`: Requested action class
- `$sig`: Base64url PoP signature
- `$nonce`: PoP request nonce

**Returns:** `array{accepted: bool, reason_code: string}`

#### `verifyFields()`

Lower-level verification for pre-parsed fields.

```php
public function verifyFields(array $fields, string $method, string $path,
                             string $act, string $sig, string $nonce): array
```

---

### `Rilavo\Credential`

Represents a parsed credential.

```php
use Rilavo\Credential;

$credential = new Rilavo\Credential($base64urlEncodedCredential);
```

#### Methods

```php
class Credential {
    public function __construct(string $base64urlEncodedCredential);
    public function getFields(): array;
    public function getNonce(): string;
    public function getAudience(): string;
    public function getActionClass(): string;
    public function getTtlSeconds(): int;
}
```

---

### `Rilavo\PopRequest`

Proof-of-possession request.

```php
use Rilavo\PopRequest;

$pop = new Rilavo\PopRequest([
    'method' => 'POST',
    'path' => '/api/data',
    'act' => 'data.read',
    'signature' => $signature,
    'request_nonce' => $nonce,
]);
```

---

### `Rilavo\Result`

Verification result object.

```php
class Rilavo_Result {
    public bool $accepted;
    public ?string $reasonCode;

    public function isAccepted(): bool;
    public function getReasonCode(): ?string;
}
```

---

### `Rilavo\NonceCacheInterface`

Interface for pluggable nonce cache implementations.

```php
interface NonceCacheInterface {
    public function seenBefore(string $nonce, int $windowSeconds, ?int $now = null): bool;
}
```

### `Rilavo\TransientNonceCache`

Default implementation using WordPress transients.

```php
class TransientNonceCache implements NonceCacheInterface {
    public function seenBefore(string $nonce, int $windowSeconds, ?int $now = null): bool;
}
```

Works with any WordPress object cache backend (Memcached, Redis via object cache plugin, APCu, database).

### `Rilavo\RedisNonceCache`

Redis-backed nonce cache for distributed deployments.

```php
class RedisNonceCache implements NonceCacheInterface {
    public function __construct(string $url = "redis://localhost:6379", string $keyPrefix = "rilavo:nonce:");
    public function connect(): bool;
    public function seenBefore(string $nonce, int $windowSeconds, ?int $now = null): bool;
}
```

**Requires:** `predis/predis` composer package.

---

### `Rilavo\RilavoJCS`

JCS canonicalization utility.

```php
class RilavoJCS {
    public static function canonicalize(array $fields): string;
    public static function escapeStringPublic(string $value): string;
}
```

---

### `Rilavo\RilavoGate`

WordPress REST API gate middleware.

```php
use Rilavo\RilavoGate;

$gate = new RilavoGate('verifier:example.com', $issuer_pem);
```

Hooks into `rest_pre_dispatch` filter to verify credentials on protected routes.

---

## Reason Codes

All reason codes match the protocol specification:

```php
const REASON_MISSING_FIELD = 'missing_field';
const REASON_MALFORMED_CREDENTIAL = 'malformed_credential';
const REASON_UNRECOGNIZED_VERSION = 'unrecognized_version';
const REASON_AUDIENCE_MISMATCH = 'audience_mismatch';
const REASON_EXPIRED = 'expired';
const REASON_NOT_YET_VALID = 'not_yet_valid';
const REASON_UNKNOWN_ISSUER = 'unknown_issuer';
const REASON_KEY_NOT_VALID_AT_ISSUANCE = 'key_not_valid_at_issuance';
const REASON_INVALID_SIGNATURE = 'invalid_signature';
const REASON_REPLAY_DETECTED = 'replay_detected';
const REASON_REVOKED = 'revoked';
const REASON_PROOF_OF_POSSESSION_FAILED = 'proof_of_possession_failed';
const REASON_SCOPE_MISMATCH = 'scope_mismatch';
const REASON_DELEGATION_NOT_PERMITTED = 'delegation_not_permitted';
```

---

## Usage Example

```php
// In your mu-plugin or theme functions.php
add_action('init', function() {
    $verifier = new Rilavo\Verifier([
        'audience' => 'mysite.example.com',
        'issuer_directory' => new MyKeyDirectory(),
        'revocation_log' => new MyRevocationLog(),
        'nonce_cache' => new Rilavo\RedisNonceCache('redis://localhost:6379'),
    ]);

    $credentialHeader = $_SERVER['HTTP_X_RILAVO_CREDENTIAL'] ?? '';
    $popHeaders = [
        'method' => $_SERVER['REQUEST_METHOD'],
        'path' => $_SERVER['REQUEST_URI'],
        'act' => 'data.read',
        'signature' => $_SERVER['HTTP_X_RILAVO_POP_SIGNATURE'] ?? '',
        'request_nonce' => $_SERVER['HTTP_X_RILAVO_REQUEST_NONCE'] ?? '',
    ];

    $credential = new Rilavo\Credential($credentialHeader);
    $popRequest = new Rilavo\PopRequest($popHeaders);

    $result = $verifier->verify($credential, $popRequest);

    if (!$result->isAccepted()) {
        wp_die('Unauthorized: ' . $result->getReasonCode(), 401);
    }

    // Credential verified, $credential->getFields() contains the parsed credential
});
```

## Nonce Cache Configuration

### Default: WordPress Transients

```php
// No configuration needed - uses WP transients
$verifier = new Rilavo\Verifier([...]);
```

Works with any WordPress object cache backend (Redis, Memcached, APCu) via WordPress object cache.

### Redis: Distributed Deployments

```php
// Requires: composer require predis/predis
$verifier = new Rilavo\Verifier([
    'audience' => 'mysite.example.com',
    'issuer_directory' => $directory,
    'revocation_log' => $revocationLog,
    'nonce_cache' => new Rilavo\RedisNonceCache('redis://localhost:6379'),
]);
```

Gracefully falls back to transients if Redis is unavailable.

## Security Notes

- All cryptographic operations use libsodium (ext-sodium required)
- JCS canonicalization per RFC 8785 (string+integer subset)
- Proof-of-possession uses domain-separated `rilavo_pop_v0`
- Nonce cache uses SHA-256 hashed keys (P-10 discipline)
- Fail-closed on all verification gates
- Must-use plugin ensures it loads before any other plugins
