"""P3-A2: discovery publisher tests — flag off -> 404, flag on -> schema-valid doc."""

from __future__ import annotations

import json

from rilavo.discovery import validate_discovery_document
from rilavo.service import RilavoService


def test_discovery_off_returns_404():
    svc = RilavoService(port=0, serve_discovery=False).start()
    try:
        import urllib.request
        try:
            urllib.request.urlopen(svc.url + "/.well-known/rilavo", timeout=5)
            assert False, "should 404"
        except Exception as e:
            assert "404" in str(e) or "HTTP Error" in str(e)
    finally:
        svc.stop()


def test_discovery_on_serves_schema_valid_document():
    from rilavo.discovery import validate_discovery_document
    svc = RilavoService(port=0, serve_discovery=True).start()
    try:
        import urllib.request
        with urllib.request.urlopen(svc.url + "/.well-known/rilavo", timeout=5) as r:
            doc = json.loads(r.read())
        ok, errors = validate_discovery_document(doc)
        assert ok, errors
    finally:
        svc.stop()


def test_discovery_entries_reflect_directory_state():
    svc = RilavoService(port=0, serve_discovery=True).start()
    try:
        import urllib.request
        with urllib.request.urlopen(svc.url + "/.well-known/rilavo", timeout=5) as r:
            doc = json.loads(r.read())
        entry = doc["entries"][0]
        assert entry["issuer_id"] == svc.state.issuer.issuer_id
        assert "BEGIN PUBLIC KEY" in entry["public_key_pem"]
        # audience_hints reflects the verifier's configured audience:
        assert svc.state.verifier_id in entry["audience_hints"]
    finally:
        svc.stop()
