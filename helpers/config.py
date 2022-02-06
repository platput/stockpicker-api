from pydantic import BaseSettings


class Settings(BaseSettings):
    sqlalchemy_db_url: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
