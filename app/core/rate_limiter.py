import time
from collections import defaultdict
from typing import Dict, List
from app.core.exceptions import RateLimitError


class InMemoryRateLimiter:
    """In-memory rate limiter using sliding window log algorithm."""

    def __init__(self):
        self._requests: Dict[str, List[float]] = defaultdict(list)

    def check(self, key: str, max_requests: int = 5, window_seconds: int = 60) -> None:
        now = time.time()
        cutoff = now - window_seconds
        
        # Clean up old timestamps
        timestamps = [t for t in self._requests[key] if t > cutoff]
        self._requests[key] = timestamps

        if len(timestamps) >= max_requests:
            raise RateLimitError(
                message=f"Rate limit exceeded ({max_requests} requests per {window_seconds}s). Please wait before trying again."
            )

        self._requests[key].append(now)

    def reset(self, key: str) -> None:
        if key in self._requests:
            del self._requests[key]


rate_limiter = InMemoryRateLimiter()
