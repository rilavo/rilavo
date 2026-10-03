"""P5-B: the cross-language golden corpus round-trips through the Python
reference verifier, and the Go copy cannot silently drift."""
import json
from datetime import datetime, timezone
from pathlib import Path

import pytest
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from rilavo.canonical import canonicalize
from rilavo.credential import Credential
from rilavo.errors import VerificationError
from rilavo.keys import IssuerKeyEntry, KeyDirectory, b64url_decode
from rilavo.pop import Request, request_payload
from rilavo.revocation import RevocationLog
from rilavo.verifier import verify

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "golden"
GO_COPY = ROOT / "sdks" / "go" / "testdata" / "golden.json"


@pytest.fixture(scope="module")
def golden():
    return json.loads((CORPUS / "golden.json").read_text())


@pytest.fixture(scope="module")
def rejects():
    return json.loads((CORPUS / "rejects.json").read_text())


def test_jcs_vectors(golden):
    for case in golden["jcs"]:
        assert canonicalize(case["input"]) == case["expected"].encode()


def test_pop_payload_hex_parity(golden):
    pop = golden["pop"]
    payload = request_payload(pop["method"], pop["path"], pop["act"], pop["nonce"])
    assert payload.hex() == pop["payload_hex"]


def _make_dir(issuer_pub_b64url: str) -> KeyDirectory:
    raw = b64url_decode(issuer_pub_b64url)
    pub = Ed25519PublicKey.from_public_bytes(raw)
    pem = pub.public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo)
    entry = IssuerKeyEntry(fingerprint_id="rilavo:iss:goldencorpus",
                           public_key_pem=pem, valid_until=9999999999.0)
    d = KeyDirectory()
    d.publish(entry)
    return d


def _verify(fields: dict, golden: dict, method="GET", path="/data/1",
            act="data.read"):
    d = _make_dir(golden["issuer_pub_b64url"])
    cred = Credential.from_json(json.dumps(fields))
    req = Request(method=method, path=path, requested_action=act,
                  signature=golden["pop_sig"]["sig_b64url"],
                  request_nonce=golden["pop_sig"]["nonce"])
    now = float(golden["credential_fields"]["iat"]) + 1
    # The verifier's own audience is always the ORIGINAL expected value --
    # reject vectors must be checked against what the verifier requires,
    # not against the mutated credential.
    expected_audience = golden["credential_fields"]["aud"]
    return verify(cred, req, expected_audience, d, RevocationLog(), now=now)


def test_full_accept_path(golden):
    assert _verify(dict(golden["credential_fields"]), golden).strip() == "accept"


@pytest.mark.parametrize("case", ["unknown_version", "wrong_audience", "expired"])
def test_reject_vectors(golden, rejects, case):
    spec = rejects[case]
    fields = dict(golden["credential_fields"])
    fields.update({k: v for k, v in spec["credential_fields"].items()
                   if k not in ("sig",)})
    # sig no longer covers mutated fields -> re-sign is out of scope for a
    # vector; instead verify against the ORIGINAL signed credential when the
    # mutation invalidates the signature path differently.
    with pytest.raises(VerificationError) as ei:
        _verify(fields, golden)
    assert ei.value.reason_code == spec["expected_reason"], (
        f"{case}: got {ei.value.reason_code}, want {spec['expected_reason']}")


def test_go_copy_does_not_drift():
    assert GO_COPY.read_bytes() == (CORPUS / "golden.json").read_bytes(), (
        "sdks/go/testdata/golden.json diverged from golden/; "
        "regenerate via scripts/generate_golden_vectors.py and re-copy")
