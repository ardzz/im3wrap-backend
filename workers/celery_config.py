from datetime import timedelta

# Celery configuration
CELERY_CONFIG = {
    # Broker settings
    'broker_url': 'redis://localhost:6379/0',
    'result_backend': 'redis://localhost:6379/0',

    # Task settings
    'task_serializer': 'json',
    'accept_content': ['json'],
    'result_serializer': 'json',
    'timezone': 'UTC',
    'enable_utc': True,

    # Task routing
    'task_routes': {
        'purchase_package': {'queue': 'package_purchases'},
        'check_transaction_status': {'queue': 'package_purchases'},
        'cleanup_expired_tokens': {'queue': 'maintenance'},
        'validate_im3_tokens': {'queue': 'maintenance'},
        'send_notification': {'queue': 'notifications'},
        'send_bulk_notifications': {'queue': 'bulk_notifications'},
    },

    # Task execution settings
    'task_acks_late': True,
    'worker_prefetch_multiplier': 1,
    'task_reject_on_worker_lost': True,

    # Task retry settings
    'task_default_retry_delay': 60,  # 1 minute
    'task_max_retries': 3,

    # Beat schedule (for periodic tasks)
    'beat_schedule': {
        'cleanup-expired-tokens': {
            'task': 'cleanup_expired_tokens',
            'schedule': timedelta(hours=1),  # Run every hour
        },
        'validate-im3-tokens': {
            'task': 'validate_im3_tokens',
            'schedule': timedelta(hours=6),  # Run every 6 hours
        },
    },

    # Result backend settings
    'result_expires': 3600,  # 1 hour

    # Worker settings
    'worker_send_task_events': True,
    'task_send_sent_event': True,

    # Logging
    'worker_log_format': '[%(asctime)s: %(levelname)s/%(processName)s] %(message)s',
    'worker_task_log_format': '[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s',
}