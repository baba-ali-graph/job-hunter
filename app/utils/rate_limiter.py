"""Rate limiting utilities."""

import asyncio
import time
from typing import Dict, Optional

from app.core.exceptions import RateLimitError
from app.core.logging import get_logger

logger = get_logger(__name__)


class RateLimiter:
    """Rate limiter implementation."""
    
    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, list] = {}
        self._lock = asyncio.Lock()
    
    async def is_allowed(self, key: str) -> bool:
        """Check if request is allowed for the given key."""
        async with self._lock:
            now = time.time()
            
            # Initialize key if not exists
            if key not in self.requests:
                self.requests[key] = []
            
            # Remove old requests outside the window
            self.requests[key] = [
                req_time for req_time in self.requests[key]
                if now - req_time < self.window_seconds
            ]
            
            # Check if under limit
            if len(self.requests[key]) < self.max_requests:
                self.requests[key].append(now)
                logger.debug("Request allowed", key=key, requests=len(self.requests[key]))
                return True
            else:
                logger.warning("Rate limit exceeded", key=key, requests=len(self.requests[key]))
                return False
    
    async def get_retry_after(self, key: str) -> int:
        """Get seconds until next request is allowed."""
        async with self._lock:
            if key not in self.requests or not self.requests[key]:
                return 0
            
            oldest_request = min(self.requests[key])
            retry_after = int(self.window_seconds - (time.time() - oldest_request))
            return max(0, retry_after)
    
    async def check_rate_limit(self, key: str) -> None:
        """Check rate limit and raise exception if exceeded."""
        if not await self.is_allowed(key):
            retry_after = await self.get_retry_after(key)
            raise RateLimitError(
                f"Rate limit exceeded. Try again in {retry_after} seconds.",
                retry_after=retry_after
            )


class TokenBucket:
    """Token bucket rate limiter."""
    
    def __init__(self, capacity: int = 10, refill_rate: float = 1.0):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time.time()
        self._lock = asyncio.Lock()
    
    async def consume(self, tokens: int = 1) -> bool:
        """Consume tokens from the bucket."""
        async with self._lock:
            now = time.time()
            
            # Refill tokens based on time passed
            time_passed = now - self.last_refill
            tokens_to_add = time_passed * self.refill_rate
            self.tokens = min(self.capacity, self.tokens + tokens_to_add)
            self.last_refill = now
            
            # Check if enough tokens available
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            else:
                return False
    
    async def wait_for_tokens(self, tokens: int = 1) -> float:
        """Wait for tokens to become available and return wait time."""
        async with self._lock:
            if self.tokens >= tokens:
                return 0.0
            
            tokens_needed = tokens - self.tokens
            wait_time = tokens_needed / self.refill_rate
            return wait_time