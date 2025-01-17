from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    which_db: str
    db_username: str = ""
    db_password: str = ""
    db_name: str


@lru_cache()
def get_settings():
    return Settings()
