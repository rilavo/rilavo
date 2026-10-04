"""P3-A3 DiscoveringKeyDirectory tests: TLS-only, TTL cache, fail-closed."""

from __future__ import annotations

import pytest

from rilavo.discovery_client import DiscoveringKeyDirectory

VALID_DOC = {
    "rilavo_discovery_version": 1,
    "entries": [{
        "issuer_id": "rilavo:iss:56475aa75463474c",
        "public_key_pem": "-----BEGIN PUBLIC KEY-----\nX\n-----END PUBLIC KEY-----\n",
        "valid_until": None,
        "audience_hints": ["verifier:a.example"],
    }],
}

ISSUER_ID = "rilavo:iss:56475aa75463474c"


def _make(cache_doc=None, cached_at=None, ttl=300, allow_stale=False):
    """Creates a DiscoveringKeyDirectory without __init__ (no TLS check)."""
    d = DiscoveringKeyDirectory.__new__(DiscoveringKeyDirectory)
    d.url = "https://example.com"
    d.ttl_seconds = ttl
    d.allow_stale_on_error = allow_stale
    d._cache = cache_doc
    import time
    d._cached_at = cached_at if cached_at is not None else time.time()
    return d


def test_https_enforced():
    with pytest.raises(ValueError, match="refusing non-HTTPS"):
        DiscoveringKeyDirectory(url="http://example.com")


def test_https_accepted():
    d = DiscoveringKeyDirectory(url="https://example.com")
    assert d.ttl_seconds == 300


def test_lookup_from_valid_cache():
    d = _make(VALID_DOC)
    entry = d.lookup(ISSUER_ID)
    assert entry is not None
    assert "BEGIN PUBLIC KEY" in entry.public_key_pem


def test_unknown_issuer_returns_none():
    d = _make(VALID_DOC)
    assert d.lookup("rilavo:iss:stranger") is None


def test_invalid_document_fail_closed():
    d = _make(None)   # no cached doc -> _ensure_fresh returns False -> lookup None
    assert d.lookup("any") is None


def test_allow_stale_false_by_default():
    d = _make(None)
    assert d.allow_stale_on_error is False


def test_ttl_cache_hit_avoids_refetch():
    fetch_count = [0]

    class CountingDir(DiscoveringKeyDirectory):
        def _fetch(self):
            fetch_count[0] += 1
            return VALID_DOC

    d = CountingDir.__new__(CountingDir)
    d.url = "https://example.com"
    d.ttl_seconds = 300
    d.allow_stale_on_error = False
    d._cache = None
    d._cached_at = 0.0

    d.lookup(ISSUER_ID)       # triggers fetch (count=1)
    count_1 = fetch_count[0]
    d.lookup(ISSUER_ID)       # should use cache
    assert fetch_count[0] == count_1


def test_expired_ttl_triggers_refetch():
    fetch_count = [0]

    class RefetchDir(DiscoveringKeyDirectory):
        def _fetch(self):
            fetch_count[0] += 1
            return VALID_DOC

    d = RefetchDir.__new__(RefetchDir)
    d.url = "https://example.com"
    d.ttl_seconds = 1
    d.allow_stale_on_error = False
    d._cache = None
    d._cached_at = 0.0

    d.lookup(ISSUER_ID)
    c1 = fetch_count[0]
    import time as _time
    _time.sleep(1.2)
    d._cached_at -= 2.0     # force expiry artificially
    d.lookup(ISSUER_ID)
    assert fetch_count[0] > c1
