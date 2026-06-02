from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///../storage/freelaboard.db"
    API_KEY: str = "freela-secret-key-2024"
    STORAGE_PATH: str = "../storage"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
