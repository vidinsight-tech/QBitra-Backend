"""
Node Repository - Node işlemleri için repository.

Kullanım:
    >>> from miniflow.repository import NodeRepository
    >>> node_repo = NodeRepository()
    >>> nodes = node_repo.get_all_by_workflow_id(session, "WF-123")
"""

from __future__ import annotations

from typing import Optional, List
from datetime import datetime, timezone

from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from miniflow.database.repository.advanced import AdvancedRepository
from miniflow.models import Node
from miniflow.database.repository.base import handle_db_exceptions



class NodeRepository(AdvancedRepository):
    """Node işlemleri için repository."""
    
    def __init__(self):
        super().__init__(Node)
    
    # =========================================================================
    # LOOKUP METHODS
    # =========================================================================
    
    @handle_db_exceptions
    def get_by_name(
        self, 
        session: Session, 
        workflow_id: str, 
        name: str
    ) -> Optional[Node]:
        """İsim ile node getirir."""
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
    ) -> List[Node]:
        """Workflow'un tüm node'larını getirir."""
        return session.query(self.model).filter(
            self.model.workflow_id == workflow_id,
            self.model.is_deleted == False
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).all()
    
    @handle_db_exceptions
    def count_by_workflow_id(self, session: Session, workflow_id: str) -> int:
        """Node sayısını döndürür."""
        return session.query(func.count(self.model.id)).filter(
            self.model.workflow_id == workflow_id,
            self.model.is_deleted == False
        ).scalar()
    
    @handle_db_exceptions
    def get_all_by_script_id(
        self, 
        session: Session, 
        script_id: str, order_by: Optional[str] = "created_at", order_desc: bool = True
    ) -> List[Node]:
        """Global script kullanan node'ları getirir (liste)."""
        return session.query(self.model).filter(
            self.model.script_id == script_id,
            self.model.is_deleted == False
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).all()
    
    @handle_db_exceptions
    def get_all_by_custom_script_id(
        self, 
        session: Session, 
        custom_script_id: str, order_by: Optional[str] = "created_at", order_desc: bool = True
    ) -> List[Node]:
        """Custom script kullanan node'ları getirir (liste)."""
        return session.query(self.model).filter(
            self.model.custom_script_id == custom_script_id,
            self.model.is_deleted == False
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).all()
    
    # =========================================================================
    # DELETE METHODS
    # =========================================================================
    
    @handle_db_exceptions
    def delete_all_by_workflow_id(self, session: Session, workflow_id: str) -> int:
        """Workflow'un tüm node'larını siler (soft delete)."""
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

