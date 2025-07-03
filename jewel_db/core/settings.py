from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ── primary runtime switches ───────────────────────────────────────────
    debug: bool = False
    database_url: str = "sqlite:///./jewel.db"
    secret_key: str = "PLEASE_CHANGE_ME"  # used later for JWT / cookies

    # ── upload/media ───────────────────────────────────────────────────────
    media_dir: str = "media"
    max_image_px: int = 1600

    # ── model config ───────────────────────────────────────────────────────
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()  # imported as a singleton but can be overridden in tests
