import time
from typing import Optional


class ResponseCache:
    """
    In-memory response cache with TTL (Time To Live) and size limits.
    Reduces redundant LLM calls and latency for repeat queries.

    - Normalizes queries (strip + lowercase) before cache key lookup
    - Enforces a max size to prevent unbounded memory growth
    - Evicts oldest entries when capacity is reached (LRU-style)
    """

    def __init__(self, default_ttl: int = 3600, max_size: int = 1000):
        self.cache: dict[str, tuple[str, float]] = {}  # {normalized_query: (response, expiry_ts)}
        self.default_ttl = default_ttl
        self.max_size = max_size
        self._hits = 0
        self._misses = 0

    def _normalize(self, query: str) -> str:
        """Normalize query for consistent cache key matching."""
        return query.strip().lower()

    def get(self, query: str) -> Optional[str]:
        """Retrieve cached response if it exists and hasn't expired."""
        normalized = self._normalize(query)
        if normalized in self.cache:
            response, expiry = self.cache[normalized]
            if time.time() < expiry:
                self._hits += 1
                return response
            else:
                del self.cache[normalized]  # Evict expired entry
        self._misses += 1
        return None

    def set(self, query: str, response: str, ttl: Optional[int] = None) -> None:
        """Store response in cache. Evicts oldest entry if at capacity."""
        normalized = self._normalize(query)
        ttl = ttl or self.default_ttl

        # Evict oldest entry if at capacity (simple FIFO eviction)
        if len(self.cache) >= self.max_size and normalized not in self.cache:
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]

        self.cache[normalized] = (response, time.time() + ttl)

    def clear(self) -> None:
        """Clear all cached entries."""
        self.cache.clear()
        self._hits = 0
        self._misses = 0

    def stats(self) -> dict:
        """Return cache performance statistics."""
        total = self._hits + self._misses
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": round(self._hits / total, 2) if total > 0 else 0.0,
            "ttl_seconds": self.default_ttl,
        }


# Singleton instance
cache_manager = ResponseCache()
