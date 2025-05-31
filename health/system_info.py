import os
import sys
import subprocess
from typing import Dict, Any


class SystemInfo:
    """System information collector"""

    @staticmethod
    def get_version() -> str:
        """Get application version from various sources"""
        try:
            # Try to get from git tag
            result = subprocess.run(['git', 'describe', '--tags', '--abbrev=0'],
                                    capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass

        try:
            # Try to get from git commit hash
            result = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'],
                                    capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return f"commit-{result.stdout.strip()}"
        except:
            pass

        # Fallback to environment variable or default
        return os.getenv('APP_VERSION', '2.0.0-dev')

    @staticmethod
    def get_system_info() -> Dict[str, Any]:
        """Get comprehensive system information"""
        return {
            'python_version': sys.version.split()[0],
            'platform': sys.platform,
            'environment': os.getenv('FLASK_ENV', 'production'),
            'user': os.getenv('USER', 'ardzz'),
            'hostname': os.getenv('HOSTNAME', 'im3wrap-backend'),
            'timezone': 'UTC',
            'pid': os.getpid(),
            'working_directory': os.getcwd()
        }

    @staticmethod
    def get_build_info() -> Dict[str, Any]:
        """Get build information"""
        return {
            'version': SystemInfo.get_version(),
            'environment': os.getenv('FLASK_ENV', 'production')
        }