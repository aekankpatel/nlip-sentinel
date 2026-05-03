from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


def mask_secret(value: str | None) -> str:
    """Mask a secret for rare debugging without leaking the full value."""
    if not value or len(value) <= 8:
        return "****"
    return f"{value[:4]}...{value[-4:]}"


class Settings(BaseSettings):
    gemini_api_key: str | None = None
    tavily_api_key: str | None = None
    daytona_api_key: str | None = None
    daytona_api_token: str | None = None
    model_name: str = "gemini-1.5-flash"
    use_mocks: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        protected_namespaces=("settings_",),
    )

    @property
    def has_gemini(self) -> bool:
        return bool(self.gemini_api_key) and not self.use_mocks

    @property
    def has_tavily(self) -> bool:
        return bool(self.tavily_api_key) and not self.use_mocks

    @property
    def has_daytona(self) -> bool:
        return bool(self.daytona_api_key or self.daytona_api_token) and not self.use_mocks


@lru_cache
def get_settings() -> Settings:
    return Settings()
