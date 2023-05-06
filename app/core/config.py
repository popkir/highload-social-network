from pydantic import BaseSettings, Field, PostgresDsn, AnyUrl

class Settings(BaseSettings):
    DB_URL: PostgresDsn = Field(..., env="db_url")

    class Config:
        env_file_encoding = "utf-8"


settings = Settings()
