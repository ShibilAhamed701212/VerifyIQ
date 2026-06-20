"""VLM API rate limiting with retry and backoff."""

import random
import threading
import time
from collections import deque


class RateLimiter:
    """Sliding-window rate limiter with thread safety."""

    def __init__(self, max_calls: int = 60, window: float = 60.0):
        self.max_calls = max_calls
        self.window = window
        self._lock = threading.Lock()
        self._timestamps: deque[float] = deque()

    def _trim(self) -> None:
        """Remove timestamps outside the current window."""
        cutoff = time.monotonic() - self.window
        while self._timestamps and self._timestamps[0] < cutoff:
            self._timestamps.popleft()

    def wait_if_needed(self) -> None:
        """Block if at the rate limit, then record the call."""
        with self._lock:
            self._trim()
            if len(self._timestamps) >= self.max_calls:
                sleep_for = self._timestamps[0] + self.window - time.monotonic()
                if sleep_for > 0:
                    time.sleep(sleep_for)
                self._trim()
            self._timestamps.append(time.monotonic())

    def record_call(self) -> None:
        """Record a timestamp manually (e.g. if wait was handled externally)."""
        with self._lock:
            self._timestamps.append(time.monotonic())

    def remaining(self) -> int:
        """Number of calls remaining in the current window."""
        with self._lock:
            self._trim()
            return max(0, self.max_calls - len(self._timestamps))

    def reset_at(self) -> float:
        """Timestamp (monotonic) when the rate limit window resets."""
        with self._lock:
            self._trim()
            if not self._timestamps:
                return 0.0
            return self._timestamps[0] + self.window


class ExponentialBackoff:
    """Exponential backoff with jitter for retrying operations."""

    def __init__(self, base_delay: float = 1.0, max_delay: float = 60.0, jitter: bool = True):
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.jitter = jitter

    def execute(self, fn, max_retries: int = 3) -> object:
        """Call fn, retrying with exponential backoff on exception."""
        last_exception = None
        for attempt in range(max_retries + 1):
            try:
                return fn()
            except Exception as e:
                last_exception = e
                if attempt < max_retries:
                    delay = min(self.base_delay * (2 ** attempt), self.max_delay)
                    if self.jitter:
                        delay *= 0.5 + random.random() * 0.5
                    time.sleep(delay)
        raise last_exception

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            return False
        return True
