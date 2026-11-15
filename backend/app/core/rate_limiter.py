import time
from collections import defaultdict
from typing import Dict, List
from fastapi import Request, HTTPException, status

class InMemoryRateLimiter:
    """
    Lightweight, thread-safe in-memory sliding-window rate limiter.
    Enforces per-client IP request limits on expensive computational endpoints.
    """
    def __init__(self, requests_per_minute: int = 30):
        self.requests_per_minute = requests_per_minute
        self.window_seconds = 60.0
        self._clients: Dict[str, List[float]] = defaultdict(list)

    async def __call__(self, request: Request):
        # Extract client IP, prioritizing X-Forwarded-For if behind a reverse proxy
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            client_ip = forwarded.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"

        now = time.time()
        cutoff = now - self.window_seconds

        # Clean timestamps older than sliding window
        timestamps = [t for t in self._clients[client_ip] if t > cutoff]
        
        if len(timestamps) >= self.requests_per_minute:
            retry_after = int(self.window_seconds - (now - timestamps[0])) + 1
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Maximum {self.requests_per_minute} requests per minute. Retry in {retry_after}s.",
                headers={"Retry-After": str(retry_after)}
            )

        timestamps.append(now)
        self._clients[client_ip] = timestamps

# Pre-configured limiter instances
heavy_computation_limiter = InMemoryRateLimiter(requests_per_minute=30)
report_generation_limiter = InMemoryRateLimiter(requests_per_minute=20)

