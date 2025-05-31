"""
Legacy task file - kept for backward compatibility
This imports the new worker task implementation
"""

def purchase_package(*args, **kwargs):
    """Legacy function that delegates to the new worker task"""
    from app import app
    if hasattr(app, 'celery_tasks') and 'purchase_package' in app.celery_tasks:
        return app.celery_tasks['purchase_package'].delay(*args, **kwargs)
    else:
        raise RuntimeError("Celery tasks not properly initialized")