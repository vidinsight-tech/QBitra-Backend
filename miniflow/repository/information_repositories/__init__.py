"""Information Repositories - Bilgi modelleri için repository'ler."""

from .audit_log_repository import AuditLogRepository
from .crash_log_repository import CrashLogRepository
from .system_setting_repository import SystemSettingRepository

__all__ = [
    "AuditLogRepository",
    "CrashLogRepository",
    "SystemSettingRepository",
]

