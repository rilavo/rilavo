#!/usr/bin/env python3
"""P5-B: regenerate the cross-language golden-vector corpus from the Python
reference implementation. Writes golden/golden.json (wire-format vectors:
JCS canonicalization, PoP payload/signature, full issued credential) and
golden/rejects.json (deterministic reject cases with expected reason codes).

The corpus is the single source of truth for Python, TypeScript and Go suites;
packages/rilavo-go/testdata/golden.json must stay byte-identical to
golden/golden.json (drift-guard test enforces this).
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from cryptography.hazmat.primitives.serialization import (  # noqa: E402
    Encoding, PublicFormat, load_pem_private_key,
)
from rilavo.canonical import canonicalize  # noqa: E402
from rilavo.credential import Credential  # noqa: E402
from rilavo.keys import (IssuerKeyEntry, KeyDirectory, b64url_encode,  # noqa: E402
                         fingerprint, generate_keypair)
from rilavo.pop import Request, request_payload  # noqa: E402


def main() -> None:
    out_dir = REPO_ROOT / "golden"
    out_dir.mkdir(exist_ok=True)

    # Deterministic keys from fixed seeds (32 bytes each)
    ISSUER_SEED = bytes.fromhex("a0a1a2a3a4a5a6a7a8a9aaabacadaeafb0b1b2b3b4b5b6b7b8b9babbbcbdbebf")
    AGENT_SEED = bytes.fromhex("c0c1c2c3c4c5c6c7c8c9cacbcccdcecfd0d1d2d3d4d5d6d7d8d9dadbdcdddedf")
    
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    issuer_priv = Ed25519PrivateKey.from_private_bytes(ISSUER_SEED)
    issuer_pub = issuer_priv.public_key()
    agent_priv = Ed25519PrivateKey.from_private_bytes(AGENT_SEED)
    agent_pub = agent_priv.public_key()

    # Fixed credential fields (deterministic)
    agent_pub_b64 = b64url_encode(bytes(agent_pub.public_bytes(
        Encoding.Raw, PublicFormat.Raw)))
    issuer_pub_b64 = b64url_encode(bytes(issuer_pub.public_bytes(
        Encoding.Raw, PublicFormat.Raw)))
    
    cred_fields = {
        "iss": "rilavo:iss:goldencorpus",
        "sub": "did:example:alice",
        "agt": "did:example:alice-bot",
        "aud": "svc:corpus",
        "act": "data.read",
        "apk": agent_pub_b64,
        "iat": 1700000000,
        "exp": 1700003600,
        "nonce": "goldencorpus-nonce-fixed",  # Fixed nonce
    }

    # Manually construct credential signing payload and compute signature
    signing_payload = {
        "iss": cred_fields["iss"],
        "sub": cred_fields["sub"],
        "agt": cred_fields["agt"],
        "apk": cred_fields["apk"],
        "act": cred_fields["act"],
        "aud": cred_fields["aud"],
        "iat": cred_fields["iat"],
        "exp": cred_fields["exp"],
        "nonce": cred_fields["nonce"],
    }
    from rilavo.canonical import canonicalize
    payload_bytes = canonicalize(signing_payload)
    sig = issuer_priv.sign(payload_bytes)

    # PoP request shape must match the consumers' fixed request in tests
    # (rilavo-go TestFullAcceptPath uses GET /data/1 with act data.read).
    POP_METHOD, POP_PATH, POP_ACT, POP_NONCE = "GET", "/data/1", "data.read", "corpus-nonce"
    pop_sig = agent_priv.sign(request_payload(POP_METHOD, POP_PATH, POP_ACT, POP_NONCE))

    golden = {
        "jcs": [
            {"input": {"b": "2", "a": "1"}, "expected": '{"a":"1","b":"2"}'},
            {"input": {"k": "line\nbreak"}, "expected": '{"k":"line\\nbreak"}'},
        ],
        "pop": {"method": POP_METHOD, "path": POP_PATH, "act": POP_ACT,
                "nonce": POP_NONCE,
                "payload_hex": request_payload(POP_METHOD, POP_PATH, POP_ACT, POP_NONCE).hex()},
        "issuer_pub_b64url": issuer_pub_b64,
        "agent_pub_b64url": agent_pub_b64,
        "pop_sig": {"sig_b64url": b64url_encode(pop_sig), "nonce": "corpus-nonce"},
        "credential_fields": cred_fields,
        "credential_sig_b64url": b64url_encode(sig),
    }
    (out_dir / "golden.json").write_text(json.dumps(golden, indent=2) + "\n")

    rejects = {
        "unknown_version": {
            "credential_fields": {**cred_fields, "ver": 9},
            "expected_reason": "unrecognized_version",
        },
        "wrong_audience": {
            "credential_fields": {**cred_fields, "aud": "svc:other"},
            "expected_reason": "audience_mismatch",
        },
        "expired": {
            "credential_fields": {**cred_fields, "exp": 1000000000},
            "expected_reason": "expired",
        },
    }
    (out_dir / "rejects.json").write_text(json.dumps(rejects, indent=2) + "\n")
    print(f"wrote {out_dir/\'golden.json\'} and {out_dir/\'rejects.json\'}")

if __name__ == "__main__":
    main()
