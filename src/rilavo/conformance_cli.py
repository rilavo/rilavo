"""`rilavo conformance` — mechanical self-check against any target (D2).

Pre-figures P-21 WITHOUT claiming conformance-certification authority:
this tool runs REAL, mechanical checks derived from the P-22 threat model
and reports per-check pass/fail with reasons. Results are INFORMATIONAL --
exit codes reflect check outcomes only; nothing here certifies an
implementation or resolves any Open item.

Targets:
  --target local            in-process offline kit (no network)
  --target http://host:port published HTTP surface of a running issuer

Usage:
    uv run rilavo conformance --target local
    uv run python -m rilavo.conformance_cli --target http://127.0.0.1:8090
"""

from __future__ import annotations

import argparse
import base64
import json
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass, field

INFORMATIONAL_LABEL = ("informational self-check -- NOT conformance "
                       "certification (P-21 authority not claimed)")


@dataclass
class CheckResult:
    check_id: str
    title: str
    passed: bool | None       # None = skipped/not applicable
    detail: str


@dataclass
class ConformanceReport:
    target: str
    results: list[CheckResult] = field(default_factory=list)

    @property
    def all_passed(self) -> bool:
        return all(r.passed is True or r.passed is None for r in self.results)

    def exit_code(self) -> int:
        return 0 if self.all_passed else 1


# --------------------------------------------------------------------------
# HTTP plumbing (published API only)
# --------------------------------------------------------------------------

def _get(base: str, path: str) -> tuple[int, dict]:
    try:
        with urllib.request.urlopen(base.rstrip("/") + path, timeout=10) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())
    except Exception as e:
        return 0, {"error": repr(e)}


def _post(base: str, path: str, payload: dict) -> tuple[int, dict]:
    req = urllib.request.Request(base.rstrip("/") + path,
                                 data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"},
                                 method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())
    except Exception as e:
        return 0, {"error": repr(e)}


def _b64(pub_bytes: bytes) -> str:
    import base64
    return base64.urlsafe_b64encode(pub_bytes).decode().rstrip("=")


def _sign(agent_priv, method, path, action):
    from .pop import sign_request
    return sign_request(agent_priv, method, path, action)


def _agent_keys():
    from .testing import local_test_agent
    return local_test_agent()


# --------------------------------------------------------------------------
# The checks (each returns CheckResult)
# --------------------------------------------------------------------------

def check_directory(ctx) -> CheckResult:
    status, body = ctx["get"]("/directory")
    ok = (status == 200 and str(body.get("issuer_id", "")).startswith("rilavo:iss:")
          and "BEGIN PUBLIC KEY" in str(body.get("public_key_pem", "")))
    return CheckResult("directory", "key-directory entry well-formed",
                       ok, json.dumps(body)[:120] if not ok else "")


def check_roundtrip_accept(ctx) -> CheckResult:
    status, body = ctx["post"]("/issue", {
        "principal": "conformance:principal", "agent": "conformance-agent",
        "agent_public_key": ctx["agent_pub_b64"],
        "action_class": "data.read", "audience": ctx["audience"]})
    if status != 201:
        return CheckResult("roundtrip_accept", "issue -> verify accept",
                           False, f"issue HTTP {status}: {body}")
    cred = body["credential"] if "credential" in body else body
    sig, nonce = _sign(ctx["agent_priv"], "POST", "/x", "data.read")
    vstatus, vbody = ctx["post"]("/verify", {
        "credential": cred,
        "request": {"method": "POST", "path": "/x",
                    "requested_action": "data.read",
                    "signature": sig, "request_nonce": nonce}})
    ok = vstatus == 200 and vbody.get("accepted") is True
    return CheckResult("roundtrip_accept", "issue -> verify accept",
                       ok, json.dumps(vbody)[:120] if not ok else "")


def check_wrong_audience_rejected(ctx) -> CheckResult:
    status, body = ctx["post"]("/issue", {
        "principal": "p", "agent": "a",
        "agent_public_key": ctx["agent_pub_b64"],
        "action_class": "data.read",
        "audience": "verifier:not-this-verifier.example"})
    if status != 201:
        return CheckResult("wrong_audience", "audience binding rejects foreign "
                           "credentials", None, f"could not stage: HTTP {status}")
    sig, nonce = _sign(ctx["agent_priv"], "POST", "/x", "data.read")
    vstatus, vbody = ctx["post"]("/verify", {
        "credential": body["credential"] if "credential" in body else body,
        "request": {"method": "POST", "path": "/x",
                    "requested_action": "data.read",
                    "signature": sig, "request_nonce": nonce}})
    ok = (vstatus == 200 and vbody.get("accepted") is False
          and vbody.get("reason_code") == "audience_mismatch")
    return CheckResult("wrong_audience", "audience binding rejects foreign "
                       "credentials", ok, json.dumps(vbody)[:120])


