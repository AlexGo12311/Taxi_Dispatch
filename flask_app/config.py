import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    DB_CONFIG = {
        'host': 'localhost',
        'port': '5432',
        'database': 'taxi_dispatch_k',
        'user': 'postgres',
        'password': 'password'
    }

    SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@" \
                              f"{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    LOG_FILE_PATH = os.path.join(BASE_DIR, 'output', 'api_logs.txt')
    API_PREFIX = '/api/taxi'

    @staticmethod
    def init_app(app):
        log_dir = os.path.dirname(Config.LOG_FILE_PATH)
        os.makedirs(log_dir, exist_ok=True)


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}