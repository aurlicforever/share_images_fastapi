from pydantic import BaseSettings
import os

class Settings(BaseSettings):

    PROJECT_NAME: str = "Share Images"
    PROJECT_VERSION: str = "1.0.0"

    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "Share Images")
    PROJECT_VERSION: str = os.getenv("PROJECT_VERSION", "1.0.0")

    DB_USER: str = os.getenv("DB_USER", "myuser")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "password")
    DB_SERVER: str = os.getenv("DB_SERVER", "localhost")
    DB_NAME: str = os.getenv("DB_NAME", "share_images")
    DB_PORT: int = "5433"

    DB_ECHO_LOG: bool = os.getenv("DB_ECHO_LOG", "True").lower() == "true"

    JWT_SECRET: str = os.getenv("JWT_SECRET", "E5A88913-198B-4746-9080-060428D11FAE")
    JWT_ALGORITHHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))
    ISSUER: str = os.getenv("ISSUER", "http://localhost:8000")
    AUDIENCE: str = os.getenv("AUDIENCE", "http://localhost:4200")

    API_KEY_HEADER_NAME: str = os.getenv("API_KEY_HEADER_NAME", "X-Api-Key")
    API_KEY: str = os.getenv("API_KEY", "1BEF31B9-3893-4D1E-BAFD-B13E29540AB5")

    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", 465))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    EMAIL_FROM: str = os.getenv("EMAIL_FROM", "")

    SALT = str = os.getenv("SALT", "D3DBF0AF-84B5-432D-9F65-A83E3BF139F0")
    HASHLENGTH = int = int(os.getenv("HASHLENGTH", 10))
    
settings = Settings()