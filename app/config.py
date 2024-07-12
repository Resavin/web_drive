import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_port: str
    app_host: str
    app_port: int
    app_debug: bool
    database_url: str
    root_directory: str
    postgres_user: str
    postgres_port: str
    postgres_password: str
    postgres_db: str

    model_config = SettingsConfigDict(env_file="/web_drive/.env")

settings = Settings()
