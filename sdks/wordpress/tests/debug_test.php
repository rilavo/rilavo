<?php
require_once __DIR__ . '/../vendor/autoload.php';

use Rilavo\RilavoVerifier;

// Load golden vector
$goldenPath = __DIR__ . '/../../golden/golden.json';
if (!file_exists($goldenPath)) {
    $goldenPath = __DIR__ . '/../../../golden/golden.json';
}
$golden = json_decode(file_get_contents($goldenPath), true);
$v = $golden;
$fields = $v['credential_fields'];

// Create PEM from raw key
function pemFromRaw(string $raw): string
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

$pem = "-----BEGIN PUBLIC KEY-----\n" . chunk_split(pemFromRaw($v['issuer_pub_b64url']), 64, "\n") . "-----END PUBLIC KEY-----\n";

$verifier = new \Rilavo\RilavoVerifier(
    $fields['aud'],
    $pem,
    null,
    fn() => 1700000001 // Fixed time: iat + 1
);

$fields = $v['credential_fields'];

$result = $verifier->verifyFields(
    $fields,
    $v['pop_sig']['method'],
    $v['pop_sig']['path'],
    $v['pop_sig']['act'],
    $v['pop_sig']['sig_b64url'],
    $v['pop_sig']['nonce']
);

echo "Result: " . json_encode($result) . "\n";
echo "Accepted: " . ($result['accepted'] ? 'true' : 'false') . "\n";
echo "Reason: " . ($result['reason_code'] ?? 'null') . "\n";
