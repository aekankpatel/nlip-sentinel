from app.config import get_settings
import httpx


class TavilySearchTool:
    async def search(self, query: str) -> list[dict[str, str]]:
        settings = get_settings()
        if not settings.has_tavily:
            return self._mock_results(query)

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
            return normalized or self._mock_results(query)
        except Exception:
            return self._mock_results(query)

    def _mock_results(self, query: str = "") -> list[dict[str, str]]:
        topic = (query[:80].strip()) or "the research topic"
        return [
            {
                "title": f"Research overview: {topic[:60]}",
                "url": "https://scholar.example.com/overview",
                "snippet": (
                    f"Current research on '{topic}' draws on multiple empirical data sources. "
                    "Findings vary across studies and should be interpreted with appropriate caveats."
                ),
            },
            {
                "title": "Systematic review and evidence synthesis",
                "url": "https://www.cochrane.org/reviews",
                "snippet": (
                    "Systematic reviews aggregate evidence across independent studies and are considered "
                    "high-quality evidence. Meta-analyses can quantify effect sizes where individual "
                    "studies are underpowered."
                ),
            },
            {
                "title": "Statistical analysis and regression methodology",
                "url": "https://stats.stackexchange.com",
                "snippet": (
                    "Regression analysis and hypothesis testing are standard tools for quantitative "
                    "research. Controlling for confounders improves causal inference in observational data."
                ),
            },
        ]
