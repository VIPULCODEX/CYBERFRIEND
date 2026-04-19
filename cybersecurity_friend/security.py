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

    def get_active_sessions(self) -> int:
        """Return count of unique identifiers currently in the rate limiter."""
        return len(self.requests)


# Global singleton instance
rate_limiter = RateLimiter(max_requests=8, window_seconds=60)  # Increased slightly for better interactivity


def sanitize_input(text: str) -> str:
    """
    Remove potentially malicious HTML tags and scripts.
    Returns cleaned text.
    """
    import re
    # Remove <script> tags and their contents
    text = re.sub(r'<script.*?>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
    # Remove all other HTML tags
    text = re.sub(r'<.*?>', '', text)
    # Remove common SQL injection keywords if they appear as standalone words
    sql_patterns = [r'\bdrop\s+table\b', r'\bdelete\s+from\b', r'\bunion\s+select\b']
    for pattern in sql_patterns:
        text = re.sub(pattern, '[REDACTED]', text, flags=re.IGNORECASE)
    return text.strip()


def validate_query(query: str) -> str:
    """
    Normalize and validate user input:
    - Strip whitespace
    - Sanitize for harmful scripts/SQLi
    - Reject empty or very short queries (< 2 chars for general chatting)
    """
    if not query:
        return ""

    # Check for obvious malicious patterns before sanitizing
    import re
    malicious_patterns = [r'<script', r'javascript:', r'onerror=']
    if any(re.search(p, query, re.I) for p in malicious_patterns):
        logger.warning(f"Malicious pattern detected and blocked.")
        raise ValueError("Security Violation: Malicious script pattern detected.")

    clean_query = sanitize_input(query)

    if len(clean_query) < 2:
        return "" # Ignore tiny inputs

    return clean_query


def get_client_id(request: Request) -> str:
    """Extract client identifier from request. Uses IP as fallback for anonymous users."""
    return request.client.host if request.client else "unknown"
