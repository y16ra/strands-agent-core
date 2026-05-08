from __future__ import annotations

import json
import logging
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from tavily import TavilyClient
from strands.tools import tool

from config.settings import load_settings


logger = logging.getLogger(__name__)


def _search_with_tavily(query: str, api_key: str) -> str:
    client = TavilyClient(api_key=api_key)
    response = client.search(query=query, max_results=5)
    results = response.get("results", [])
    lines = [f"- {item.get('title', '')}: {item.get('url', '')}" for item in results]
    return "\n".join(lines)


def _search_with_brave(query: str, api_key: str) -> str:
    req = Request(
        f"https://api.search.brave.com/res/v1/web/search?q={query}",
        headers={"Accept": "application/json", "X-Subscription-Token": api_key},
    )
    with urlopen(req, timeout=20) as resp:  # noqa: S310
        payload = json.loads(resp.read().decode("utf-8"))
    results = payload.get("web", {}).get("results", [])
    lines = [f"- {item.get('title', '')}: {item.get('url', '')}" for item in results[:5]]
    return "\n".join(lines)


@tool
def web_search(query: str) -> str:
    """Search the web using Tavily or Brave API."""
    settings = load_settings()
    try:
        if settings.tavily_api_key:
            return _search_with_tavily(query, settings.tavily_api_key)
        if settings.brave_api_key:
            return _search_with_brave(query, settings.brave_api_key)
        return ""
    except (HTTPError, URLError, TimeoutError, ValueError) as exc:
        logger.exception("Web search failed: %s", exc)
        return ""
