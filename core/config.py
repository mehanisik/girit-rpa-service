import os
from dotenv import load_dotenv
from typing import List
from urllib.parse import quote_plus

load_dotenv()

class Config:
    PROJECT_NAME = os.getenv("PROJECT_NAME", "Girit RPA Service (Flask)")
    API_V1_STR = os.getenv("API_V1_STR", "/api/v1")

    DATABASE_USER = os.getenv("DATABASE_USER")
    DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
    DATABASE_HOST = os.getenv("DATABASE_HOST")
    DATABASE_PORT = os.getenv("DATABASE_PORT")
    DATABASE_NAME = os.getenv("DATABASE_NAME")

    _db_password_encoded = quote_plus(DATABASE_PASSWORD) if DATABASE_PASSWORD else ""
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql+psycopg2://{DATABASE_USER}:{_db_password_encoded}"
        f"@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
        f"?sslmode=require"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    _cors_origins_str = os.getenv("CORS_ORIGINS", "http://localhost:3000")
    CORS_ORIGINS: List[str] = [origin.strip() for origin in _cors_origins_str.split(',')]

    SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key_change_me")

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = os.getenv("SQLALCHEMY_ECHO", "False").lower() in ('true', '1', 't')

class ProductionConfig(Config):
    DEBUG = False

flask_env = os.getenv("FLASK_ENV", "development")

if flask_env == "production":
    app_config = ProductionConfig()
else:
    app_config = DevelopmentConfig()

settings = app_config