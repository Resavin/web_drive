import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_port: int = 8000
    app_host: str
    app_debug: bool = True
    database_url: str | None = None
    root_directory: str | None = None
    postgres_user: str | None = None
    postgres_port: str | None = None
    postgres_password: str | None = None
    postgres_db: str | None = None

    model_config = SettingsConfigDict(env_file="/web_drive/.env")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.root_directory:
            os.makedirs(self.root_directory, exist_ok=True)


settings = Settings()
