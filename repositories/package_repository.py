from typing import List
from .base_repository import BaseRepository
from models.package import Package
from core.exceptions import PackageNotFoundError


class PackageRepository(BaseRepository[Package]):
    """Package repository"""

    def __init__(self):
        super().__init__(Package)

    def get_by_pvr_code(self, pvr_code: str) -> Package:
        """Get package by PVR code"""
        return self.get_by_field('pvr_code', pvr_code)

    def get_or_raise(self, package_id: int) -> Package:
        """Get package by ID or raise exception"""
        package = self.get_by_id(package_id)
        if not package:
            raise PackageNotFoundError(f"Package with ID {package_id} not found")
        return package

    def get_available_packages(self) -> List[Package]:
        """Get all available packages"""
        return self.get_all()