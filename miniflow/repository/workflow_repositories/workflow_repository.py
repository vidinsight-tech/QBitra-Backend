"""
Workflow Repository - Workflow işlemleri için repository.

Kullanım:
    >>> from miniflow.repository import WorkflowRepository
    >>> workflow_repo = WorkflowRepository()
    >>> workflow = workflow_repo.get_by_name(session, "WSP-123", "my-workflow")
"""

from __future__ import annotations

from typing import Optional, List

from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from miniflow.database.repository.bulk import BulkRepository
from miniflow.models import Workflow
from miniflow.database.repository.base import handle_db_exceptions



class WorkflowRepository(BulkRepository):
    """Workflow işlemleri için repository."""
    
    def __init__(self):
        super().__init__(Workflow)
    
    # =========================================================================
    # LOOKUP METHODS
    # =========================================================================
    
    @handle_db_exceptions
    def get_by_name(
        self, 
        session: Session, 
        workspace_id: str, 
        name: str
    ) -> Optional[Workflow]:
        """İsim ile workflow getirir."""
        return session.query(self.model).filter(
            self.model.workspace_id == workspace_id,
            self.model.name == name,
            self.model.is_deleted == False
        ).first()
    
    @handle_db_exceptions
    def get_all_by_workspace_id(
        self, 
        session: Session, 
        workspace_id: str, order_by: Optional[str] = "created_at", order_desc: bool = True
    ) -> List[Workflow]:
        """Workspace'in workflow'larını getirir."""
        return session.query(self.model).filter(
            self.model.workspace_id == workspace_id,
            self.model.is_deleted == False
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).all()
    
    @handle_db_exceptions
    def count_by_workspace_id(self, session: Session, workspace_id: str) -> int:
        """Workflow sayısını döndürür."""
        return session.query(func.count(self.model.id)).filter(
            self.model.workspace_id == workspace_id,
            self.model.is_deleted == False
        ).scalar()
    
    @handle_db_exceptions
    def get_all_by_status(
        self, 
        session: Session, 
        workspace_id: str, 
        status: str, order_by: Optional[str] = "created_at", order_desc: bool = True
    ) -> List[Workflow]:
        """Duruma göre workflow'ları getirir (liste)."""
        return session.query(self.model).filter(
            self.model.workspace_id == workspace_id,
            self.model.status == status,
            self.model.is_deleted == False
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).all()
    
    @handle_db_exceptions
    def get_active_workflows(
        self, 
        session: Session, 
        workspace_id: str,
        order_by: Optional[str] = "created_at",
        order_desc: bool = True
    ) -> List[Workflow]:
        """Aktif workflow'ları getirir."""
        return session.query(self.model).filter(
            self.model.workspace_id == workspace_id,
            self.model.is_active == True,
            self.model.is_deleted == False
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).all()
    
    # =========================================================================
    # UPDATE METHODS
    # =========================================================================
    
    @handle_db_exceptions
    def update_status(
        self, 
        session: Session, 
        workflow_id: str, 
        status: str
    ) -> Optional[Workflow]:
        """Workflow durumunu günceller."""
        workflow = self.get_by_id(session, workflow_id)
        if workflow:
            workflow.status = status
            session.flush()
        return workflow

