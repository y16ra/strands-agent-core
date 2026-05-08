from __future__ import annotations

import json
import logging
from urllib.error import HTTPError, URLError
from urllib.parse import quote_plus
from urllib.request import Request, urlopen

from strands.tools import tool

from config.settings import load_settings


logger = logging.getLogger(__name__)


def _search_with_tavily(query: str, api_key: str) -> str:
    # Import lazily so this module still works when tavily-python is not installed.
    from tavily import TavilyClient

    client = TavilyClient(api_key=api_key)
    response = client.search(query=query, max_results=5)
    results = response.get("results", [])
    lines = [f"- {item.get('title', '')}: {item.get('url', '')}" for item in results]
    return "\n".join(lines)


def _search_with_brave(query: str, api_key: str) -> str:
    encoded_query = quote_plus(query)
    req = Request(
        f"https://api.search.brave.com/res/v1/web/search?q={encoded_query}",
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
    if not settings.tavily_api_key and not settings.brave_api_key:
        return (
            "web_searchを使うには `TAVILY_API_KEY` または `BRAVE_API_KEY` の設定が必要です。"
        )
    try:
        if settings.tavily_api_key:
            return _search_with_tavily(query, settings.tavily_api_key)
        if settings.brave_api_key:
            return _search_with_brave(query, settings.brave_api_key)
        return "Web検索のプロバイダー設定が見つかりませんでした。"
    except ModuleNotFoundError as exc:
        logger.exception("Web search dependency is missing: %s", exc)
        return (
            "`tavily-python` が未インストールです。"
            " `pip install tavily-python` を実行するか、`BRAVE_API_KEY` を使ってください。"
        )
    except (HTTPError, URLError, TimeoutError, ValueError) as exc:
        logger.exception("Web search failed: %s", exc)
        return f"Web検索に失敗しました: {exc}"
