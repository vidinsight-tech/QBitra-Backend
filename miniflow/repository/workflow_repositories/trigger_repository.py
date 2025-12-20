"""
Trigger Repository - Trigger işlemleri için repository.

Kullanım:
    >>> from miniflow.repository import TriggerRepository
    >>> trigger_repo = TriggerRepository()
    >>> triggers = trigger_repo.get_all_by_workflow_id(session, "WF-123")
"""

from __future__ import annotations

from typing import Optional, List
from datetime import datetime, timezone

from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from miniflow.database.repository.advanced import AdvancedRepository
from miniflow.models import Trigger
from miniflow.database.repository.base import handle_db_exceptions



class TriggerRepository(AdvancedRepository):
    """Trigger işlemleri için repository."""
    
    def __init__(self):
        super().__init__(Trigger)
    
    # =========================================================================
    # LOOKUP METHODS
    # =========================================================================
    
    @handle_db_exceptions
    def get_by_name(
        self, 
        session: Session, 
        workflow_id: str, 
        name: str
    ) -> Optional[Trigger]:
        """İsim ile trigger getirir."""
        return session.query(self.model).filter(
            self.model.workflow_id == workflow_id,
            self.model.name == name,
            self.model.is_deleted == False
        ).first()
    
    @handle_db_exceptions
    def get_all_by_workflow_id(
        self, 
        session: Session, 
        workflow_id: str, order_by: Optional[str] = "created_at", order_desc: bool = True
    ) -> List[Trigger]:
        """Workflow'un trigger'larını getirir."""
        return session.query(self.model).filter(
            self.model.workflow_id == workflow_id,
            self.model.is_deleted == False
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).all()
    
    @handle_db_exceptions
    def count_by_workflow_id(self, session: Session, workflow_id: str) -> int:
        """Workflow'daki trigger sayısını döndürür."""
        return session.query(func.count(self.model.id)).filter(
            self.model.workflow_id == workflow_id,
            self.model.is_deleted == False
        ).scalar()
    
    @handle_db_exceptions
    def get_enabled_triggers(
        self, 
        session: Session, 
        workflow_id: Optional[str] = None
    ) -> List[Trigger]:
        """Aktif trigger'ları getirir."""
        query = session.query(self.model).filter(
            self.model.is_active == True,
            self.model.is_deleted == False
        )
        if workflow_id:
            query = query.filter(self.model.workflow_id == workflow_id)
        return query.all()
    
    @handle_db_exceptions
    def get_all_active_by_workflow_id(
        self, 
        session: Session, 
        workflow_id: str, order_by: Optional[str] = "created_at", order_desc: bool = True
    ) -> List[Trigger]:
        """Workflow'un aktif trigger'larını getirir."""
        return session.query(self.model).filter(
            self.model.workflow_id == workflow_id,
            self.model.is_active == True,
            self.model.is_deleted == False
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).all()
    
    @handle_db_exceptions
    def get_all_by_type(
        self, 
        session: Session, 
        workflow_id: str, 
        trigger_type: str, order_by: Optional[str] = "created_at", order_desc: bool = True
    ) -> List[Trigger]:
        """Tipe göre trigger'ları getirir (liste)."""
        return session.query(self.model).filter(
            self.model.workflow_id == workflow_id,
            self.model.trigger_type == trigger_type,
            self.model.is_deleted == False
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).all()
    
    # =========================================================================
    # DELETE METHODS
    # =========================================================================
    
    @handle_db_exceptions
    def delete_all_by_workflow_id(self, session: Session, workflow_id: str) -> int:
        """Workflow'un tüm trigger'larını siler (soft delete)."""
        now = datetime.now(timezone.utc)
        result = session.query(self.model).filter(
            self.model.workflow_id == workflow_id,
            self.model.is_deleted == False
        ).update({
            self.model.is_deleted: True,
            self.model.deleted_at: now
        }, synchronize_session=False)
        session.flush()
        return result

