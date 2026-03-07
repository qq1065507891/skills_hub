"""通知服务"""
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional

import httpx

from app.config import get_settings
from app.utils.logger import setup_logger


class NotificationLevel(Enum):
    """通知级别"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Notification:
    """通知数据结构"""

    title: str
    message: str
    level: NotificationLevel = NotificationLevel.INFO
    metadata: Optional[Dict[str, Any]] = None


class NotificationService:
    """通知服务"""

    def __init__(self):
        self.settings = get_settings()
        self.logger = setup_logger(__name__)
        self.enabled = self.settings.NOTIFICATION_ENABLED

    async def send(self, notification):
        """发送通知"""
        if not self.enabled:
            self.logger.debug("通知服务未启用，跳过发送")
            return False

        self.logger.info(
            f"发送通知 - 级别: {notification.level.value}, 标题: {notification.title}"
        )

        success = True

        if self.settings.NOTIFICATION_WEBHOOK_URL:
            webhook_success = await self._send_webhook(notification)
            success = success and webhook_success

        if (
            self.settings.NOTIFICATION_EMAIL_FROM
            and self.settings.NOTIFICATION_EMAIL_TO
        ):
            email_success = await self._send_email(notification)
            success = success and email_success

        self._log_notification(notification)
        return success

    async def _send_webhook(self, notification):
        """发送 Webhook 通知"""
        try:
            payload = {
                "title": notification.title,
                "message": notification.message,
                "level": notification.level.value,
                "metadata": notification.metadata or {},
            }

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    self.settings.NOTIFICATION_WEBHOOK_URL, json=payload
                )
                response.raise_for_status()

            self.logger.debug(f"Webhook 通知发送成功: {notification.title}")
            return True
        except Exception as e:
            self.logger.error(f"Webhook 通知发送失败: {str(e)}")
            return False

    async def _send_email(self, notification):
        """发送邮件通知 (占位实现)"""
        self.logger.warning(f"邮件通知功能尚未完整实现 - 标题: {notification.title}")
        return True

    def _log_notification(self, notification):
        """记录通知日志"""
        log_level = {
            NotificationLevel.INFO: logging.INFO,
            NotificationLevel.WARNING: logging.WARNING,
            NotificationLevel.ERROR: logging.ERROR,
            NotificationLevel.CRITICAL: logging.CRITICAL,
        }.get(notification.level, logging.INFO)

        self.logger.log(log_level, f"[通知] {notification.title}: {notification.message}")

    async def send_info(self, title, message, metadata=None):
        """发送信息通知"""
        return await self.send(
            Notification(
                title=title,
                message=message,
                level=NotificationLevel.INFO,
                metadata=metadata,
            )
        )

    async def send_warning(self, title, message, metadata=None):
        """发送警告通知"""
        return await self.send(
            Notification(
                title=title,
                message=message,
                level=NotificationLevel.WARNING,
                metadata=metadata,
            )
        )

    async def send_error(self, title, message, metadata=None):
        """发送错误通知"""
        return await self.send(
            Notification(
                title=title,
                message=message,
                level=NotificationLevel.ERROR,
                metadata=metadata,
            )
        )

    async def send_critical(self, title, message, metadata=None):
        """发送严重通知"""
        return await self.send(
            Notification(
                title=title,
                message=message,
                level=NotificationLevel.CRITICAL,
                metadata=metadata,
            )
        )


_notification_service = None


def get_notification_service():
    """获取通知服务单例"""
    global _notification_service
    if _notification_service is None:
        _notification_service = NotificationService()
    return _notification_service
