import logging
from datetime import datetime
from typing import Dict, Any, Optional


class TaskMonitor:
    """Task monitoring and progress tracking utility"""

    def __init__(self, task_id: str):
        self.task_id = task_id
        self.logger = logging.getLogger(f"TaskMonitor.{task_id}")
        self.start_time = datetime.utcnow()
        self.checkpoints: Dict[str, datetime] = {}

    def checkpoint(self, name: str, details: Optional[Dict[str, Any]] = None):
        """Record a checkpoint in task execution"""
        timestamp = datetime.utcnow()
        self.checkpoints[name] = timestamp

        elapsed = (timestamp - self.start_time).total_seconds()

        self.logger.info(f"Checkpoint '{name}' reached at {elapsed:.2f}s", extra={
            'task_id': self.task_id,
            'checkpoint': name,
            'elapsed_seconds': elapsed,
            'details': details or {}
        })

    def get_execution_time(self) -> float:
        """Get total execution time"""
        return (datetime.utcnow() - self.start_time).total_seconds()

    def get_checkpoint_duration(self, start_checkpoint: str, end_checkpoint: str) -> Optional[float]:
        """Get duration between two checkpoints"""
        if start_checkpoint not in self.checkpoints or end_checkpoint not in self.checkpoints:
            return None

        start_time = self.checkpoints[start_checkpoint]
        end_time = self.checkpoints[end_checkpoint]
        return (end_time - start_time).total_seconds()