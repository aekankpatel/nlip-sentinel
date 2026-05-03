from app.config import get_settings
import httpx


class TavilySearchTool:
    async def search(self, query: str) -> list[dict[str, str]]:
        settings = get_settings()
        if not settings.has_tavily:
            return self._mock_results()

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.post(
                    "https://api.tavily.com/search",
                    json={
                        "api_key": settings.tavily_api_key,
                        "query": query,
                        "search_depth": "basic",
                        "max_results": 3,
                        "include_answer": False,
                    },
                )
                response.raise_for_status()
            data = response.json()
            results = data.get("results", [])
            normalized = [
                {
                    "title": item.get("title", "Untitled source"),
                    "url": item.get("url", ""),
                    "snippet": item.get("content", "")[:500],
                }
                for item in results
                if item.get("url")
            ]
            return normalized or self._mock_results()
        except Exception:
            return self._mock_results()

    def _mock_results(self) -> list[dict[str, str]]:
        return [
            {
                "title": "Airline fuel costs and profitability",
                "url": "https://www.iata.org/en/publications/economics/fuel-monitor/",
                "snippet": "Jet fuel is a substantial operating cost for airlines and can affect margins.",
            },
            {
                "title": "Oil prices, macro shocks, and transportation equities",
                "url": "https://www.eia.gov/energyexplained/oil-and-petroleum-products/prices-and-outlook.php",
                "snippet": "Oil price movements reflect supply, demand, and macro expectations.",
            },
            {
                "title": "Equity factor controls for return analysis",
                "url": "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html",
                "snippet": "Market factors are common controls when studying stock return variation.",
            },
        ]