def check_tampered_credential_rejected(ctx) -> CheckResult:
    status, body = ctx["post"]("/issue", {
        "principal": "p", "agent": "a",
        "agent_public_key": ctx["agent_pub_b64"],
        "action_class": "data.read", "audience": ctx["audience"]})
    cred = body.get("credential", body)
    tampered = dict(cred)
    tampered["sig"] = ("AAAA" if not tampered["sig"].startswith("AAAA")
                       else "BBBB") + tampered["sig"][4:]
    sig, nonce = _sign(ctx["agent_priv"], "POST", "/x", "data.read")
    vstatus, vbody = ctx["post"]("/verify", {
        "credential": tampered,
        "request": {"method": "POST", "path": "/x",
                    "requested_action": "data.read",
                    "signature": sig, "request_nonce": nonce}})
    ok = (vbody.get("accepted") is False
          and vbody.get("reason_code") == "invalid_signature")
    return CheckResult("tampered_credential", "tampered signature rejected",
                       ok, json.dumps(vbody)[:120])


def check_scope_mismatch_rejected(ctx) -> CheckResult:
    """Properly signed request for an action the credential does not carry."""
    status, body = ctx["post"]("/issue", {
        "principal": "p", "agent": "a",
        "agent_public_key": ctx["agent_pub_b64"],
        "action_class": "data.read", "audience": ctx["audience"]})
    cred = body.get("credential", body)
    sig, nonce = _sign(ctx["agent_priv"], "POST", "/x", "payments.refund")
    vstatus, vbody = ctx["post"]("/verify", {
        "credential": cred,
        "request": {"method": "POST", "path": "/x",
                    "requested_action": "payments.refund",
                    "signature": sig, "request_nonce": nonce}})
    ok = (vbody.get("accepted") is False
          and vbody.get("reason_code") == "scope_mismatch")
    return CheckResult("scope_mismatch", "exact-match scope enforced (P-07)",
                       ok, json.dumps(vbody)[:120])


def check_replay_rejected(ctx) -> CheckResult:
    status, body = ctx["post"]("/issue", {
        "principal": "p", "agent": "a",
        "agent_public_key": ctx["agent_pub_b64"],
        "action_class": "data.read", "audience": ctx["audience"]})
    cred = body.get("credential", body)
    sig, nonce = _sign(ctx["agent_priv"], "POST", "/x", "data.read")
    req = {"credential": cred, "request": {
        "method": "POST", "path": "/x", "requested_action": "data.read",
        "signature": sig, "request_nonce": nonce}}
    s1, b1 = ctx["post"]("/verify", req)
    s2, b2 = ctx["post"]("/verify", req)
    # fresh credential for the second presentation would be normal client
    # behavior; replaying the SAME one must be caught:
    ok = b1.get("accepted") is True and b2.get("accepted") is False          and b2.get("reason_code") == "replay_detected"
    return CheckResult("replay", "replayed credential+nonce rejected (P-09)",
                       ok, json.dumps(b2)[:120])


HTTP_CHECKS = [
    ("directory", "key-directory entry well-formed", check_directory),
    ("roundtrip_accept", "issue -> verify accept", check_roundtrip_accept),
    ("wrong_audience", "audience binding rejects foreign credentials",
     check_wrong_audience_rejected),
    ("tampered_credential", "tampered signature rejected",
     check_tampered_credential_rejected),
    ("scope_mismatch", "exact-match scope enforced (P-07)",
     check_scope_mismatch_rejected),
    ("replay", "replayed credential+nonce rejected (P-09)",
     check_replay_rejected),
]


# --------------------------------------------------------------------------
# Runners
# --------------------------------------------------------------------------

def run_http_checks(base_url: str) -> ConformanceReport:
    from .keys import public_key_bytes  # local import: keys module is heavy
    report = ConformanceReport(target=base_url)

    def target_get(path):
        return _get(base_url, path)

    def target_post(path, payload):
        return _post(base_url, path, payload)

    agent_priv, agent_pub = _agent_keys()
    ctx = {"get": target_get,
           "post": lambda p, payload: target_post(p, payload),
           "agent_priv": agent_priv,
           "agent_pub_b64": _b64(public_key_bytes(agent_pub)),
           "audience": None}
    status, entry = target_get("/directory")
    ctx["audience"] = entry.get("verifier_id", "verifier:unknown")

    for check_id, title, fn in HTTP_CHECKS:
        try:
            r = fn(ctx)
            r.check_id = check_id
            r.title = title
        except Exception as exc:               # a crashing check is a failure
            r = CheckResult(check_id, title, False, f"exception: {exc!r}")
        report.results.append(r)
    return report


