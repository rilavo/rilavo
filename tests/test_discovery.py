"""P3-A1 discovery document format tests."""

from __future__ import annotations

import json
from pathlib import Path

from rilavo.discovery import (
    validate_discovery_document,
    parse_discovery_document,
    golden_minimal,
    golden_multi,
)

DOCS = Path(__file__).resolve().parents[1] / "docs"


def test_golden_minimal_valid():
    doc = json.loads((DOCS / "p3a1_example_minimal_single_issuer.json").read_text())
    ok, errors = validate_discovery_document(doc)
    assert ok, errors


def test_golden_multi_issuer_valid():
    doc = json.loads((DOCS / "p3a1_example_multi_issuer_with_rotation.json").read_text())
    ok, errors = validate_discovery_document(doc)
    assert ok, errors


def test_absent_version_implies_v1():
    """P-26 style: absent rilavo_discovery_version means version 1."""
    doc = {"entries": []}
    ok, _ = validate_discovery_document(doc)
    assert ok


def test_version_2_rejected():
    doc = {"rilavo_discovery_version": 2, "entries": []}
    ok, errors = validate_discovery_document(doc)
    assert not ok
    assert "unsupported discovery version" in errors[0]


def test_unknown_top_level_fields_tolerated():
    """Fail-open at discovery layer for unknown fields."""
    doc = {"rilavo_discovery_version": 1, "entries": [],
           "future_field": "whatever"}
    ok, _ = validate_discovery_document(doc)
    assert ok


def test_bad_issuer_id_format_rejected():
    doc = {"entries": [{"issuer_id": "not-a-fingerprint",
                        "public_key_pem": "-----BEGIN PUBLIC KEY-----\nX\n"}]}
    ok, errors = validate_discovery_document(doc)
    assert not ok
    assert any("issuer_id" in e for e in errors)


def test_missing_public_key_pem_rejected():
    doc = {"entries": [{"issuer_id": "rilavo:iss:abc123"}]}
    ok, errors = validate_discovery_document(doc)
    assert not ok


def test_parse_returns_typed_entries():
    doc = {
        "rilavo_discovery_version": 1,
        "entries": [{
            "issuer_id": "rilavo:iss:56475aa75463474c",
            "public_key_pem": "-----BEGIN PUBLIC KEY-----\nX\n",
            "audience_hints": ["verifier:a.example"],
        }],
        "custom_extension": {"some": "data"},
    }
    parsed = parse_discovery_document(doc)
    assert parsed.version == 1
    assert len(parsed.entries) == 1
    assert parsed.entries[0].issuer_id == "rilavo:iss:56475aa75463474c"
    # unknown fields preserved but not validated:
    assert "custom_extension" in parsed.unknown_fields
