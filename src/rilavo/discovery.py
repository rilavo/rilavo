"""P3-A1 PROPOSAL — Discovery document format (.well-known/rilavo).

STATUS: PROPOSED -- not a Decided register item. This module provides ONLY:
  - format validation (validate_discovery_document),
  - golden example documents for testing,
  - zero fetching logic (P3-A3), zero publisher serving (P3-A2),
  - zero changes to verifier gate order or defaults.

Unknown-field tolerance: fail-open at discovery parsing layer.
Verification pipeline remains fail-closed: unknown discovery fields never
affect credential gate outcomes.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

DISCOVERY_VERSION_DEFAULT = 1
ISSUER_ID_PATTERN = re.compile(r"^rilavo:iss:[0-9a-f]{16}$")


@dataclass
class DiscoveryEntry:
    issuer_id: str
    public_key_pem: str
    valid_until: int | None = None
    audience_hints: list[str] = field(default_factory=list)


@dataclass
class DiscoveryDocument:
    version: int = DISCOVERY_VERSION_DEFAULT
    entries: list[DiscoveryEntry] = field(default_factory=list)
    unknown_fields: dict = field(default_factory=dict)


def validate_discovery_document(doc: dict) -> tuple[bool, list[str]]:
    """Validates structure and field types. Returns (ok, errors).

    Unknown top-level fields are tolerated (fail-open at discovery layer).
    """
    errors = []
    if not isinstance(doc, dict):
        return False, ["document must be a JSON object"]

    version = doc.get("rilavo_discovery_version", DISCOVERY_VERSION_DEFAULT)
    if not isinstance(version, int) or isinstance(version, bool):
        errors.append("rilavo_discovery_version must be an integer")
    elif version != DISCOVERY_VERSION_DEFAULT:
        errors.append(f"unsupported discovery version: {version}")

    entries = doc.get("entries", [])
    if not isinstance(entries, list):
        errors.append("entries must be an array")
        return len(errors) == 0, errors

    for i, entry in enumerate(entries):
        prefix = f"entries[{i}]"
        if not isinstance(entry, dict):
            errors.append(f"{prefix} must be an object")
            continue
        iss = entry.get("issuer_id", "")
        if not isinstance(iss, str) or not ISSUER_ID_PATTERN.match(iss):
            errors.append(f"{prefix}.issuer_id invalid: {iss!r}")
        pem = entry.get("public_key_pem", "")
        if not isinstance(pem, str) or "BEGIN PUBLIC KEY" not in pem:
            errors.append(f"{prefix}.public_key_pem must be PEM")

    return (len(errors) == 0), errors


def parse_discovery_document(doc: dict) -> DiscoveryDocument:
    """Parses a validated discovery document into typed objects."""
    ok, errors = validate_discovery_document(doc)
    if not ok:
        raise ValueError(f"invalid discovery document: {errors}")
    known_keys = {"rilavo_discovery_version", "entries"}
    unknown = {k: v for k, v in doc.items() if k not in known_keys}
    entries = []
    for e in doc.get("entries", []):
        vu = e.get("valid_until")
        entries.append(DiscoveryEntry(
            issuer_id=e["issuer_id"], public_key_pem=e["public_key_pem"],
            valid_until=vu if vu is not None else None,
            audience_hints=e.get("audience_hints", []),
        ))
    return DiscoveryDocument(
        version=doc.get("rilavo_discovery_version", DISCOVERY_VERSION_DEFAULT),
        entries=entries,
        unknown_fields=unknown,
    )


def golden_minimal() -> dict:
    return json.loads((Path(__file__).parents[2] / ".." / "docs" /
                       "p3a1_example_minimal_single_issuer.json").read_text())


def golden_multi() -> dict:
    return json.loads((Path(__file__).parents[2] / ".." / "docs" /
                       "p3a1_example_multi_issuer_with_rotation.json").read_text())
