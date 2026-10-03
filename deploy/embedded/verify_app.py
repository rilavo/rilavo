#!/usr/bin/env python3
"""Embedded, verification-only deployment example (P-31 path 1).

A system that only ever CHECKS credentials needs no issuer infrastructure at
all: the SDK plus the relevant issuer's public key. This demo runs fully
offline -- it uses the SDK's published fixed test issuer as a stand-in for
"an issuer whose public key you fetched from its key directory" and a
credential "received" in an inbound request.

Run:  uv run python deploy/embedded/verify_app.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from rilavo.api import do_verify                      # noqa: E402
from rilavo.keys import KeyDirectory                  # noqa: E402
from rilavo.pop import Request                        # noqa: E402
from rilavo.revocation import RevocationLog           # noqa: E402
from rilavo.testing import offline_test_kit, local_test_agent  # noqa: E402
from rilavo.verifier import NonceCache                # noqa: E402


def main() -> int:
    # --- what a real verifier has BEFORE any traffic arrives ---------------
    # 1. The issuer's public key, fetched once from its key directory (P-17)
    #    and cached locally. Offline demo: the fixed test kit issuer.
    kit = offline_test_kit()
    directory: KeyDirectory = kit.key_directory

    # 2. A revocation-log cache, refreshed on your own interval (P-09).
    revocations: RevocationLog = kit.revocation_log

    # 3. Your replay cache -- held across requests, one per process.
    nonces = NonceCache()

    print("verifier ready:",
          "issuer", kit.issuer.issuer_id, "| audience", kit.verifier_id)

    # --- an inbound request carries a credential + signed request ----------
    agent_priv, agent_pub = local_test_agent()
    from rilavo.api import do_issue
    inbound_credential = do_issue(
        kit.issuer, principal="acme-corp:runner-04", agent="agt_embedded_demo",
        agent_public_key=agent_pub, action_class="data.read",
        audience=kit.verifier_id)
    sig, nonce = __import__("rilavo.pop", fromlist=["sign_request"]).sign_request(
        agent_priv, "POST", "/resource", "data.read")
    inbound_request = Request("POST", "/resource", "data.read", sig, nonce)

    # --- verify: no network call, no issuer infrastructure -----------------
    result = do_verify(kit.verifier_id, inbound_credential, inbound_request,
                       directory, revocations, nonces=nonces)

    print("verification result:", json.dumps(result.__dict__))
    return 0 if result.accepted else 1


if __name__ == "__main__":
    sys.exit(main())
