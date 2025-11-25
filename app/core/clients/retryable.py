import asyncio
import httpx
from typing import Any, Callable, Dict, Optional

class RetryableClient:
    def __init__(
        self,
        base_url: Optional[str] = None,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        **kwargs
    ):
        """
        HTTP client with automatic retry logic.

        Args:
            base_url: Base URL for endpoints (optional).
            max_retries: Maximum number of retry attempts on failure.
            retry_delay: Initial delay between retries (in seconds), doubles with each retry.
            **kwargs: Arguments passed to httpx.AsyncClient.
        """
        self.client = httpx.AsyncClient(**kwargs)
        self.base_url = base_url
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def _build_url(self, url: str) -> str:
        """Build full URL from base_url and endpoint."""
        if self.base_url:
            return f"{self.base_url.rstrip('/')}/{url.lstrip('/')}"
        return url

    async def _request_with_retry(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> httpx.Response:
        """
        Execute HTTP request with retry logic.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.).
            url: Endpoint URL (will be joined with base_url if set).
            **kwargs: Additional arguments passed to httpx request.

        Returns:
            httpx.Response object.

        Raises:
            httpx.HTTPError: If all retry attempts fail.
        """
        full_url = self._build_url(url)

        for attempt in range(self.max_retries + 1):
            try:
                response = await self.client.request(method, full_url, **kwargs)
                response.raise_for_status()
                return response

            except (httpx.HTTPError, httpx.RequestError) as e:
                if attempt == self.max_retries:
                    print(f"Request failed after {self.max_retries} retries: {method} {full_url} - {e}")
                    raise

                delay = self.retry_delay * (2 ** attempt)
                print(f"Request failed (attempt {attempt + 1}/{self.max_retries + 1}), retrying in {delay}s: {method} {full_url} - {e}")
                await asyncio.sleep(delay)

        return None

    async def get(self, url: str, **kwargs) -> httpx.Response:
        """Send GET request with retry logic."""
        return await self._request_with_retry("GET", url, **kwargs)

    async def post(
        self,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> httpx.Response:
        """Send POST request with retry logic."""
        return await self._request_with_retry("POST", url, data=data, json=json, **kwargs)

    async def put(
        self,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> httpx.Response:
        """Send PUT request with retry logic."""
        return await self._request_with_retry("PUT", url, data=data, json=json, **kwargs)

    async def delete(self, url: str, **kwargs) -> httpx.Response:
        """Send DELETE request with retry logic."""
        return await self._request_with_retry("DELETE", url, **kwargs)

    async def close(self):
        await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()