#!/usr/bin/env python3
"""Client-side drill against YOUR self-hosted issuer: generate an agent key,
issue via your /issue endpoint, then verify over /verify with proof-of-possession.

Usage:
    uv run python deploy/selfhosted/client_drill.py --server http://127.0.0.1:8090
"""

import argparse
import json
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from cryptography.hazmat.primitives import serialization          # noqa: E402
from rilavo.keys import generate_keypair, public_key_bytes, b64url_encode  # noqa: E402
from rilavo.pop import sign_request                               # noqa: E402


def post(url: str, payload: dict) -> dict:
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"},
                                 method="POST")
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode())


def get(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=10) as resp:
        return json.loads(resp.read().decode())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--server", default="http://127.0.0.1:8090")
    args = ap.parse_args()

    # 0. Discover the issuer's published directory entry (P-17).
    entry = get(args.server + "/directory")
    audience = entry["verifier_id"]
    print("directory:", entry["issuer_id"], "| verifier:", audience)

    # 1. Your agent generates its own keypair (agent keys are YOURS).
    priv, pub = generate_keypair()
    agent_pub_b64 = b64url_encode(public_key_bytes(pub))

    # 2. Ask your issuer for a credential.
    cred = post(args.server + "/issue", {
        "principal": "my-org:runner-01", "agent": "agt_local_01",
        "agent_public_key": agent_pub_b64,
        "action_class": "data.read", "audience": audience})
    print("issued:", cred["iss"], "->", cred["sub"], "nonce", cred["nonce"])

    # 3. Sign THIS request with the agent key (proof-of-possession, P-07).
    sig, nonce = sign_request(priv, "POST", "/resource", "data.read")
    result = post(args.server + "/verify", {
        "credential": cred,
        "request": {"method": "POST", "path": "/resource",
                    "requested_action": "data.read",
                    "signature": sig, "request_nonce": nonce}})
    print("verify:", json.dumps(result))
    return 0 if result.get("accepted") else 1


if __name__ == "__main__":
    sys.exit(main())
