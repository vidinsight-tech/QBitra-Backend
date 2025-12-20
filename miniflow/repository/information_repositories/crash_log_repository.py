"""
CrashLog Repository - Hata kayıtları için repository.

Kullanım:
    >>> from miniflow.repository import CrashLogRepository
    >>> crash_repo = CrashLogRepository()
    >>> crashes = crash_repo.get_unresolved_crashes(session)
"""

from __future__ import annotations

from typing import Optional, List
from datetime import datetime, timezone, timedelta

from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from miniflow.database.repository.advanced import AdvancedRepository
from miniflow.models import CrashLog
from miniflow.database.repository.base import handle_db_exceptions



class CrashLogRepository(AdvancedRepository):
    """Hata kayıtları için repository."""
    
    def __init__(self):
        super().__init__(CrashLog)
    
    # =========================================================================
    # LOOKUP METHODS
    # =========================================================================
    
    @handle_db_exceptions
    def get_all_by_severity(
        self, 
        session: Session, 
        severity,
        limit: int = 100, order_by: Optional[str] = "created_at", order_desc: bool = True
    ) -> List[CrashLog]:
        """Önem derecesine göre crash loglarını getirir (liste)."""
        return session.query(self.model).filter(
            self.model.severity == severity
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).limit(limit).all()
    
    @handle_db_exceptions
    def get_all_by_status(
        self, 
        session: Session, 
        status,
        limit: int = 100, order_by: Optional[str] = "created_at", order_desc: bool = True
    ) -> List[CrashLog]:
        """Duruma göre crash loglarını getirir (liste)."""
        return session.query(self.model).filter(
            self.model.status == status
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).limit(limit).all()
    
    @handle_db_exceptions
    def get_all_by_error_type(
        self, 
        session: Session, 
        error_type: str,
        limit: int = 100, order_by: Optional[str] = "created_at", order_desc: bool = True
    ) -> List[CrashLog]:
        """Hata tipine göre crash loglarını getirir (liste)."""
        return session.query(self.model).filter(
            self.model.error_type == error_type
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).limit(limit).all()
    
    @handle_db_exceptions
    def get_all_by_workflow_id(
        self, 
        session: Session, 
        workflow_id: str,
        limit: int = 100, order_by: Optional[str] = "created_at", order_desc: bool = True
    ) -> List[CrashLog]:
        """Workflow ID'ye göre crash loglarını getirir (liste)."""
        return session.query(self.model).filter(
            self.model.workflow_id == workflow_id
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).limit(limit).all()
    
    @handle_db_exceptions
    def count_by_severity(self, session: Session, severity) -> int:
        """Önem derecesine göre crash log sayısını döndürür."""
        return session.query(func.count(self.model.id)).filter(
            self.model.severity == severity
        ).scalar()
    
    @handle_db_exceptions
    def count_unresolved(self, session: Session) -> int:
        """Çözülmemiş crash log sayısını döndürür."""
        return session.query(func.count(self.model.id)).filter(
            self.model.is_resolved == False
        ).scalar()
    
    # =========================================================================
    # UNRESOLVED CRASHES
    # =========================================================================
    
    @handle_db_exceptions
    def get_unresolved_crashes(
        self, 
        session: Session,
        limit: int = 100,
        order_by: Optional[str] = "created_at",
        order_desc: bool = True
    ) -> List[CrashLog]:
        """Çözülmemiş crash loglarını getirir."""
        return session.query(self.model).filter(
            self.model.is_resolved == False
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).limit(limit).all()
    
    @handle_db_exceptions
    def get_critical_crashes(
        self, 
        session: Session,
        limit: int = 100,
        order_by: Optional[str] = "created_at",
        order_desc: bool = True
    ) -> List[CrashLog]:
        """Kritik crash loglarını getirir."""
        from miniflow.models.enums import CrashSeverity
        return session.query(self.model).filter(
            self.model.severity == CrashSeverity.CRITICAL,
            self.model.is_resolved == False
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).limit(limit).all()
    
    # =========================================================================
    # RESOLUTION METHODS
    # =========================================================================
    
    @handle_db_exceptions
    def mark_as_resolved(
        self, 
        session: Session, 
        crash_id: str,
        resolved_by: str,
        resolution_notes: Optional[str] = None,
        fix_version: Optional[str] = None
    ) -> Optional[CrashLog]:
        """Crash log'u çözüldü olarak işaretler."""
        crash = self.get_by_id(session, crash_id)
        if crash:
            crash.is_resolved = True
            crash.resolved_at = datetime.now(timezone.utc)
            crash.resolved_by = resolved_by
            if resolution_notes:
                crash.resolution_notes = resolution_notes
            if fix_version:
                crash.fix_version = fix_version
            session.flush()
        return crash
    
    @handle_db_exceptions
    def update_status(
        self, 
        session: Session, 
        crash_id: str,
        status
    ) -> Optional[CrashLog]:
        """Crash log durumunu günceller."""
        crash = self.get_by_id(session, crash_id)
        if crash:
            crash.status = status
            session.flush()
        return crash
    
    @handle_db_exceptions
    def increment_occurrence(
        self, 
        session: Session, 
        crash_id: str
    ) -> Optional[CrashLog]:
        """Tekrar sayısını artırır."""
        crash = self.get_by_id(session, crash_id)
        if crash:
            crash.occurrence_count = (crash.occurrence_count or 1) + 1
            crash.last_occurred_at = datetime.now(timezone.utc)
            session.flush()
        return crash

