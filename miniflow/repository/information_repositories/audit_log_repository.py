"""
AuditLog Repository - Denetim kayıtları için repository.

Kullanım:
    >>> from miniflow.repository import AuditLogRepository
    >>> audit_repo = AuditLogRepository()
    >>> logs = audit_repo.get_all_by_workspace_id(session, "WSP-123")
"""

from __future__ import annotations

from typing import Optional, List
from datetime import datetime, timezone, timedelta

from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from miniflow.database.repository.bulk import BulkRepository
from miniflow.models import AuditLog
from miniflow.database.repository.base import handle_db_exceptions



class AuditLogRepository(BulkRepository):
    """Denetim kayıtları için repository."""
    
    def __init__(self):
        super().__init__(AuditLog)
    
    # =========================================================================
    # LOOKUP METHODS
    # =========================================================================
    
    @handle_db_exceptions
    def get_all_by_workspace_id(
        self, 
        session: Session, 
        workspace_id: str,
        limit: int = 100, order_by: Optional[str] = "created_at", order_desc: bool = True
    ) -> List[AuditLog]:
        """Workspace'in audit loglarını getirir (liste)."""
        return session.query(self.model).filter(
            self.model.workspace_id == workspace_id
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).limit(limit).all()
    
    @handle_db_exceptions
    def get_all_by_user_id(
        self, 
        session: Session, 
        user_id: str,
        limit: int = 100, order_by: Optional[str] = "created_at", order_desc: bool = True
    ) -> List[AuditLog]:
        """Kullanıcının audit loglarını getirir (liste)."""
        return session.query(self.model).filter(
            self.model.user_id == user_id
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).limit(limit).all()
    
    @handle_db_exceptions
    def get_all_by_resource(
        self, 
        session: Session, 
        resource_type: str,
        resource_id: str,
        limit: int = 100, order_by: Optional[str] = "created_at", order_desc: bool = True
    ) -> List[AuditLog]:
        """Kaynak için audit loglarını getirir (liste)."""
        return session.query(self.model).filter(
            self.model.resource_type == resource_type,
            self.model.resource_id == resource_id
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).limit(limit).all()
    
    @handle_db_exceptions
    def get_all_by_action_type(
        self, 
        session: Session, 
        workspace_id: str,
        action_type,
        limit: int = 100, order_by: Optional[str] = "created_at", order_desc: bool = True
    ) -> List[AuditLog]:
        """İşlem tipine göre audit loglarını getirir (liste)."""
        return session.query(self.model).filter(
            self.model.workspace_id == workspace_id,
            self.model.action_type == action_type
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).limit(limit).all()
    
    @handle_db_exceptions
    def count_by_workspace_id(self, session: Session, workspace_id: str) -> int:
        """Audit log sayısını döndürür."""
        return session.query(func.count(self.model.id)).filter(
            self.model.workspace_id == workspace_id
        ).scalar()
    
    # =========================================================================
    # DATE RANGE QUERIES
    # =========================================================================
    
    @handle_db_exceptions
    def get_all_by_date_range(
        self, 
        session: Session, 
        workspace_id: str,
        start_date: datetime,
        end_date: datetime,
        limit: int = 1000, order_by: Optional[str] = "created_at", order_desc: bool = True
    ) -> List[AuditLog]:
        """Tarih aralığına göre audit loglarını getirir (liste)."""
        return session.query(self.model).filter(
            self.model.workspace_id == workspace_id,
            self.model.created_at >= start_date,
            self.model.created_at <= end_date
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).limit(limit).all()
    
    @handle_db_exceptions
    def get_recent_logs(
        self, 
        session: Session, 
        workspace_id: str,
        hours: int = 24,
        limit: int = 100,
        order_by: Optional[str] = "created_at",
        order_desc: bool = True
    ) -> List[AuditLog]:
        """Son X saatin audit loglarını getirir."""
        since = datetime.now(timezone.utc) - timedelta(hours=hours)
        return session.query(self.model).filter(
            self.model.workspace_id == workspace_id,
            self.model.created_at >= since
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).limit(limit).all()
    
    # =========================================================================
    # CLEANUP METHODS
    # =========================================================================
    
    @handle_db_exceptions
    def cleanup_old_logs(
        self, 
        session: Session, 
        days: int = 365
    ) -> int:
        """Eski audit loglarını siler (hard delete)."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        result = session.query(self.model).filter(
            self.model.created_at < cutoff
        ).delete(synchronize_session=False)
        session.flush()
        return result

