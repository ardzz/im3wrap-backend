from database import db


class Package(db.Model):
    __tablename__ = "packages"
    id = db.Column(db.Integer, primary_key=True)
    pvr_code = db.Column(db.String(255), unique=True, nullable=False)
    keyword = db.Column(db.String(255), nullable=False)
    discount_price = db.Column(db.Integer, nullable=False)
    normal_price = db.Column(db.Integer, nullable=False)
    package_name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    def __repr__(self):
        return f"<Package {self.package_name}>"
