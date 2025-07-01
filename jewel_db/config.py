# jewel_db/config.py

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # tell Pydantic where to find your .env
    model_config = ConfigDict(env_file=".env")

    DATABASE_URL: str = "sqlite:///./jewel.db"
    SECRET_KEY: str = "replace-me-with-secure-key"
    DEBUG: bool = True


# instantiate once
settings = Settings()

# expose for easy import elsewhere
DATABASE_URL = settings.DATABASE_URL
SECRET_KEY = settings.SECRET_KEY
DEBUG = settings.DEBUG
