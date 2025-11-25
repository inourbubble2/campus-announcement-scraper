import asyncio
import time
import httpx

class RateLimitedClient:
    def __init__(self, interval: float = 1.0, **kwargs):
        """
        Args:
            interval: Minimum time interval (in seconds) between requests.
            **kwargs: Arguments passed to httpx.AsyncClient.
        """
        self.client = httpx.AsyncClient(**kwargs)
        self.interval = interval
        self.last_request_time = 0.0
        self._lock = asyncio.Lock()

    async def get(self, url: str, **kwargs) -> httpx.Response:
        async with self._lock:
            current_time = time.time()
            elapsed = current_time - self.last_request_time

            if elapsed < self.interval:
                wait_time = self.interval - elapsed
                print(f"Rate limiting: waiting {wait_time:.2f}s")
                await asyncio.sleep(wait_time)

            try:
                response = await self.client.get(url, **kwargs)
                self.last_request_time = time.time()
                return response
            except Exception as e:
                # Update last request time even on failure to maintain rate limit
                self.last_request_time = time.time()
                raise e

    async def close(self):
        await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()