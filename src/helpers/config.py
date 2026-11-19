from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "mini-rag"
    APP_VERSION: str = "0.1.0"

    OPENAI_API_KEY: str = ""

    FILE_ALLOWED_TYPES: list = ["text/plain", "application/pdf"]
    FILE_MAX_SIZE: int = 10
    FILE_DEFAULT_CHUNK_SIZE: int = 512000

    MONGODB_URL: str
    MONGODB_DATABASE: str


    # شاور على ملف .env سواء شغلت السيرفر من برة أو من جوة فولدر src
    model_config = SettingsConfigDict(env_file=[".env", "../.env"])


def get_settings():
    return Settings()
