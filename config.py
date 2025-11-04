"""
Configuration file for production deployment
"""
import os
from pathlib import Path

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DOWNLOAD_FOLDER = Path(os.environ.get('DOWNLOAD_FOLDER', 'downloads'))
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max request size

    # Flask-SocketIO
    SOCKETIO_CORS_ALLOWED_ORIGINS = os.environ.get('ALLOWED_ORIGINS', '*')

    # Rate limiting
    RATELIMIT_ENABLED = os.environ.get('RATELIMIT_ENABLED', 'True').lower() == 'true'
    RATELIMIT_DEFAULT = os.environ.get('RATE_LIMIT', '10 per minute')

    # Cleanup
    FILE_CLEANUP_TIME = int(os.environ.get('FILE_CLEANUP_TIME', 60))  # minutes


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

    # Ensure secret key is set in production
    if Config.SECRET_KEY == 'dev-secret-key-change-in-production':
        raise ValueError("SECRET_KEY environment variable must be set in production")


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
