from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    WHICH_DB: str
    DB_NAME: str
    DB_USERNAME: str = ""
    DB_PASSWORD: str = ""
    DB_HOST: str = ""
    JWT_SECRET: str
    JWT_ALG: str


@lru_cache()
def get_settings():
    return Settings()
