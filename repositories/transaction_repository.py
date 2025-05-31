from typing import List
from .base_repository import BaseRepository
from models.transaction import Transaction


class TransactionRepository(BaseRepository[Transaction]):
    """Transaction repository"""

    def __init__(self):
        super().__init__(Transaction)

    def get_by_user(self, user_id: int) -> List[Transaction]:
        """Get transactions by user ID"""
        return self.session.query(self.model).filter(self.model.user_id == user_id).all()

    def get_by_status(self, status: str) -> List[Transaction]:
        """Get transactions by status"""
        return self.session.query(self.model).filter(self.model.status == status).all()