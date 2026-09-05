import time
from collections import defaultdict, deque
from typing import Tuple


class InMemoryRateLimiter:
    """
    High-performance sliding-window in-memory rate limiter.
    Acts as the digital turnstile to prevent resource exhaustion and DoS abuse.
    """
    def __init__(self, requests_per_minute: int = 60):
        self.limit = requests_per_minute
        self.window = 60.0  # seconds
        self._records = defaultdict(deque)

    def is_rate_limited(self, ip: str) -> Tuple[bool, int]:
        """
        Evaluate if an IP has exceeded the allowed rate.
        Returns (is_limited, remaining_requests).
        """
        now = time.time()
        timestamps = self._records[ip]

        # Purge timestamps outside the 60-second window
        while timestamps and timestamps[0] <= now - self.window:
            timestamps.popleft()

        if len(timestamps) >= self.limit:
            return True, 0

        timestamps.append(now)
        remaining = max(0, self.limit - len(timestamps))

        # Memory hygiene: prune completely empty records if table exceeds 10,000 entries
        if len(self._records) > 10000:
            stale_ips = [k for k, v in self._records.items() if not v or v[-1] <= now - self.window]
            for k in stale_ips:
                del self._records[k]

        return False, remaining

    def reset(self):
        """Clears all tracking records (useful for test isolation)."""
        self._records.clear()


rate_limiter = InMemoryRateLimiter(requests_per_minute=60)
