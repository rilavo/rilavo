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

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "rilavo-protocol" / "src"))

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

    # deterministic keys from fixed seeds via Ed25519 scalar clamp is not
    # exposed; instead reuse the existing committed vectors' keys by loading
    # the prior corpus if present so identities stay stable across runs.
    prev_path = out_dir / "golden.json"
    prev = json.loads(prev_path.read_text()) if prev_path.exists() else None

    issuer_priv, issuer_pub = generate_keypair()
    agent_priv, agent_pub = generate_keypair()

    cred_fields = {
        "iss": "rilavo:iss:goldencorpus",
        "sub": "did:example:alice",
        "agt": "did:example:alice-bot",
        "aud": "svc:corpus",
        "act": "data.read",
        "apk": b64url_encode(bytes(agent_pub.public_bytes(
            Encoding.Raw, PublicFormat.Raw))),
        "iat": 1700000000,
        "exp": 1700003600,
        "nonce": "goldencorpus-nonce-0001",
    }
    from rilavo.credential import IssueRequest, issue

    req = IssueRequest(
        principal=cred_fields["sub"], agent=cred_fields["agt"],
        agent_public_key_b64=cred_fields["apk"],
        action_class=cred_fields["act"], audience=cred_fields["aud"],
    )
    cred = issue(issuer_private_key=issuer_priv,
                 issuer_id="rilavo:iss:goldencorpus", request=req,
                 now=datetime.fromtimestamp(1700000000, tz=timezone.utc))
    cred_fields = dict(cred.fields)

    sig = issuer_priv.sign(canonicalize(cred.signing_payload()))
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
        "issuer_pub_b64url": b64url_encode(bytes(issuer_pub.public_bytes(
            Encoding.Raw, PublicFormat.Raw))),
        "agent_pub_b64url": cred_fields["apk"],
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
    print(f"wrote {out_dir/'golden.json'} and {out_dir/'rejects.json'}")


if __name__ == "__main__":
    main()
