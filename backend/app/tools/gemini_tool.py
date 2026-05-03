import httpx

from app.config import get_settings


class GeminiTool:
    """Small Gemini REST adapter with no secret logging."""

    async def generate_text(self, prompt: str) -> str | None:
        settings = get_settings()
        if not settings.has_gemini:
            return None

        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{settings.model_name}:generateContent"
        )
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}],
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 700,
            },
        }
        try:
            async with httpx.AsyncClient(timeout=20) as client:
                response = await client.post(
                    url,
                    params={"key": settings.gemini_api_key},
                    json=payload,
                )
                response.raise_for_status()
            data = response.json()
            parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
            return "\n".join(part.get("text", "") for part in parts).strip() or None
        except Exception:
            return None
