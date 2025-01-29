from dataclasses import dataclass

from database import db


@dataclass
class Transaction(db.Model):
    __tablename__ = "transactions"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    package_id = db.Column(db.Integer, db.ForeignKey('packages.id'), nullable=False)
    qr_code = db.Column(db.String(1024), nullable=True)
    status = db.Column(db.String(255), default="PENDING")
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    def __repr__(self):
        return f"<Transaction {self.id}>"

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "package_id": self.package_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "status": self.status,
            "qr_code": self.qr_code,
        }

    @staticmethod
    def get_all():
        return Transaction.query.all()