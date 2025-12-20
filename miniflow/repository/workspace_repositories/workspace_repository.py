"""
Workspace Repository - Workspace işlemleri için repository.

Kullanım:
    >>> from miniflow.repository import WorkspaceRepository
    >>> workspace_repo = WorkspaceRepository()
    >>> workspace = workspace_repo.get_by_slug(session, "my-workspace")
"""

from __future__ import annotations

from typing import Optional, List
from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from miniflow.database.repository.bulk import BulkRepository
from miniflow.models import Workspace
from miniflow.database.repository.base import handle_db_exceptions



class WorkspaceRepository(BulkRepository):
    """Workspace işlemleri için repository."""
    
    def __init__(self):
        super().__init__(Workspace)
    
    # =========================================================================
    # LOOKUP METHODS
    # =========================================================================
    
    @handle_db_exceptions
    def get_by_slug(self, session: Session, slug: str) -> Optional[Workspace]:
        """Slug ile workspace getirir."""
        return session.query(self.model).filter(
            self.model.slug == slug,
            self.model.is_deleted == False
        ).first()
    
    @handle_db_exceptions
    def get_by_name(self, session: Session, name: str) -> Optional[Workspace]:
        """İsim ile workspace getirir."""
        return session.query(self.model).filter(
            self.model.name == name,
            self.model.is_deleted == False
        ).first()
    
    @handle_db_exceptions
    def get_by_owner_id(self, session: Session, owner_id: str) -> List[Workspace]:
        """Sahibin workspace'lerini getirir."""
        return session.query(self.model).filter(
            self.model.owner_id == owner_id,
            self.model.is_deleted == False
        ).all()
    
    @handle_db_exceptions
    def count_by_plan_id(self, session: Session, plan_id: str) -> int:
        """Plana göre workspace sayısını döndürür."""
        return session.query(func.count(self.model.id)).filter(
            self.model.plan_id == plan_id,
            self.model.is_deleted == False
        ).scalar()
    
    # =========================================================================
    # COUNT MANAGEMENT (ATOMIC)
    # =========================================================================
    
    @handle_db_exceptions
    def increment_member_count(self, session: Session, workspace_id: str) -> Optional[Workspace]:
        """Üye sayısını artırır."""
        return self.increment(session, workspace_id, "current_member_count")
    
    @handle_db_exceptions
    def decrement_member_count(self, session: Session, workspace_id: str) -> Optional[Workspace]:
        """Üye sayısını azaltır."""
        return self.decrement(session, workspace_id, "current_member_count")
    
    @handle_db_exceptions
    def increment_workflow_count(self, session: Session, workspace_id: str) -> Optional[Workspace]:
        """Workflow sayısını artırır."""
        return self.increment(session, workspace_id, "current_workflow_count")
    
    @handle_db_exceptions
    def decrement_workflow_count(self, session: Session, workspace_id: str) -> Optional[Workspace]:
        """Workflow sayısını azaltır."""
        return self.decrement(session, workspace_id, "current_workflow_count")
    
    @handle_db_exceptions
    def increment_execution_count(self, session: Session, workspace_id: str) -> Optional[Workspace]:
        """Aylık execution sayısını artırır."""
        return self.increment(session, workspace_id, "current_month_executions")
    
    @handle_db_exceptions
    def increment_storage(self, session: Session, workspace_id: str, mb: float) -> Optional[Workspace]:
        """Depolama kullanımını artırır."""
        workspace = self.get_by_id(session, workspace_id)
        if workspace:
            workspace.current_storage_mb = (workspace.current_storage_mb or 0) + mb
            session.flush()
        return workspace
    
    @handle_db_exceptions
    def decrement_storage(self, session: Session, workspace_id: str, mb: float) -> Optional[Workspace]:
        """Depolama kullanımını azaltır."""
        workspace = self.get_by_id(session, workspace_id)
        if workspace:
            workspace.current_storage_mb = max(0, (workspace.current_storage_mb or 0) - mb)
            session.flush()
        return workspace
    
    # =========================================================================
    # SUSPENSION MANAGEMENT
    # =========================================================================
    
    @handle_db_exceptions
    def suspend_workspace(self, session: Session, workspace_id: str, reason: str) -> Optional[Workspace]:
        """Workspace'i askıya alır."""
        workspace = self.get_by_id(session, workspace_id)
        if workspace:
            workspace.is_suspended = True
            workspace.suspension_reason = reason
            workspace.suspended_at = datetime.now(timezone.utc)
            session.flush()
        return workspace
    
    @handle_db_exceptions
    def unsuspend_workspace(self, session: Session, workspace_id: str) -> Optional[Workspace]:
        """Askıyı kaldırır."""
        workspace = self.get_by_id(session, workspace_id)
        if workspace:
            workspace.is_suspended = False
            workspace.suspension_reason = None
            workspace.suspended_at = None
            session.flush()
        return workspace
    
    # =========================================================================
    # RESET METHODS
    # =========================================================================
    
    @handle_db_exceptions
    def reset_monthly_counters(self, session: Session, workspace_id: str) -> Optional[Workspace]:
        """Aylık sayaçları sıfırlar."""
        workspace = self.get_by_id(session, workspace_id)
        if workspace:
            workspace.current_month_executions = 0
            session.flush()
        return workspace

