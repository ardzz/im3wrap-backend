from typing import Type, TypeVar, Generic, Optional, List, Dict, Any
from sqlalchemy.orm import Session
from database import db

T = TypeVar('T')


class BaseRepository(Generic[T]):
    """Base repository class"""

    def __init__(self, model: Type[T]):
        self.model = model
        self.session = db.session

    def create(self, **kwargs) -> T:
        """Create a new record"""
        instance = self.model(**kwargs)
        self.session.add(instance)
        self.session.commit()
        return instance

    def get_by_id(self, id: int) -> Optional[T]:
        """Get record by ID"""
        return self.session.query(self.model).filter(self.model.id == id).first()

    def get_by_field(self, field: str, value: Any) -> Optional[T]:
        """Get record by field"""
        return self.session.query(self.model).filter(getattr(self.model, field) == value).first()

    def get_all(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[T]:
        """Get all records"""
        query = self.session.query(self.model)
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
        return query.all()

    def update(self, instance: T, **kwargs) -> T:
        """Update record"""
        for key, value in kwargs.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        self.session.commit()
        return instance

    def delete(self, instance: T) -> bool:
        """Delete record"""
        self.session.delete(instance)
        self.session.commit()
        return True

    def count(self) -> int:
        """Count all records"""
        return self.session.query(self.model).count()

    def exists(self, **kwargs) -> bool:
        """Check if record exists"""
        query = self.session.query(self.model)
        for key, value in kwargs.items():
            query = query.filter(getattr(self.model, key) == value)
        return query.first() is not None