from flask import Blueprint, request
from datetime import datetime
from .checks import HealthChecker
from .system_info import SystemInfo

health_bp = Blueprint('health', __name__)
health_checker = HealthChecker()
system_info = SystemInfo()


@health_bp.route('/health')
def health_check():
    """Comprehensive health check with real-time status"""

    # Get comprehensive health status
    health_data = health_checker.get_comprehensive_health()

    # Add system information
    health_data.update({
        'version': system_info.get_version(),
        'system': system_info.get_system_info(),
        'build': system_info.get_build_info(),
        'request_info': {
            'method': request.method,
            'user_agent': request.headers.get('User-Agent', 'unknown'),
            'remote_addr': request.remote_addr,
            'endpoint': request.endpoint
        }
    })

    # Return appropriate HTTP status code
    status_code = (
        200 if health_data['status'] == 'healthy'
        else 503 if health_data['status'] == 'unhealthy'
        else 200  # warning
    )

    return health_data, status_code


@health_bp.route('/health/database')
def health_database():
    """Database-specific health check"""
    health = health_checker.check_database()
    status_code = 200 if health['status'] == 'healthy' else 503
    return health, status_code


@health_bp.route('/health/redis')
def health_redis():
    """Redis-specific health check"""
    health = health_checker.check_redis()
    status_code = 200 if health['status'] == 'healthy' else 503
    return health, status_code


@health_bp.route('/health/workers')
def health_workers():
    """Celery workers health check"""
    health = health_checker.check_celery_workers()
    status_code = 200 if health['status'] in ['healthy', 'warning'] else 503
    return health, status_code


@health_bp.route('/health/disk')
def health_disk():
    """Disk space health check"""
    health = health_checker.check_disk_space()
    status_code = 200 if health['status'] in ['healthy', 'warning'] else 503
    return health, status_code


@health_bp.route('/health/logs')
def health_logs():
    """Logs directory health check"""
    health = health_checker.check_logs_directory()
    status_code = 200 if health['status'] in ['healthy', 'warning'] else 503
    return health, status_code


@health_bp.route('/version')
def version_info():
    """Get version information"""
    return {
        'version': system_info.get_version(),
        'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
        'system': system_info.get_system_info(),
        'build': system_info.get_build_info()
    }


@health_bp.route('/api/cors-test')
def cors_test():
    """Test endpoint to verify CORS is working"""
    return {
        'message': 'CORS is working correctly',
        'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
        'cors_enabled': True,
        'origin': request.headers.get('Origin', 'none'),
        'user_agent': request.headers.get('User-Agent', 'unknown'),
        'system': system_info.get_system_info()
    }