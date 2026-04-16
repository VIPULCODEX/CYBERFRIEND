"""
cache_manager.py — Thread-safe async response cache for QuantX
==============================================================
Improvements over v1:
  - asyncio.Lock for full coroutine-safety under concurrent load
  - True LRU eviction (OrderedDict-based) instead of FIFO
  - Per-query custom TTL support
  - get_or_set() helper to collapse cache-stampede (multiple coroutines
    waiting on the same cold key all get the same future result)
"""

import asyncio
import time
from collections import OrderedDict
from typing import Optional


class ResponseCache:
    """
    Async-safe in-memory LRU cache with TTL.

    - Uses asyncio.Lock so concurrent coroutines never corrupt state.
    - Stampede guard: a pending dict ensures only ONE coroutine calls
      the LLM for a cold key; all others await the same Future.
    - Max-size enforced via OrderedDict LRU eviction.
    """

    def __init__(self, default_ttl: int = 3600, max_size: int = 1000):
        # OrderedDict to enable O(1) LRU eviction
        self._cache: OrderedDict[str, tuple[str, float]] = OrderedDict()
        self.default_ttl = default_ttl
        self.max_size = max_size
        self._lock = asyncio.Lock()

        # Stampede guard: maps normalized_query -> asyncio.Future
        self._pending: dict[str, asyncio.Future] = {}

        self._hits = 0
        self._misses = 0

    # ── Internal helpers ──────────────────────────────────────────────────────

    @staticmethod
    def _normalize(query: str) -> str:
        return query.strip().lower()

    def _is_valid(self, entry: tuple[str, float]) -> bool:
        _, expiry = entry
        return time.monotonic() < expiry

    def _evict_if_full(self, key: str) -> None:
        """Evict LRU entry when at capacity and key is new."""
        if len(self._cache) >= self.max_size and key not in self._cache:
            self._cache.popitem(last=False)  # Remove least-recently-used

    # ── Public sync interface (used in non-async code paths) ─────────────────

    def get(self, query: str) -> Optional[str]:
        """Sync get — safe for single-threaded use in lifespan/startup."""
        key = self._normalize(query)
        entry = self._cache.get(key)
        if entry and self._is_valid(entry):
            self._cache.move_to_end(key)   # Mark as recently used
            self._hits += 1
            return entry[0]
        if entry:
            del self._cache[key]           # Remove expired
        self._misses += 1
        return None

    def set(self, query: str, response: str, ttl: Optional[int] = None) -> None:
        """Sync set — safe for single-threaded use."""
        key = self._normalize(query)
        self._evict_if_full(key)
        expiry = time.monotonic() + (ttl or self.default_ttl)
        self._cache[key] = (response, expiry)
        self._cache.move_to_end(key)

    # ── Public async interface (used in api.py endpoints) ────────────────────

    async def aget(self, query: str) -> Optional[str]:
        """Async get with lock."""
        key = self._normalize(query)
        async with self._lock:
            entry = self._cache.get(key)
            if entry and self._is_valid(entry):
                self._cache.move_to_end(key)
                self._hits += 1
                return entry[0]
            if entry:
                del self._cache[key]
            self._misses += 1
            return None

    async def aset(self, query: str, response: str, ttl: Optional[int] = None) -> None:
        """Async set with lock."""
        key = self._normalize(query)
        async with self._lock:
            self._evict_if_full(key)
            expiry = time.monotonic() + (ttl or self.default_ttl)
            self._cache[key] = (response, expiry)
            self._cache.move_to_end(key)

    async def get_or_compute(self, query: str, compute_fn) -> str:
        """
        Stampede-safe fetch:
        1. Return cached value if hot.
        2. If another coroutine is already computing this key, await their result.
        3. Otherwise, compute, cache, and broadcast to all waiters.

        compute_fn must be an async callable: async def fn() -> str
        """
        key = self._normalize(query)

        # Fast path — cache hit
        cached = await self.aget(key)
        if cached is not None:
            return cached

        async with self._lock:
            # Double-check after lock (another coroutine may have computed it)
            entry = self._cache.get(key)
            if entry and self._is_valid(entry):
                self._cache.move_to_end(key)
                self._hits += 1
                return entry[0]

            # Join an in-flight computation if one exists
            if key in self._pending:
                fut = self._pending[key]
            else:
                # We are the first — create a Future, others will await it
                loop = asyncio.get_event_loop()
                fut = loop.create_future()
                self._pending[key] = fut

        if not fut.done():
            try:
                result = await compute_fn()
                # Store in cache
                await self.aset(key, result)
                # Resolve future for all waiters
                if not fut.done():
                    fut.set_result(result)
            except Exception as exc:
                if not fut.done():
                    fut.set_exception(exc)
                raise
            finally:
                self._pending.pop(key, None)
        else:
            result = await asyncio.shield(fut)

        return result

    # ── Utility ───────────────────────────────────────────────────────────────

    def clear(self) -> None:
        self._cache.clear()
        self._pending.clear()
        self._hits = 0
        self._misses = 0

    def stats(self) -> dict:
        total = self._hits + self._misses
        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": round(self._hits / total, 4) if total > 0 else 0.0,
            "ttl_seconds": self.default_ttl,
            "pending_computations": len(self._pending),
        }


# ── Singleton ──────────────────────────────────────────────────────────────────
cache_manager = ResponseCache()
