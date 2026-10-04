"""Pluggable nonce backend tests: memory and sqlite behave identically."""
import time

import pytest

from rilavo.nonce_backends import (
    InMemoryNonceBackend,
    RedisNonceBackend,
    SQLiteNonceBackend,
    make_nonce_backend,
)


@pytest.fixture(params=["memory", "sqlite"])
def backend(request, tmp_path):
    if request.param == "sqlite":
        return SQLiteNonceBackend(db_path=str(tmp_path / "nonces.db"))
    return InMemoryNonceBackend()


class TestEquivalence:
    def test_first_use_false(self, backend):
        assert backend.seen_before("n1", 3600) is False

    def test_second_use_true(self, backend):
        backend.seen_before("n1", 3600)
        assert backend.seen_before("n1", 3600) is True

    def test_different_nonces_independent(self, backend):
        assert backend.seen_before("a", 3600) is False
        assert backend.seen_before("b", 3600) is False

    def test_expiry_eviction_returns_usable_again(self, backend):
        now = time.time()
        backend.seen_before("exp", 10, now=now)
        # Simulate time passing beyond TTL:
        later = now + 11
        assert backend.seen_before("exp", 10, now=later) is False


class TestSQLiteSpecific:
    def test_sqlite_persists_across_instances(self, tmp_path):
        db = str(tmp_path / "test.db")
        b1 = SQLiteNonceBackend(db_path=db)
        b1.seen_before("persistent", 3600)
        b2 = SQLiteNonceBackend(db_path=db)
        assert b2.seen_before("persistent", 3600) is True


class TestFactory:
    def test_memory_factory(self):
        b = make_nonce_backend("memory")
        assert isinstance(b, InMemoryNonceBackend)

    def test_sqlite_factory(self, tmp_path):
        b = make_nonce_backend("sqlite", path=str(tmp_path / "t.db"))
        assert isinstance(b, SQLiteNonceBackend)

    def test_unknown_kind_raises(self):
        with pytest.raises(ValueError, match="unknown backend kind"):
            make_nonce_backend("invalid_kind")

class TestRedisFactory:
    def test_redis_factory_creates_backend(self):
        # Redis backend can be created (connection tested lazily)
        b = make_nonce_backend("redis", redis_url="redis://localhost:6379/0")
        assert isinstance(b, RedisNonceBackend)

    def test_redis_factory_default_url(self):
        b = make_nonce_backend("redis")
        assert isinstance(b, RedisNonceBackend)
        assert b._url == "redis://localhost:6379/0"

    def test_redis_fallback_on_connection_failure(self):
        # When Redis is unavailable, falls back to in-memory
        b = make_nonce_backend("redis", redis_url="redis://unreachable:6379/0")
        # First call triggers connection attempt and fallback
        result1 = b.seen_before("test-nonce-1", 60)
        result2 = b.seen_before("test-nonce-1", 60)
        # Should behave like in-memory: first=False, second=True (replay)
        assert result1 is False
        assert result2 is True

    def test_redis_key_hashing(self):
        # Nonce is hashed before storing in Redis (P-10 discipline)
        b = make_nonce_backend("redis", redis_url="redis://unreachable:6379/0")
        key = b._nonce_key("test-nonce")
        assert key.startswith("rilavo:nonce:")
        assert len(key) == len("rilavo:nonce:") + 32  # sha256 truncated to 32 chars

