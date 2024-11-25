import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    environment: str
    database_url: str
    secret_key: str
    access_token_expire_minutes: int = 30
    app_name: str = "ToolShare"  # Default value in case it's not in the .env file

    class Config:
        # Dynamically load the .env file based on the environment
        env_file = f".env.{os.getenv('ENVIRONMENT', 'development')}"


# Create a settings instance for the application
settings = Settings()
