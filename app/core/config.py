from pydantic import BaseSettings, Field, PostgresDsn, AnyUrl

class Settings(BaseSettings):
    DB_0_URL: PostgresDsn = Field(..., env="db_0_url")
    DB_1_URL: PostgresDsn = Field(..., env="db_1_url")
    DB_2_URL: PostgresDsn = Field(..., env="db_2_url")

    class Config:
        env_file_encoding = "utf-8"


settings = Settings()
