import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_port: str
    app_host: str
    app_port: int
    app_debug: bool
    database_url: str
    root_directory: str

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()