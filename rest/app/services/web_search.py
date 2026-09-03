from dataclasses import dataclass

import httpx


TAVILY_SEARCH_URL = "https://api.tavily.com/search"


class WebSearchError(RuntimeError):
    pass


@dataclass(frozen=True)
class WebResult:
    title: str
    url: str
    content: str


async def search_web(query: str, api_key: str, limit: int = 4) -> list[WebResult]:
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                TAVILY_SEARCH_URL,
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "query": query,
                    "search_depth": "basic",
                    "max_results": limit,
                    "include_answer": False,
                    "include_raw_content": False,
                },
            )
            response.raise_for_status()
            payload = response.json()
    except (httpx.HTTPError, ValueError) as error:
        raise WebSearchError("External search failed.") from error

    try:
        results = []
        for item in payload.get("results", []):
            title = str(item.get("title", "")).strip()
            url = str(item.get("url", "")).strip()
            content = str(item.get("content", "")).strip()
            if not title or not url or not content:
                continue

            results.append(
                WebResult(
                    title=title,
                    url=url,
                    content=content,
                )
            )
    except (AttributeError, TypeError) as error:
        raise WebSearchError("External search returned invalid data.") from error

    return results
