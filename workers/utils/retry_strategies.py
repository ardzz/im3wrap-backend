import random
from abc import ABC, abstractmethod


class RetryStrategy(ABC):
    """Abstract retry strategy"""

    @abstractmethod
    def should_retry(self, attempt: int, exception: Exception) -> bool:
        """Determine if task should be retried"""
        pass

    @abstractmethod
    def get_delay(self, attempt: int) -> int:
        """Get delay before next retry"""
        pass


class ExponentialBackoffRetry(RetryStrategy):
    """Exponential backoff retry strategy"""

    def __init__(self, max_retries: int = 3, base_delay: int = 60,
                 max_delay: int = 3600, backoff_factor: float = 2.0,
                 jitter: bool = True):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.jitter = jitter

    def should_retry(self, attempt: int, exception: Exception) -> bool:
        """Check if should retry based on attempt count"""
        return attempt <= self.max_retries

    def get_delay(self, attempt: int) -> int:
        """Calculate delay with exponential backoff"""
        delay = min(self.base_delay * (self.backoff_factor ** (attempt - 1)), self.max_delay)

        if self.jitter:
            # Add random jitter to avoid thundering herd
            delay = delay * (0.5 + random.random() * 0.5)

        return int(delay)


class LinearRetry(RetryStrategy):
    """Linear retry strategy"""

    def __init__(self, max_retries: int = 3, delay: int = 60):
        self.max_retries = max_retries
        self.delay = delay

    def should_retry(self, attempt: int, exception: Exception) -> bool:
        return attempt <= self.max_retries

    def get_delay(self, attempt: int) -> int:
        return self.delay