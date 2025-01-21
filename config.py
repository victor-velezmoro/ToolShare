from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    environment: str
    database_url: str
    secret_key: str
    access_token_expire_minutes: int = 30
    app_name: str = "ToolShare"

    class Config:
        env_file = ".env"  # Only for local development
        env_file_encoding = 'utf-8'


settings = Settings()

