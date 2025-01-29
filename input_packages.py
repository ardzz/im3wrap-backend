import json
from sqlalchemy.exc import IntegrityError

from database import Base, engine, Session
from models.package import Package

# Create tables (if they don't exist)
Base.metadata.create_all(engine)

# Create a session
session = Session()

try:
    packages = json.loads(open("parsed_packages.json").read())

    for package_data in packages:
        # Check for duplicates
        existing_package = session.query(Package).filter_by(pvr_code=package_data["pvr_code"]).first()
        if not existing_package:
            new_package = Package(
                pvr_code=package_data["pvr_code"],
                keyword=package_data["keyword"],
                discount_price=package_data["discount_price"],
                normal_price=package_data["normal_price"],
                package_name=package_data["package_name"]
            )
            session.add(new_package)

    session.commit()
    print(f"Imported {len(packages)} packages successfully!")

except IntegrityError as e:
    session.rollback()
    print(f"Duplicate entry error: {e}")

finally:
    session.close()