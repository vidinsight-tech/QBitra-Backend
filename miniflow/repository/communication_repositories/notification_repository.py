"""
Notification Repository - Bildirim işlemleri için repository.

Kullanım:
    >>> from miniflow.repository import NotificationRepository
    >>> notification_repo = NotificationRepository()
    >>> notifications = notification_repo.get_all_by_user_id(session, "USR-123")
"""

from __future__ import annotations

from typing import Optional, List
from datetime import datetime, timezone

from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from miniflow.database.repository.advanced import AdvancedRepository
from miniflow.models import Notification
from miniflow.database.repository.base import handle_db_exceptions



class NotificationRepository(AdvancedRepository):
    """Bildirim işlemleri için repository."""
    
    def __init__(self):
        super().__init__(Notification)
    
    # =========================================================================
    # LOOKUP METHODS
    # =========================================================================
    
    @handle_db_exceptions
    def get_all_by_user_id(
        self, 
        session: Session, 
        user_id: str,
        limit: int = 100, order_by: Optional[str] = "sent_at", order_desc: bool = True
    ) -> List[Notification]:
        """Kullanıcının bildirimlerini getirir (liste)."""
        return session.query(self.model).filter(
            self.model.user_id == user_id
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).limit(limit).all()
    
    @handle_db_exceptions
    def get_unread_by_user_id(
        self, 
        session: Session, 
        user_id: str,
        limit: int = 100, order_by: Optional[str] = "sent_at", order_desc: bool = True
    ) -> List[Notification]:
        """Kullanıcının okunmamış bildirimlerini getirir (liste)."""
        return session.query(self.model).filter(
            self.model.user_id == user_id,
            self.model.is_read == False
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).limit(limit).all()
    
    @handle_db_exceptions
    def count_by_user_id(self, session: Session, user_id: str) -> int:
        """Kullanıcının bildirim sayısını döndürür."""
        return session.query(func.count(self.model.id)).filter(
            self.model.user_id == user_id
        ).scalar()
    
    @handle_db_exceptions
    def count_unread_by_user_id(self, session: Session, user_id: str) -> int:
        """Kullanıcının okunmamış bildirim sayısını döndürür."""
        return session.query(func.count(self.model.id)).filter(
            self.model.user_id == user_id,
            self.model.is_read == False
        ).scalar()
    
    # =========================================================================
    # READ STATUS METHODS
    # =========================================================================
    
    @handle_db_exceptions
    def mark_as_read(
        self, 
        session: Session, 
        notification_id: str
    ) -> Optional[Notification]:
        """Bildirimi okundu olarak işaretler."""
        notification = self.get_by_id(session, notification_id)
        if notification and not notification.is_read:
            notification.is_read = True
            notification.read_at = datetime.now(timezone.utc)
            session.flush()
        return notification
    
    @handle_db_exceptions
    def mark_all_as_read(self, session: Session, user_id: str) -> int:
        """Kullanıcının tüm bildirimlerini okundu olarak işaretler."""
        now = datetime.now(timezone.utc)
        result = session.query(self.model).filter(
            self.model.user_id == user_id,
            self.model.is_read == False
        ).update({
            self.model.is_read: True,
            self.model.read_at: now
        }, synchronize_session=False)
        session.flush()
        return result
    
    # =========================================================================
    # DELETE METHODS
    # =========================================================================
    
    @handle_db_exceptions
    def delete_all_by_user_id(self, session: Session, user_id: str) -> int:
        """Kullanıcının tüm bildirimlerini siler (hard delete)."""
        result = session.query(self.model).filter(
            self.model.user_id == user_id
        ).delete(synchronize_session=False)
        session.flush()
        return result
    
    @handle_db_exceptions
    def delete_read_notifications(
        self, 
        session: Session, 
        user_id: str
    ) -> int:
        """Kullanıcının okunmuş bildirimlerini siler."""
        result = session.query(self.model).filter(
            self.model.user_id == user_id,
            self.model.is_read == True
        ).delete(synchronize_session=False)
        session.flush()
        return result

