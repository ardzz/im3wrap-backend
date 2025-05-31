from .base import Config
from .development import DevelopmentConfig
from .production import ProductionConfig
from .testing import TestingConfig

config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config(config_name=None):
    """Get configuration class based on environment"""
    if config_name is None:
        config_name = 'default'
    return config_map.get(config_name, DevelopmentConfig)