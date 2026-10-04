"""Pluggable NonceCache backends (P3-A3/D1 adjacent).

Abstracts the replay-defense cache behind a backend protocol so deployments
can swap between in-memory (default), SQLite, and Redis without changing
verifier gate logic.
"""

from __future__ import annotations

import hashlib
import sqlite3
import threading
import time
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    import redis
    ConnectionPool = redis.ConnectionPool


class NonceBackend(Protocol):
    """Contract matching the existing NonceCache in verifier.py."""

    def seen_before(self, nonce: str, window_seconds: int,
                    now: float | None = None) -> bool:
        """Returns True if this nonce was already used within the window."""
        ...

    def _evict(self, now: float) -> None:
        """Removes expired entries. Called internally by implementations."""
        ...


class InMemoryNonceBackend:
    """Re-implementation of the dict-based NonceCache from verifier.py.
    Byte-identical behavior to the original."""

    def __init__(self) -> None:
        self._seen: dict[str, float] = {}
        self._lock = threading.Lock()

    def seen_before(self, nonce: str, window_seconds: int,
                    now: float | None = None) -> bool:
        current = now if now is not None else time.time()
        with self._lock:
            self._evict(current)
            if nonce in self._seen:
                return True
            self._seen[nonce] = current + window_seconds
            return False

    def _evict(self, now: float) -> None:
        expired = [n for n, exp in self._seen.items() if exp <= now]
        for n in expired:
            del self._seen[n]


class SQLiteNonceBackend:
    """SQLite-backed nonce cache for multi-process deployments.
    Single connection, thread-locked. Lazy cleanup on each call."""

    def __init__(self, db_path: str = ":memory:") -> None:
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._lock = threading.Lock()
        self._conn.execute(
            "CREATE TABLE IF NOT EXISTS seen_nonces "
            "(nonce TEXT PRIMARY KEY, expiry REAL NOT NULL)"
        )
        self._conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_expiry ON seen_nonces(expiry)"
        )
        self._conn.commit()

    def seen_before(self, nonce: str, window_seconds: int,
                    now: float | None = None) -> bool:
        current = now if now is not None else time.time()
        with self._lock:
            # Lazy cleanup of expired entries:
            self._conn.execute("DELETE FROM seen_nonces WHERE expiry < ?",
                               (current,))
            row = self._conn.execute(
                "SELECT expiry FROM seen_nonces WHERE nonce = ?",
                (nonce,)).fetchone()
            if row is not None:
                return True
            self._conn.execute(
                "INSERT INTO seen_nonces VALUES (?, ?)",
                (nonce, current + window_seconds))
            self._conn.commit()
            return False

    def _evict(self, now: float) -> None:
        with self._lock:
            self._conn.execute("DELETE FROM seen_nonces WHERE expiry < ?",
                               (now,))


class RedisNonceBackend:
    """Redis-backed nonce cache for distributed multi-instance deployments.
    Uses Redis SET with EX expiry for atomic check-and-set semantics.
    Gracefully degrades to in-memory on connection failure (fail-open for availability)."""

    def __init__(
        self,
        url: str = "redis://localhost:6379/0",
        key_prefix: str = "rilavo:nonce:",
        connection_pool: ConnectionPool | None = None,
    ) -> None:
        self._key_prefix = key_prefix
        self._pool = connection_pool
        self._url = url
        self._local_fallback = InMemoryNonceBackend()
        self._use_fallback = False
        self._connect()

    def _connect(self) -> None:
        try:
            import redis
            if self._pool is None:
                self._pool = redis.ConnectionPool.from_url(
                    self._url,
                    max_connections=10,
                    decode_responses=True,
                )
            self._client = redis.Redis(connection_pool=self._pool)
            # Test connection
            self._client.ping()
            self._use_fallback = False
        except Exception:
            # Fail-open: use in-memory fallback if Redis unavailable
            self._use_fallback = True

    def _nonce_key(self, nonce: str) -> str:
        # Hash nonce to avoid storing raw nonces in Redis (P-10 discipline)
        nonce_hash = hashlib.sha256(nonce.encode()).hexdigest()[:32]
        return f"{self._key_prefix}{nonce_hash}"

    def seen_before(self, nonce: str, window_seconds: int,
                    now: float | None = None) -> bool:
        if self._use_fallback:
            return self._local_fallback.seen_before(nonce, window_seconds, now)

        now if now is not None else time.time()
        key = self._nonce_key(nonce)

        try:
            # Atomic check-and-set: SET key value EX expiry NX (only if not exists)
            # Returns True if key was set (first time), False if key already exists (replay)
            result = self._client.set(key, "1", ex=window_seconds, nx=True)
            return not result  # True if first time (no replay), False if replay detected
        except Exception:
            # On any Redis error, fail-open to local fallback
            self._use_fallback = True
            return self._local_fallback.seen_before(nonce, window_seconds, now)

    def _evict(self, now: float) -> None:
        # Redis handles expiry automatically via TTL; no manual eviction needed
        if self._use_fallback:
            self._local_fallback._evict(now)


def make_nonce_backend(kind: str = "memory",
                       path: str | None = None,
                       redis_url: str | None = None,
                       redis_key_prefix: str = "rilavo:nonce:") -> NonceBackend:
    """Factory for nonce cache backends.

    kind='memory' -> InMemoryNonceBackend (default, single-process)
    kind='sqlite' -> SQLiteNonceBackend (multi-process capable)
    kind='redis'  -> RedisNonceBackend (distributed multi-instance)
    """
    if kind == "memory":
        return InMemoryNonceBackend()
    if kind == "sqlite":
        return SQLiteNonceBackend(db_path=path or ":memory:")
    if kind == "redis":
        return RedisNonceBackend(
            url=redis_url or "redis://localhost:6379/0",
            key_prefix=redis_key_prefix,
        )
    raise ValueError(f"unknown backend kind: {kind!r}")
