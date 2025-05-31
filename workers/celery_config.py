from celery.schedules import crontab
from config import get_config

config = get_config()

# Celery configuration
CELERY_CONFIG = {
    # Broker settings
    'broker_url': config.CELERY_BROKER_URL,
    'result_backend': config.CELERY_RESULT_BACKEND,

    # Task settings
    'task_serializer': 'json',
    'result_serializer': 'json',
    'accept_content': ['json'],
    'timezone': 'UTC',
    'enable_utc': True,

    # Worker settings
    'worker_send_task_events': True,
    'task_send_sent_event': True,
    'worker_prefetch_multiplier': 1,
    'worker_max_tasks_per_child': 1000,

    # Task execution settings
    'task_acks_late': True,
    'task_reject_on_worker_lost': True,
    'task_default_retry_delay': 60,
    'task_max_retries': 3,

    # Result backend settings
    'result_expires': 3600,  # 1 hour
    'result_backend_transport_options': {
        'master_name': 'mymaster'
    },

    # Task routing
    'task_routes': {
        'workers.tasks.purchase_package': {'queue': 'package_purchases'},
        'workers.tasks.send_notification': {'queue': 'notifications'},
        'workers.tasks.send_bulk_notifications': {'queue': 'bulk_notifications'},
        'workers.tasks.cleanup_expired_tokens': {'queue': 'maintenance'},
        'workers.tasks.validate_im3_tokens': {'queue': 'maintenance'},
    },

    # Scheduled tasks (Celery Beat)
    'beat_schedule': {
        'cleanup-expired-tokens': {
            'task': 'workers.tasks.cleanup_expired_tokens',
            'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
        },
        'validate-im3-tokens': {
            'task': 'workers.tasks.validate_im3_tokens',
            'schedule': crontab(hour=3, minute=0, day_of_week=0),  # Weekly on Sunday at 3 AM
            'kwargs': {'batch_size': 50}
        },
    },
}