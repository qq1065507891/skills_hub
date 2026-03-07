"""Monitor Service"""
import time

import psutil
from sqlalchemy import text

from app.config import get_settings
from app.dependencies.database import SessionLocal
from app.utils.logger import setup_logger


class MonitorService:
    """Monitor Service"""

    def __init__(self):
        self.settings = get_settings()
        self.logger = setup_logger(__name__)
        self.start_time = time.time()

    def get_system_info(self):
        """Get system information"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")
            uptime = time.time() - self.start_time

            return {
                "status": "healthy",
                "uptime_seconds": uptime,
                "uptime_formatted": self._format_uptime(uptime),
                "cpu": {
                    "percent": cpu_percent,
                    "count": psutil.cpu_count(),
                },
                "memory": {
                    "total_mb": memory.total // (1024 * 1024),
                    "used_mb": memory.used // (1024 * 1024),
                    "available_mb": memory.available // (1024 * 1024),
                    "percent": memory.percent,
                },
                "disk": {
                    "total_mb": disk.total // (1024 * 1024),
                    "used_mb": disk.used // (1024 * 1024),
                    "free_mb": disk.free // (1024 * 1024),
                    "percent": disk.percent,
                },
            }
        except Exception as e:
            self.logger.error(f"Failed to get system info: {str(e)}")
            return {"status": "error", "error": str(e)}

    def check_database(self):
        """Check database connection"""
        start_time = time.time()
        try:
            db = SessionLocal()
            db.execute(text("SELECT 1"))
            db.close()
            response_time = (time.time() - start_time) * 1000
            return {
                "status": "healthy",
                "response_time_ms": round(response_time, 2),
            }
        except Exception as e:
            self.logger.error(f"Database check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e),
            }

    def check_redis(self):
        """Check Redis connection"""
        if not self.settings.REDIS_URL:
            return None

        start_time = time.time()
        try:
            import redis

            r = redis.from_url(self.settings.REDIS_URL)
            r.ping()
            response_time = (time.time() - start_time) * 1000
            return {
                "status": "healthy",
                "response_time_ms": round(response_time, 2),
            }
        except Exception as e:
            self.logger.error(f"Redis check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e),
            }

    def get_health_status(self):
        """Get full health status"""
        system_info = self.get_system_info()
        database = self.check_database()
        redis = self.check_redis()

        checks = [system_info["status"] == "healthy", database["status"] == "healthy"]
        if redis:
            checks.append(redis["status"] == "healthy")

        overall_status = "healthy" if all(checks) else "unhealthy"

        return {
            "status": overall_status,
            "app_name": self.settings.APP_NAME,
            "timestamp": time.time(),
            "system": system_info,
            "database": database,
            "redis": redis,
        }

    def _format_uptime(self, seconds):
        """Format uptime"""
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)

        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        parts.append(f"{secs}s")

        return " ".join(parts)


_monitor_service = None


def get_monitor_service():
    """Get monitor service singleton"""
    global _monitor_service
    if _monitor_service is None:
        _monitor_service = MonitorService()
    return _monitor_service
