import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration class"""

    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql+psycopg2://myuser:mypassword@db:5432/im3wrap')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET', 'jwt-super-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = False

    # Celery
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://redis:6379/0')
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://redis:6379/0')
    CELERY_WORKER_SEND_TASK_EVENTS = True
    CELERY_TASK_SEND_SENT_EVENT = True
    CELERY_ENABLE_UTC = True

    # WTF
    WTF_CSRF_ENABLED = False

    # CORS Configuration
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    CORS_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
    CORS_ALLOW_HEADERS = ['Content-Type', 'Authorization', 'X-Requested-With']
    CORS_SUPPORTS_CREDENTIALS = True
    CORS_MAX_AGE = 3600

    # IM3 API Configuration
    IM3_API_BASE_URL = 'https://myim3api1.ioh.co.id'
    IM3_RC4_PASSWORD = 'INDOSAT2798'
    IM3_API_TIMEOUT = 30

    # Task Configuration
    PACKAGE_TASK_CONFIG = {
        'eligibility_check_retries': 6,
        'eligibility_check_interval': 2,
        'payment_timeout': 300,
        'max_task_retries': 3
    }

    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

    # Security Headers
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Referrer-Policy': 'strict-origin-when-cross-origin'
    }