"""P3-A3 PROPOSAL -- DiscoveringKeyDirectory: consumer side of .well-known/rilavo.

STATUS: PROPOSED -- not a Decided register item. KeyDirectory-compatible
wrapper that fetches from an HTTPS endpoint. TLS-only, fail-closed.
"""

from __future__ import annotations

import json
import urllib.request

from .discovery import validate_discovery_document


class DiscoveredKeyEntry:
    """Minimal IssuerKeyEntry-compatible object."""
    def __init__(self, issuer_id: str, public_key_pem: str, valid_until):
        self.issuer_id = issuer_id
        self.public_key_pem = public_key_pem
        self.valid_until = valid_until


class DiscoveringKeyDirectory:
    """KeyDirectory-compatible wrapper sourcing entries from .well-known/rilavo.

    TLS-verified HTTPS only. TTL cache with fail-closed expiry.
    """

    def __init__(self, url: str, ttl_seconds: int = 300,
                 allow_stale_on_error: bool = False) -> None:
        if not url.startswith("https://"):
            raise ValueError(
                f"refusing non-HTTPS scheme for discovery: {url!r}. "
                "P-30 discipline requires TLS-verified transport."
            )
        self.url = url
        self.ttl_seconds = ttl_seconds
        self.allow_stale_on_error = allow_stale_on_error
        self._cache = None
        self._cached_at: float = 0.0

    def _fetch(self) -> dict:
        req = urllib.request.Request(
            self.url + "/.well-known/rilavo", method="GET")
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())

    def _ensure_fresh(self) -> bool:
        import time as _time
        now = _time.time()
        if self._cache is not None and (now - self._cached_at) < self.ttl_seconds:
            return True
        try:
            doc = self._fetch()
            ok, errors = validate_discovery_document(doc)
            if not ok:
                return False
            self._cache = doc
            self._cached_at = now
            return True
        except Exception:
            pass
        if self.allow_stale_on_error and self._cache is not None:
            return True
        return False

    def lookup(self, issuer_id: str):
        """KeyDirectory-compatible lookup."""
        if not self._ensure_fresh():
            return None     # fail-closed -> verifier sees unknown_issuer
        for entry in self._cache.get("entries", []):
            if entry["issuer_id"] == issuer_id:
                vu = entry.get("valid_until")
                if vu is not None and vu < time.time():
                    return None
                pem = entry.get("public_key_pem", "")
                if not pem:
                    return None
                return DiscoveredKeyEntry(issuer_id=issuer_id,
                                          public_key_pem=pem,
                                          valid_until=vu or 9999999999)
        return None
