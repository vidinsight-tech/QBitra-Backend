"""
LoginHistory Repository - Giriş geçmişi için repository.

Kullanım:
    >>> from miniflow.repository import LoginHistoryRepository
    >>> history_repo = LoginHistoryRepository()
    >>> history = history_repo.get_all_by_user_id(session, "USR-123")
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional, List
from datetime import datetime, timezone, timedelta

from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from miniflow.database.repository.advanced import AdvancedRepository
from miniflow.database.repository.base import handle_db_exceptions

if TYPE_CHECKING:
    from miniflow.models import LoginHistory


class LoginHistoryRepository(AdvancedRepository):
    """Giriş geçmişi için repository."""
    
    def __init__(self):
        from miniflow.models import LoginHistory
        super().__init__(LoginHistory)
    
    # =========================================================================
    # LOOKUP METHODS
    # =========================================================================
    
    @handle_db_exceptions
    def get_all_by_user_id(
        self, 
        session: Session, 
        user_id: str,
        limit: int = 100, order_by: Optional[str] = "created_at", order_desc: bool = True
    ) -> List[LoginHistory]:
        """Kullanıcının giriş geçmişini getirir (liste)."""
        return session.query(self.model).filter(
            self.model.user_id == user_id,
            self.model.is_deleted == False
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).limit(limit).all()
    
    # =========================================================================
    # RATE LIMIT METHODS
    # =========================================================================
    
    @handle_db_exceptions
    def check_user_rate_limit(
        self, 
        session: Session, 
        user_id: str,
        max_attempts: int = 5,
        window_minutes: int = 15
    ) -> bool:
        """
        Rate limit aşıldı mı kontrol eder.
        
        Returns:
            True: Rate limit aşıldı
            False: Rate limit aşılmadı
        """
        from miniflow.models.enums import LoginStatus
        window_start = datetime.now(timezone.utc) - timedelta(minutes=window_minutes)
        
        failed_count = session.query(func.count(self.model.id)).filter(
            self.model.user_id == user_id,
            self.model.status == LoginStatus.FAILED,
            self.model.created_at >= window_start,
            self.model.is_deleted == False
        ).scalar()
        
        return failed_count >= max_attempts
    
    @handle_db_exceptions
    def count_recent_lockouts(
        self, 
        session: Session, 
        user_id: str,
        hours: int = 24
    ) -> int:
        """Son kilitleme sayısını hesaplar."""
        window_start = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        from miniflow.models.enums import LoginStatus
        return session.query(func.count(self.model.id)).filter(
            self.model.user_id == user_id,
            self.model.status == LoginStatus.LOCKED,
            self.model.created_at >= window_start,
            self.model.is_deleted == False
        ).scalar()
    
    # =========================================================================
    # CLEANUP METHODS
    # =========================================================================
    
    @handle_db_exceptions
    def cleanup_old_history(
        self, 
        session: Session, 
        days: int = 90
    ) -> int:
        """Eski kayıtları temizler (soft delete)."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        
        result = session.query(self.model).filter(
            self.model.created_at < cutoff,
            self.model.is_deleted == False
        ).update({
            self.model.is_deleted: True,
            self.model.deleted_at: datetime.now(timezone.utc)
        }, synchronize_session=False)
        
        session.flush()
        return result

