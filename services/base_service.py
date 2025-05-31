from typing import TypeVar, Generic
from repositories.base_repository import BaseRepository
import logging

T = TypeVar('T')


class BaseService(Generic[T]):
    """Base service class"""

    def __init__(self, repository: BaseRepository[T]):
        self.repository = repository
        self.logger = logging.getLogger(self.__class__.__name__)

    def get_by_id(self, id: int) -> T:
        """Get entity by ID"""
        return self.repository.get_by_id(id)

    def get_all(self, limit: int = None, offset: int = None):
        """Get all entities"""
        return self.repository.get_all(limit=limit, offset=offset)

    def count(self) -> int:
        """Count entities"""
        return self.repository.count()