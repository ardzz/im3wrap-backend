import logging
from datetime import datetime
from typing import Dict, Any, Optional, Callable

from celery import Task
from workers.exceptions import TaskError, TransientTaskError, PermanentTaskError

from .task_status import TaskStatus, TaskResult


class BaseTask(Task):
    """Base task class with common functionality"""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self._progress_callback: Optional[Callable] = None
        self._current_status = TaskStatus.PENDING

    def on_start(self, task_id, args, kwargs):
        """Called when task starts"""
        self.logger.info(f"Task {task_id} started with args: {args}, kwargs: {kwargs}")
        self.update_status(TaskStatus.PROCESSING)

    def on_success(self, retval, task_id, args, kwargs):
        """Called when task succeeds"""
        self.logger.info(f"Task {task_id} completed successfully")
        self.update_status(TaskStatus.COMPLETED)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Called when task fails"""
        self.logger.error(f"Task {task_id} failed: {exc}")
        self.update_status(TaskStatus.FAILED, error=str(exc))

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Called when task is retried"""
        self.logger.warning(f"Task {task_id} retrying due to: {exc}")
        self.update_status(TaskStatus.RETRYING, error=str(exc))

    def update_status(self, status: TaskStatus, progress: Optional[int] = None,
                      error: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        """Update task status"""
        self._current_status = status

        # Update task state in Celery
        meta = {
            'status': status.value,
            'timestamp': datetime.utcnow().isoformat(),
            'progress': progress,
            'error': error,
            'details': details or {}
        }

        self.update_state(state=status.value, meta=meta)

        # Call progress callback if available
        if self._progress_callback:
            self._progress_callback(status, progress, error, details)

        self.logger.info(f"Task status updated to: {status.value}")

    def update_progress(self, progress: int, message: Optional[str] = None):
        """Update task progress"""
        details = {'message': message} if message else None
        self.update_status(self._current_status, progress=progress, details=details)

    def set_progress_callback(self, callback: Callable):
        """Set progress callback function"""
        self._progress_callback = callback

    def handle_exception(self, exc: Exception) -> TaskResult:
        """Handle task exceptions with proper categorization"""
        if isinstance(exc, PermanentTaskError):
            self.logger.error(f"Permanent error: {exc}")
            self.update_status(TaskStatus.FAILED, error=str(exc))
            return TaskResult.FAILED

        elif isinstance(exc, TransientTaskError):
            self.logger.warning(f"Transient error: {exc}")
            raise self.retry(countdown=60, exc=exc)

        elif isinstance(exc, TaskError):
            self.logger.error(f"Task error: {exc}")
            self.update_status(TaskStatus.FAILED, error=str(exc))
            return TaskResult.FAILED

        else:
            self.logger.exception("Unexpected error occurred")
            self.update_status(TaskStatus.FAILED, error="An unexpected error occurred")
            return TaskResult.FAILED