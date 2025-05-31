import os
import redis
import logging
from typing import Dict, Any
from datetime import datetime, timedelta
from database import db


class HealthChecker:
    """Health check utilities for various system components"""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def check_database(self) -> Dict[str, Any]:
        """Check database connectivity and status"""
        try:
            start_time = datetime.utcnow()

            # Test basic connectivity
            result = db.session.execute(db.text('SELECT 1'))

            # Test a more complex query to check table access
            from models.user import User
            user_count = db.session.query(User).count()

            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            return {
                'status': 'healthy',
                'response_time_ms': round(response_time, 2),
                'connection': 'active',
                'user_count': user_count,
                'database_url': self._mask_db_url(db.engine.url),
                'last_checked': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            self.logger.error(f"Database health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'connection': 'failed',
                'last_checked': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            }

    def check_redis(self) -> Dict[str, Any]:
        """Check Redis connectivity and status"""
        try:
            start_time = datetime.utcnow()

            # Get Redis URL from config
            redis_url = os.getenv('CELERY_BROKER_URL', 'redis://redis:6379/0')

            # Parse Redis connection details
            if redis_url.startswith('redis://'):
                parts = redis_url.replace('redis://', '').split(':')
                host = parts[0]
                port = int(parts[1].split('/')[0]) if len(parts) > 1 else 6379
                db_num = int(parts[1].split('/')[1]) if '/' in parts[1] else 0
            else:
                host, port, db_num = 'redis', 6379, 0

            # Test Redis connection
            r = redis.Redis(host=host, port=port, db=db_num, socket_timeout=5)
            r.ping()

            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            # Get Redis info
            info = r.info()

            return {
                'status': 'healthy',
                'response_time_ms': round(response_time, 2),
                'version': info.get('redis_version', 'unknown'),
                'connected_clients': info.get('connected_clients', 0),
                'used_memory_human': info.get('used_memory_human', 'unknown'),
                'uptime_in_seconds': info.get('uptime_in_seconds', 0),
                'connection': 'active',
                'host': host,
                'port': port,
                'database': db_num,
                'last_checked': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            self.logger.error(f"Redis health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'connection': 'failed',
                'last_checked': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            }

    def check_celery_workers(self) -> Dict[str, Any]:
        """Check Celery worker status"""
        try:
            from flask import current_app
            celery = current_app.celery

            start_time = datetime.utcnow()

            # Get active workers
            inspect = celery.control.inspect(timeout=5)
            active_workers = inspect.active()
            stats = inspect.stats()

            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            if active_workers:
                worker_count = len(active_workers)
                worker_names = list(active_workers.keys())

                # Get worker statistics
                worker_stats = {}
                if stats:
                    for worker_name, worker_stat in stats.items():
                        worker_stats[worker_name] = {
                            'pool': worker_stat.get('pool', {}),
                            'rusage': worker_stat.get('rusage', {}),
                            'clock': worker_stat.get('clock', 'unknown')
                        }

                return {
                    'status': 'healthy',
                    'response_time_ms': round(response_time, 2),
                    'worker_count': worker_count,
                    'workers': worker_names,
                    'worker_stats': worker_stats,
                    'connection': 'active',
                    'last_checked': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
                }
            else:
                return {
                    'status': 'warning',
                    'response_time_ms': round(response_time, 2),
                    'worker_count': 0,
                    'message': 'No active workers found',
                    'connection': 'inactive',
                    'last_checked': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
                }
        except Exception as e:
            self.logger.error(f"Celery health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'connection': 'failed',
                'last_checked': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            }

    def check_disk_space(self) -> Dict[str, Any]:
        """Check disk space usage"""
        try:
            import shutil

            # Check current directory disk usage
            total, used, free = shutil.disk_usage('/')

            # Convert to GB
            total_gb = total // (1024 ** 3)
            used_gb = used // (1024 ** 3)
            free_gb = free // (1024 ** 3)
            usage_percent = (used / total) * 100

            # Determine status based on usage
            if usage_percent > 90:
                status = 'critical'
            elif usage_percent > 80:
                status = 'warning'
            else:
                status = 'healthy'

            return {
                'status': status,
                'total_gb': total_gb,
                'used_gb': used_gb,
                'free_gb': free_gb,
                'usage_percent': round(usage_percent, 2),
                'last_checked': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            self.logger.error(f"Disk space check failed: {e}")
            return {
                'status': 'unknown',
                'error': str(e),
                'last_checked': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            }

    def check_logs_directory(self) -> Dict[str, Any]:
        """Check logs directory status"""
        try:
            logs_dir = 'logs'

            if not os.path.exists(logs_dir):
                return {
                    'status': 'warning',
                    'message': 'Logs directory does not exist',
                    'path': os.path.abspath(logs_dir),
                    'last_checked': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
                }

            # Check if writable
            if not os.access(logs_dir, os.W_OK):
                return {
                    'status': 'warning',
                    'message': 'Logs directory is not writable',
                    'path': os.path.abspath(logs_dir),
                    'last_checked': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
                }

            # Get log files info
            log_files = []
            total_size = 0

            for file in os.listdir(logs_dir):
                if file.endswith('.log'):
                    file_path = os.path.join(logs_dir, file)
                    file_size = os.path.getsize(file_path)
                    total_size += file_size

                    log_files.append({
                        'name': file,
                        'size_bytes': file_size,
                        'size_mb': round(file_size / (1024 * 1024), 2),
                        'modified': datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
                    })

            return {
                'status': 'healthy',
                'path': os.path.abspath(logs_dir),
                'writable': True,
                'log_files_count': len(log_files),
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'log_files': log_files,
                'last_checked': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            }

        except Exception as e:
            self.logger.error(f"Logs directory check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'last_checked': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            }

    def get_comprehensive_health(self) -> Dict[str, Any]:
        """Get comprehensive health status of all components"""
        start_time = datetime.utcnow()

        # Check all components
        database_health = self.check_database()
        redis_health = self.check_redis()
        workers_health = self.check_celery_workers()
        disk_health = self.check_disk_space()
        logs_health = self.check_logs_directory()

        # Determine overall status
        overall_status = 'healthy'
        critical_issues = []
        warnings = []

        if database_health['status'] == 'unhealthy':
            overall_status = 'unhealthy'
            critical_issues.append('database')

        if redis_health['status'] == 'unhealthy':
            overall_status = 'unhealthy'
            critical_issues.append('redis')

        if workers_health['status'] == 'unhealthy':
            overall_status = 'unhealthy'
            critical_issues.append('workers')
        elif workers_health['status'] == 'warning':
            warnings.append('workers')

        if disk_health['status'] == 'critical':
            overall_status = 'unhealthy'
            critical_issues.append('disk_space')
        elif disk_health['status'] == 'warning':
            warnings.append('disk_space')

        if logs_health['status'] == 'warning':
            warnings.append('logs')

        # If no critical issues but warnings exist, set to warning
        if overall_status == 'healthy' and warnings:
            overall_status = 'warning'

        # Calculate total response time
        response_time = (datetime.utcnow() - start_time).total_seconds() * 1000

        return {
            'status': overall_status,
            'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
            'response_time_ms': round(response_time, 2),
            'critical_issues': critical_issues,
            'warnings': warnings,
            'components': {
                'database': database_health,
                'redis': redis_health,
                'workers': workers_health,
                'disk_space': disk_health,
                'logs': logs_health,
                'cors': {
                    'status': 'enabled',
                    'config': 'dynamic'
                }
            }
        }

    @staticmethod
    def _mask_db_url(url) -> str:
        """Mask database URL for security"""
        url_str = str(url)
        if '@' in url_str:
            parts = url_str.split('@')
            credentials = parts[0].split('//')[-1]
            if ':' in credentials:
                user, password = credentials.split(':', 1)
                masked_creds = f"{user}:{'*' * len(password)}"
                return url_str.replace(credentials, masked_creds)
        return url_str