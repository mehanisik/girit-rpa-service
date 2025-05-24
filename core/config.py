# core/config.py
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
    _sqlalchemy_database_uri_base = (
        f"postgresql+psycopg2://{DATABASE_USER}:{_db_password_encoded}"
        f"@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
    )

    if "supabase.com" in DATABASE_HOST:
        SQLALCHEMY_DATABASE_URI = f"{_sqlalchemy_database_uri_base}?sslmode=require"
    else:
        SQLALCHEMY_DATABASE_URI = _sqlalchemy_database_uri_base 

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    _cors_origins_str = os.getenv("CORS_ORIGINS", "http://localhost:3000")
    CORS_ORIGINS: List[str] = [origin.strip() for origin in _cors_origins_str.split(',')]

    SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key_change_me_in_production")

    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL

    CELERY_TASK_ALWAYS_EAGER = os.getenv('CELERY_TASK_ALWAYS_EAGER', 'False').lower() in ('true', '1', 't')
    CELERY_TASK_EAGER_PROPAGATES = CELERY_TASK_ALWAYS_EAGER 

    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads') 
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024 

    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")

    ADMIN_PASSWORD_HASH = os.getenv("ADMIN_PASSWORD_HASH", "pbkdf2:sha256:600000$INVALIDHASH$INVALID") 


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = os.getenv("SQLALCHEMY_ECHO", "False").lower() in ('true', '1', 't')



class ProductionConfig(Config):
    DEBUG = False
    CELERY_TASK_ALWAYS_EAGER = False 

flask_env = os.getenv("FLASK_ENV", "development")

if flask_env == "production":
    app_config = ProductionConfig()
else:
    app_config = DevelopmentConfig()

settings = app_config



PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
ABSOLUTE_UPLOAD_FOLDER = os.path.join(PROJECT_ROOT, settings.UPLOAD_FOLDER)

if not os.path.exists(ABSOLUTE_UPLOAD_FOLDER):
    os.makedirs(ABSOLUTE_UPLOAD_FOLDER, exist_ok=True)
settings.UPLOAD_FOLDER = ABSOLUTE_UPLOAD_FOLDER # Store the absolute path