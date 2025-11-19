from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "ComplejidadRoutesAPI"

    SECRET_KEY: str = "Wubba-Lubba-Dub-Dub!"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    DATABASE_URL: str = "sqlite:///./complejidad.db"

    class Config:
        env_file = ".env"


settings = Settings()
