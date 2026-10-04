"""End-to-end smoke test: issue, verify, and reject in-process."""
from __future__ import annotations


def run_smoke(verbose: bool = True) -> tuple[bool, list[str]]:
    steps: list[str] = []
    ok = True

    def _check(cond: bool) -> None:
        nonlocal ok
        if not cond:
            ok = False

    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import (
            Ed25519PrivateKey,
        )

        from .api import Issuer, do_issue, do_verify
        from .credential import Credential
        from .keys import KeyDirectory
        from .pop import Request, sign_request
        from .revocation import RevocationLog
        from .verifier import NonceCache

        issuer_priv = Ed25519PrivateKey.generate()
        agent_priv = Ed25519PrivateKey.generate()
        agent_pub = agent_priv.public_key()

        issuer = Issuer(private_key=issuer_priv)
        dir_ = KeyDirectory()
        issuer.register_into(dir_)
        revocations = RevocationLog()
        nonce_cache = NonceCache()

        V = "verifier:smoke.example"

        cred = do_issue(
            issuer=issuer,
            principal="smoke-test-principal",
            agent="smoke-test-agent",
            agent_public_key=agent_pub,
            action_class="data.read",
            audience=V,
        )
        fields = dict(cred.fields)
        if verbose:
            steps.append("issue: OK (nonce=" + fields["nonce"][:8] + ")")

        sig, req_nonce = __import__("rilavo.pop", fromlist=["sign_request"]).sign_request(
            agent_priv, "GET", "/data", "data.read"
        )
        pop_req = Request(
                    method="GET", path="/data",
                    requested_action="data.read",
                    signature=sig, request_nonce=req_nonce,
                )
        result = do_verify(
            verifier_id=V,
            credential=Credential(fields=dict(fields)),
            request=pop_req,
            key_directory=dir_,
            revocation_log=revocations,
            nonces=nonce_cache,
        )
        _check(result.accepted)
        if verbose:
            steps.append("verify accept: OK")

        # Negative: scope mismatch must reject
        bad_sig, bad_nonce = sign_request(agent_priv, "POST", "/admin", "admin.write")
        bad_req = Request(method="POST", path="/admin",
                                  requested_action="admin.write",
                                  signature=bad_sig, request_nonce=bad_nonce)
        r_bad = do_verify(
            verifier_id=V,
            credential=Credential(fields=dict(fields)),
            request=bad_req,
            key_directory=dir_,
            revocation_log=RevocationLog(),
            nonces=nonce_cache,
        )
        if r_bad.accepted:
            ok = False
        if verbose:
            steps.append("scope mismatch rejected: " + str(not r_bad.accepted))

        # Wrong audience must reject
        wrong_fields = dict(fields)
        wrong_fields["aud"] = "verifier:someone-else.example"
        r_aud = do_verify(
            verifier_id="verifier:someone-else.example",
            credential=Credential(fields=wrong_fields),
            request=pop_req,
            key_directory=dir_,
            revocation_log=RevocationLog(),
            nonces=nonce_cache,
        )
        if r_aud.accepted:
            ok = False
        if verbose:
            steps.append("wrong audience rejected: " + str(not r_aud.accepted))

    except Exception as e:
        ok = False
        steps.append(f"ERROR: {e}")

    return ok, steps


def cmd_smoke(verbose: bool = True) -> int:
    """CLI entry point. Returns exit code (0=pass, 1=fail)."""
    ok, steps = run_smoke(verbose)
    if verbose:
        for s in steps:
            print(s)
        print("\n" + ("✅ SMOKE TEST PASSED" if ok else "❌ SMOKE TEST FAILED"))
    return 0 if ok else 1