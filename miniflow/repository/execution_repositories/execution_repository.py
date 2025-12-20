"""
Execution Repository - Execution işlemleri için repository.

Kullanım:
    >>> from miniflow.repository import ExecutionRepository
    >>> execution_repo = ExecutionRepository()
    >>> executions = execution_repo.get_all_by_workspace_id(session, "WSP-123")
"""

from __future__ import annotations

from typing import Optional, List

from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from miniflow.database.repository.bulk import BulkRepository
from miniflow.models import Execution
from miniflow.database.repository.base import handle_db_exceptions

from miniflow.models.enums import ExecutionStatuses


class ExecutionRepository(BulkRepository):
    """Execution işlemleri için repository."""
    
    def __init__(self):
        super().__init__(Execution)
    
    # =========================================================================
    # LOOKUP METHODS
    # =========================================================================
    
    @handle_db_exceptions
    def get_all_by_workspace_id(
        self, 
        session: Session, 
        workspace_id: str,
        limit: int = 100, order_by: Optional[str] = "start_time", order_desc: bool = True
    ) -> List[Execution]:
        """Workspace'in execution'larını getirir."""
        return session.query(self.model).filter(
            self.model.workspace_id == workspace_id
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).limit(limit).all()
    
    @handle_db_exceptions
    def get_all_by_workflow_id(
        self, 
        session: Session, 
        workflow_id: str,
        limit: int = 100, order_by: Optional[str] = "start_time", order_desc: bool = True
    ) -> List[Execution]:
        """Workflow'un execution'larını getirir."""
        return session.query(self.model).filter(
            self.model.workflow_id == workflow_id
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).limit(limit).all()
    
    @handle_db_exceptions
    def get_all_by_status(
        self, 
        session: Session, 
        status: ExecutionStatuses,
        workspace_id: Optional[str] = None,
        limit: int = 100, order_by: Optional[str] = "start_time", order_desc: bool = True
    ) -> List[Execution]:
        """Duruma göre execution'ları getirir (liste)."""
        query = session.query(self.model).filter(
            self.model.status == status
        )
        if workspace_id:
            query = query.filter(self.model.workspace_id == workspace_id)
        return query.order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).limit(limit).all()
    
    @handle_db_exceptions
    def count_by_workspace_id(self, session: Session, workspace_id: str) -> int:
        """Execution sayısını döndürür."""
        return session.query(func.count(self.model.id)).filter(
            self.model.workspace_id == workspace_id
        ).scalar()
    
    @handle_db_exceptions
    def count_by_status(
        self, 
        session: Session, 
        status: ExecutionStatuses,
        workspace_id: Optional[str] = None
    ) -> int:
        """Duruma göre execution sayısını döndürür."""
        query = session.query(func.count(self.model.id)).filter(
            self.model.status == status
        )
        if workspace_id:
            query = query.filter(self.model.workspace_id == workspace_id)
        return query.scalar()
    
    # =========================================================================
    # STATUS METHODS
    # =========================================================================
    
    @handle_db_exceptions
    def update_status(
        self, 
        session: Session, 
        execution_id: str, 
        status: ExecutionStatuses
    ) -> Optional[Execution]:
        """Execution durumunu günceller."""
        execution = self.get_by_id(session, execution_id)
        if execution:
            execution.status = status
            session.flush()
        return execution
    
    @handle_db_exceptions
    def get_pending_executions(
        self, 
        session: Session,
        workspace_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Execution]:
        """Bekleyen execution'ları getirir."""
        return self.get_all_by_status(session, ExecutionStatuses.PENDING, workspace_id, limit)
    
    @handle_db_exceptions
    def get_running_executions(
        self, 
        session: Session,
        workspace_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Execution]:
        """Çalışan execution'ları getirir."""
        return self.get_all_by_status(session, ExecutionStatuses.RUNNING, workspace_id, limit)