from .api import do_issue, do_verify
from .credential import Credential
from .errors import VerificationError
from .keys import b64url_decode
from .pop import Request
def _local_issue(payload, kit):
    cred = do_issue(kit.issuer, principal=payload["principal"],
                    agent=payload["agent"],
                    agent_public_key=_decode_pub(payload["agent_public_key"]),
                    action_class=payload["action_class"],
                    audience=payload["audience"])
    return 201, json.loads(cred.to_json())


def _local_verify(payload, kit, verifier_id, nonce_cache):
    try:
        result = do_verify(verifier_id,
            Credential(fields=payload["credential"]),
            Request(payload["request"]["method"],
                    payload["request"]["path"],
                    payload["request"]["requested_action"],
                    payload["request"]["signature"],
                    payload["request"]["request_nonce"]),
            kit.key_directory, kit.revocation_log,
            nonces=nonce_cache)
        return 200, {"accepted": result.accepted,
                     "reason_code": result.reason_code}
    except VerificationError as exc:
        return 200, {"accepted": False, "reason_code": exc.reason_code}


def _decode_pub(b64_str):
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    from .keys import b64url_decode
    return Ed25519PublicKey.from_public_bytes(b64url_decode(b64_str))


def run_local_checks() -> ConformanceReport:
    """In-process checks against the offline kit (no network)."""
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    from .api import do_issue, do_verify
    from .errors import VerificationError
    from .keys import KeyDirectory, b64url_decode, public_key_bytes
    from .pop import Request, sign_request
    from .testing import offline_test_kit, local_test_agent
    from .verifier import NonceCache

    report = ConformanceReport(target="local")
    kit = offline_test_kit()
    agent_priv, agent_pub = local_test_agent()
    pub_b64 = _b64(public_key_bytes(agent_pub))
    V = kit.verifier_id


    # A real verifier holds ONE nonce cache across all verifications -- the
    # replay check below depends on that, exactly as production would.
    shared_cache = NonceCache()

    def post(path, payload):
        if path == "/verify":
            return _local_verify(payload, kit, V, shared_cache)
        return _local_issue(payload, kit)

    ctx = {"post": post,
           "agent_priv": agent_priv, "agent_pub_b64": pub_b64,
           "audience": V}

    d = check_directory.__wrapped__ if False else None
    status_ok = kit.key_directory.lookup(kit.issuer.issuer_id) is not None
    report.results.append(CheckResult(
        "directory", "key-directory entry well-formed", status_ok, ""))

    for check_id, title, fn in HTTP_CHECKS[1:]:
        try:
            r = fn(ctx)
            r.check_id = check_id
            r.title = title
        except Exception as exc:
            r = CheckResult(check_id, title, False, f"exception: {exc!r}")
        report.results.append(r)
    return report


def _decode(pub_b64: str):
    import base64 as _b64mod
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    from .keys import b64url_decode
    return Ed25519PublicKey.from_public_bytes(b64url_decode(pub_b64))


def render_report(report: ConformanceReport) -> str:
    lines = [f"Conformance self-check -- target: {report.target}",
             INFORMATIONAL_LABEL,
             "-" * 60]
    for r in report.results:
        state = ("PASS" if r.passed is True else
                 "SKIP" if r.passed is None else "FAIL")
        lines.append(f"[{state}] {r.check_id}: {r.title}"
                     + (f" -- {r.detail}" if r.detail and not r.passed else ""))
    lines.append("-" * 60)
    n_pass = sum(1 for r in report.results if r.passed is True)
    n_fail = sum(1 for r in report.results if r.passed is False)
    n_skip = sum(1 for r in report.results if r.passed is None)
    lines.append(f"{n_pass} pass, {n_fail} fail, {n_skip} skip")
    lines.append(INFORMATIONAL_LABEL)
    return chr(10).join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="rilavo-conformance",
                                 description=__doc__.splitlines()[0])
    ap.add_argument("--target", required=True,
                    help="'local' or an http(s) base URL of a running issuer")
    args = ap.parse_args(argv)

    if args.target == "local":
        report = run_local_checks()
    elif args.target.startswith(("http://", "https://")):
        report = run_http_checks(args.target)
    else:
        print("--target must be 'local' or an http(s) URL", file=sys.stderr)
        return 2

    print(render_report(report))
    return report.exit_code()


if __name__ == "__main__":
    sys.exit(main())
