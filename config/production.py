from .base import Config


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    LOG_LEVEL = 'WARNING'

    # Strict CORS for production
    CORS_ORIGINS = [
        "https://im3wrap.my.id",
        "https://www.im3wrap.my.id",
        "https://app.im3wrap.my.id"
    ]
    CORS_METHODS = ['GET', 'POST', 'PUT', 'DELETE']  # No OPTIONS in production
    CORS_MAX_AGE = 86400  # 24 hours