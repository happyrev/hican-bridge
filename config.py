from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str = "default_secret_key"
    OPENAI_API_KEY: str = ""
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///hican.db"

    class Config:
        env_file = ".env"
        extra = 'ignore' # Ignore extra environment variables

settings = Settings()
