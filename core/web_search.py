"""
Web search abstraction.

Tries SerpAPI first, falls back to Brave Search, then to a stub
for local development / testing.
"""
from __future__ import annotations

import httpx
from loguru import logger

from config.settings import settings


class WebSearchTool:
    def search(self, query: str, num_results: int = 10) -> list[dict]:
        """Return a list of {title, url, snippet} dicts."""
        if settings.SERP_API_KEY:
            return self._serp(query, num_results)
        if settings.BRAVE_SEARCH_API_KEY:
            return self._brave(query, num_results)
        logger.warning("No search API key configured — returning empty results.")
        return []

    # ------------------------------------------------------------------ #

    def _serp(self, query: str, num: int) -> list[dict]:
        url = "https://serpapi.com/search"
        params = {
            "q": query,
            "api_key": settings.SERP_API_KEY,
            "num": num,
            "engine": "google",
        }
        resp = httpx.get(url, params=params, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        results = []
        for item in data.get("organic_results", []):
            results.append(
                {
                    "title": item.get("title", ""),
                    "url": item.get("link", ""),
                    "snippet": item.get("snippet", ""),
                }
            )
        return results[:num]

    def _brave(self, query: str, num: int) -> list[dict]:
        url = "https://api.search.brave.com/res/v1/web/search"
        headers = {
            "Accept": "application/json",
            "X-Subscription-Token": settings.BRAVE_SEARCH_API_KEY,
        }
        params = {"q": query, "count": num}
        resp = httpx.get(url, headers=headers, params=params, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        results = []
        for item in data.get("web", {}).get("results", []):
            results.append(
                {
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "snippet": item.get("description", ""),
                }
            )
        return results[:num]
