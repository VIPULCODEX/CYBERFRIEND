import time
import logging
from fastapi import HTTPException, Request

# Privacy-safe logger — only logs metadata, NEVER user query content
logger = logging.getLogger("quantx.security")
logger.setLevel(logging.WARNING)  # Minimal logging for production


class RateLimiter:
    """
    In-memory rate limiter per user/IP.
    Limits to max_requests per window_seconds.
    Includes periodic cleanup of stale entries to prevent memory leaks.
    """

    def __init__(self, max_requests: int = 5, window_seconds: int = 60):
        self.requests: dict[str, list[float]] = {}  # {identifier: [timestamps]}
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._last_cleanup = time.time()
        self._cleanup_interval = 300  # Purge stale entries every 5 minutes

    def _cleanup_stale(self) -> None:
        """Remove identifiers with no recent activity to prevent unbounded memory growth."""
        now = time.time()
        if now - self._last_cleanup < self._cleanup_interval:
            return
        stale_keys = [
            key for key, timestamps in self.requests.items()
            if all(now - t >= self.window_seconds for t in timestamps)
        ]
        for key in stale_keys:
            del self.requests[key]
        self._last_cleanup = now

    def is_allowed(self, identifier: str) -> bool:
        """Check if a client is within their rate limit window."""
        now = time.time()
        self._cleanup_stale()

        # Clean old timestamps for this identifier
        if identifier in self.requests:
            self.requests[identifier] = [
                t for t in self.requests[identifier]
                if now - t < self.window_seconds
            ]
        else:
            self.requests[identifier] = []

        if len(self.requests[identifier]) < self.max_requests:
            self.requests[identifier].append(now)
            return True

        logger.warning("Rate limit exceeded for client: %s", identifier)
        return False

    def get_remaining(self, identifier: str) -> int:
        """Return how many requests the client has left in the current window."""
        now = time.time()
        if identifier not in self.requests:
            return self.max_requests
        active = [t for t in self.requests[identifier] if now - t < self.window_seconds]
        return max(0, self.max_requests - len(active))


# Global singleton instance
rate_limiter = RateLimiter(max_requests=5, window_seconds=60)


def validate_query(query: str) -> str:
    """
    Normalize and validate user input:
    - Strip whitespace
    - Normalize to lowercase for cache consistency
    - Reject empty or very short queries (< 5 chars)
    """
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    clean_query = query.strip().lower()

    if len(clean_query) < 5:
        raise HTTPException(
            status_code=400,
            detail="Query is too short (minimum 5 characters)."
        )

    return clean_query


def get_client_id(request: Request) -> str:
    """Extract client identifier from request. Uses IP as fallback for anonymous users."""
    return request.client.host if request.client else "unknown"
