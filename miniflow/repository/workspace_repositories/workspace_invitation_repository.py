"""
WorkspaceInvitation Repository - Davet yönetimi için repository.

Kullanım:
    >>> from miniflow.repository import WorkspaceInvitationRepository
    >>> invitation_repo = WorkspaceInvitationRepository()
    >>> invitation = invitation_repo.get_pending_by_user_id(session, "USR-123")
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional, List
from datetime import datetime, timezone

from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from miniflow.database.repository.advanced import AdvancedRepository
from miniflow.database.repository.base import handle_db_exceptions

if TYPE_CHECKING:
    from miniflow.models import WorkspaceInvitation


class WorkspaceInvitationRepository(AdvancedRepository):
    """Davet yönetimi için repository."""
    
    def __init__(self):
        from miniflow.models import WorkspaceInvitation
        super().__init__(WorkspaceInvitation)
    
    # =========================================================================
    # LOOKUP METHODS
    # =========================================================================
    
    @handle_db_exceptions
    def get_pending_by_user_id(
        self, 
        session: Session, 
        user_id: str
    ) -> List[WorkspaceInvitation]:
        """Kullanıcının bekleyen davetlerini getirir."""
        return session.query(self.model).filter(
            self.model.invitee_id == user_id,
            self.model.status == "pending",
            self.model.is_deleted == False
        ).all()
    
    @handle_db_exceptions
    def get_by_workspace_id_and_user_id(
        self, 
        session: Session, 
        workspace_id: str, 
        user_id: str
    ) -> Optional[WorkspaceInvitation]:
        """Workspace ve kullanıcı ile davet getirir."""
        return session.query(self.model).filter(
            self.model.workspace_id == workspace_id,
            self.model.invitee_id == user_id,
            self.model.is_deleted == False
        ).first()
    
    @handle_db_exceptions
    def get_all_by_workspace_id(
        self, 
        session: Session, 
        workspace_id: str, order_by: Optional[str] = "created_at", order_desc: bool = True
    ) -> List[WorkspaceInvitation]:
        """Workspace'in tüm davetlerini getirir."""
        return session.query(self.model).filter(
            self.model.workspace_id == workspace_id,
            self.model.is_deleted == False
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).all()
    
    @handle_db_exceptions
    def get_pending_by_workspace_id(
        self, 
        session: Session, 
        workspace_id: str,
        order_by: Optional[str] = "created_at",
        order_desc: bool = True
    ) -> List[WorkspaceInvitation]:
        """Workspace'in bekleyen davetlerini getirir."""
        return session.query(self.model).filter(
            self.model.workspace_id == workspace_id,
            self.model.status == "pending",
            self.model.is_deleted == False
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).all()
    
    @handle_db_exceptions
    def count_pending_by_workspace_id(self, session: Session, workspace_id: str) -> int:
        """Bekleyen davet sayısını döndürür."""
        return session.query(func.count(self.model.id)).filter(
            self.model.workspace_id == workspace_id,
            self.model.status == "pending",
            self.model.is_deleted == False
        ).scalar()
    
    # =========================================================================
    # DELETE METHODS
    # =========================================================================
    
    @handle_db_exceptions
    def delete_all_by_workspace_id(self, session: Session, workspace_id: str) -> int:
        """Workspace'in tüm davetlerini siler (soft delete)."""
        now = datetime.now(timezone.utc)
        result = session.query(self.model).filter(
            self.model.workspace_id == workspace_id,
            self.model.is_deleted == False
        ).update({
            self.model.is_deleted: True,
            self.model.deleted_at: now
        }, synchronize_session=False)
        session.flush()
        return result

