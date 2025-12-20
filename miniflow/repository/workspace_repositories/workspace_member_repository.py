"""
WorkspaceMember Repository - Üyelik yönetimi için repository.

Kullanım:
    >>> from miniflow.repository import WorkspaceMemberRepository
    >>> member_repo = WorkspaceMemberRepository()
    >>> member = member_repo.get_by_workspace_id_and_user_id(session, "WSP-123", "USR-456")
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional, List
from datetime import datetime, timezone

from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from miniflow.database.repository.advanced import AdvancedRepository
from miniflow.database.repository.base import handle_db_exceptions

if TYPE_CHECKING:
    from miniflow.models import WorkspaceMember


class WorkspaceMemberRepository(AdvancedRepository):
    """Üyelik yönetimi için repository."""
    
    def __init__(self):
        from miniflow.models import WorkspaceMember
        super().__init__(WorkspaceMember)
    
    # =========================================================================
    # LOOKUP METHODS
    # =========================================================================
    
    @handle_db_exceptions
    def get_by_workspace_id_and_user_id(
        self, 
        session: Session, 
        workspace_id: str, 
        user_id: str
    ) -> Optional[WorkspaceMember]:
        """Workspace ve kullanıcı ID'si ile üye getirir."""
        return session.query(self.model).filter(
            self.model.workspace_id == workspace_id,
            self.model.user_id == user_id,
            self.model.is_deleted == False
        ).first()
    
    @handle_db_exceptions
    def get_all_by_workspace_id(
        self, 
        session: Session, 
        workspace_id: str,
        order_by: Optional[str] = "created_at",
        order_desc: bool = True
    ) -> List[WorkspaceMember]:
        """Workspace'in tüm üyelerini getirir."""
        return session.query(self.model).filter(
            self.model.workspace_id == workspace_id,
            self.model.is_deleted == False
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).all()
    
    @handle_db_exceptions
    def get_owned_workspaces_by_user_id(
        self, 
        session: Session, 
        user_id: str
    ) -> List[WorkspaceMember]:
        """Kullanıcının sahip olduğu workspace'leri getirir."""
        return session.query(self.model).filter(
            self.model.user_id == user_id,
            self.model.is_owner == True,
            self.model.is_deleted == False
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).all()
    
    @handle_db_exceptions
    def get_memberships_by_user_id(
        self, 
        session: Session, 
        user_id: str
    ) -> List[WorkspaceMember]:
        """Kullanıcının üyeliklerini getirir (owner hariç)."""
        return session.query(self.model).filter(
            self.model.user_id == user_id,
            self.model.is_owner == False,
            self.model.is_deleted == False
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).all()
    
    @handle_db_exceptions
    def get_all_by_user_id(
        self, 
        session: Session, 
        user_id: str, order_by: Optional[str] = "created_at", order_desc: bool = True
    ) -> List[WorkspaceMember]:
        """Kullanıcının tüm üyeliklerini getirir."""
        return session.query(self.model).filter(
            self.model.user_id == user_id,
            self.model.is_deleted == False
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).all()
    
    @handle_db_exceptions
    def count_by_role_id(self, session: Session, role_id: str) -> int:
        """Role göre üye sayısını döndürür."""
        return session.query(func.count(self.model.id)).filter(
            self.model.role_id == role_id,
            self.model.is_deleted == False
        ).scalar()
    
    @handle_db_exceptions
    def count_by_workspace_id(self, session: Session, workspace_id: str) -> int:
        """Workspace'deki üye sayısını döndürür."""
        return session.query(func.count(self.model.id)).filter(
            self.model.workspace_id == workspace_id,
            self.model.is_deleted == False
        ).scalar()
    
    # =========================================================================
    # UPDATE METHODS
    # =========================================================================
    
    @handle_db_exceptions
    def update_last_accessed(
        self, 
        session: Session, 
        workspace_id: str, 
        user_id: str
    ) -> Optional[WorkspaceMember]:
        """Son erişim zamanını günceller."""
        member = self.get_by_workspace_id_and_user_id(session, workspace_id, user_id)
        if member:
            member.last_accessed_at = datetime.now(timezone.utc)
            session.flush()
        return member
    
    @handle_db_exceptions
    def update_role(
        self, 
        session: Session, 
        workspace_id: str, 
        user_id: str, 
        role_id: str
    ) -> Optional[WorkspaceMember]:
        """Üyenin rolünü günceller."""
        member = self.get_by_workspace_id_and_user_id(session, workspace_id, user_id)
        if member:
            member.role_id = role_id
            session.flush()
        return member
    
    # =========================================================================
    # DELETE METHODS
    # =========================================================================
    
    @handle_db_exceptions
    def delete_all_by_workspace_id(self, session: Session, workspace_id: str) -> int:
        """Workspace'in tüm üyelerini siler (soft delete)."""
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

