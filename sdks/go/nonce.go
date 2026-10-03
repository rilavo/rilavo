package rilavo

import (
	"context"
	"crypto/sha256"
	"encoding/hex"
	"sync"
	"time"

	"github.com/redis/go-redis/v9"
)

// InMemoryNonceCache is a thread-safe in-memory nonce cache with TTL-based expiration.
type InMemoryNonceCache struct {
	mu   sync.RWMutex
	seen map[string]int64 // nonce -> expiry (unix seconds)
}

// NewNonceCache creates a new in-memory nonce cache.
func NewNonceCache() *InMemoryNonceCache {
	return &InMemoryNonceCache{
		seen: make(map[string]int64),
	}
}

// SeenBefore returns true if the nonce was already seen within the window.
// Implements the NonceCache interface.
func (c *InMemoryNonceCache) SeenBefore(nonce string, windowSeconds int64, now int64) bool {
	c.mu.Lock()
	defer c.mu.Unlock()

	// Evict expired entries
	for n, exp := range c.seen {
		if exp <= now {
			delete(c.seen, n)
		}
	}

	if exp, ok := c.seen[nonce]; ok && exp > now {
		return true
	}
	c.seen[nonce] = now + windowSeconds
	// OTel: update nonce cache size metric
	SetNonceCacheSize(int64(len(c.seen)))
	return false
}

// RedisNonceCache is a Redis-backed nonce cache for distributed deployments.
// Uses atomic SET NX EX for check-and-set semantics.
// Gracefully falls back to in-memory on connection failure.
type RedisNonceCache struct {
	client      *redis.Client
	url         string
	keyPrefix   string
	fallback    *InMemoryNonceCache
	useFallback bool
	mu          sync.Mutex
}

// NewRedisNonceCache creates a new Redis nonce cache.
// Call Connect() before use, or it will lazily connect on first SeenBefore call.
func NewRedisNonceCache(url, keyPrefix string) *RedisNonceCache {
	if keyPrefix == "" {
		keyPrefix = "rilavo:nonce:"
	}
	return &RedisNonceCache{
		url:        url,
		keyPrefix:  keyPrefix,
		fallback:   NewNonceCache(),
		useFallback: false,
	}
}

// Connect establishes the Redis connection.
// Should be called during application startup.
func (c *RedisNonceCache) Connect(ctx context.Context) error {
	c.mu.Lock()
	defer c.mu.Unlock()

	if c.client != nil || c.useFallback {
		return nil
	}

	opts, err := redis.ParseURL(c.url)
	if err != nil {
		c.useFallback = true
		return err
	}

	c.client = redis.NewClient(opts)
	// Test connection with timeout
	ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
	defer cancel()
	if err := c.client.Ping(ctx).Err(); err != nil {
		c.client = nil
		c.useFallback = true
		return err
	}
	return nil
}

// nonceKey hashes the nonce to avoid storing raw nonces in Redis (P-10 discipline).
func (c *RedisNonceCache) nonceKey(nonce string) string {
	hash := sha256.Sum256([]byte(nonce))
	return c.keyPrefix + hex.EncodeToString(hash[:])[:32]
}

// SeenBefore returns true if the nonce was already seen within the window.
// Implements the NonceCache interface.
// Falls back to in-memory if Redis is unavailable.
func (c *RedisNonceCache) SeenBefore(nonce string, windowSeconds int64, now int64) bool {
	c.mu.Lock()
	// Check if we should use fallback
	if c.useFallback || c.client == nil {
		c.mu.Unlock()
		return c.fallback.SeenBefore(nonce, windowSeconds, now)
	}
	client := c.client
	c.mu.Unlock()

	key := c.nonceKey(nonce)

	// Atomic SET NX EX - returns true if key was set (first time), false if exists (replay)
	ctx := context.Background()
	set, err := client.SetNX(ctx, key, "1", time.Duration(windowSeconds)*time.Second).Result()
	if err != nil {
		// On error, fail-open to fallback
		c.mu.Lock()
		c.useFallback = true
		c.mu.Unlock()
		return c.fallback.SeenBefore(nonce, windowSeconds, now)
	}

	if set {
		// OTel: update nonce cache size metric (approximate)
		SetNonceCacheSize(1)
		return false // First time seeing this nonce
	}
	return true // Nonce already exists (replay detected)
}
