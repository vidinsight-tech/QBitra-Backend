"""
WorkspaceRole Repository - Rol yönetimi için repository.

Kullanım:
    >>> from miniflow.repository import WorkspaceRoleRepository
    >>> role_repo = WorkspaceRoleRepository()
    >>> role = role_repo.get_by_name(session, "admin")
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional
from sqlalchemy.orm import Session

from miniflow.database.repository.advanced import AdvancedRepository
from miniflow.database.repository.base import handle_db_exceptions

if TYPE_CHECKING:
    from miniflow.models import WorkspaceRole


class WorkspaceRoleRepository(AdvancedRepository):
    """Rol yönetimi için repository."""
    
    def __init__(self):
        from miniflow.models import WorkspaceRole
        super().__init__(WorkspaceRole)
    
    # =========================================================================
    # LOOKUP METHODS
    # =========================================================================
    
    @handle_db_exceptions
    def get_by_name(self, session: Session, name: str) -> Optional[WorkspaceRole]:
        """Rol adıyla getirir."""
        return session.query(self.model).filter(
            self.model.name == name,
            self.model.is_deleted == False
        ).first()
    
    # =========================================================================
    # PERMISSION CHECK METHODS
    # =========================================================================
    
    @handle_db_exceptions
    def has_permission(self, session: Session, role_id: str, permission: str) -> bool:
        """Rolün belirli bir yetkisi var mı kontrol eder."""
        role = self.get_by_id(session, role_id)
        if role:
            return getattr(role, permission, False)
        return False
    
    # Workspace Permissions
    def can_view_workspace(self, session: Session, role_id: str) -> bool:
        return self.has_permission(session, role_id, "can_view_workspace")
    
    def can_edit_workspace(self, session: Session, role_id: str) -> bool:
        return self.has_permission(session, role_id, "can_edit_workspace")
    
    def can_delete_workspace(self, session: Session, role_id: str) -> bool:
        return self.has_permission(session, role_id, "can_delete_workspace")
    
    def can_invite_members(self, session: Session, role_id: str) -> bool:
        return self.has_permission(session, role_id, "can_invite_members")
    
    def can_remove_members(self, session: Session, role_id: str) -> bool:
        return self.has_permission(session, role_id, "can_remove_members")
    
    def can_change_plan(self, session: Session, role_id: str) -> bool:
        return self.has_permission(session, role_id, "can_change_plan")
    
    # Workflow Permissions
    def can_view_workflows(self, session: Session, role_id: str) -> bool:
        return self.has_permission(session, role_id, "can_view_workflows")
    
    def can_create_workflows(self, session: Session, role_id: str) -> bool:
        return self.has_permission(session, role_id, "can_create_workflows")
    
    def can_edit_workflows(self, session: Session, role_id: str) -> bool:
        return self.has_permission(session, role_id, "can_edit_workflows")
    
    def can_delete_workflows(self, session: Session, role_id: str) -> bool:
        return self.has_permission(session, role_id, "can_delete_workflows")
    
    def can_execute_workflows(self, session: Session, role_id: str) -> bool:
        return self.has_permission(session, role_id, "can_execute_workflows")
    
    def can_share_workflows(self, session: Session, role_id: str) -> bool:
        return self.has_permission(session, role_id, "can_share_workflows")
    
    # Credential Permissions
    def can_view_credentials(self, session: Session, role_id: str) -> bool:
        return self.has_permission(session, role_id, "can_view_credentials")
    
    def can_create_credentials(self, session: Session, role_id: str) -> bool:
        return self.has_permission(session, role_id, "can_create_credentials")
    
    def can_edit_credentials(self, session: Session, role_id: str) -> bool:
        return self.has_permission(session, role_id, "can_edit_credentials")
    
    def can_delete_credentials(self, session: Session, role_id: str) -> bool:
        return self.has_permission(session, role_id, "can_delete_credentials")
    
    def can_share_credentials(self, session: Session, role_id: str) -> bool:
        return self.has_permission(session, role_id, "can_share_credentials")
    
    def can_view_credential_values(self, session: Session, role_id: str) -> bool:
        return self.has_permission(session, role_id, "can_view_credential_values")
    
    # File Permissions
    def can_view_files(self, session: Session, role_id: str) -> bool:
        return self.has_permission(session, role_id, "can_view_files")
    
    def can_upload_files(self, session: Session, role_id: str) -> bool:
        return self.has_permission(session, role_id, "can_upload_files")
    
    def can_download_files(self, session: Session, role_id: str) -> bool:
        return self.has_permission(session, role_id, "can_download_files")
    
    def can_delete_files(self, session: Session, role_id: str) -> bool:
        return self.has_permission(session, role_id, "can_delete_files")
    
    def can_share_files(self, session: Session, role_id: str) -> bool:
        return self.has_permission(session, role_id, "can_share_files")
    
    # Database Permissions
    def can_view_databases(self, session: Session, role_id: str) -> bool:
        return self.has_permission(session, role_id, "can_view_databases")
    
    def can_create_databases(self, session: Session, role_id: str) -> bool:
        return self.has_permission(session, role_id, "can_create_databases")
    
    def can_edit_databases(self, session: Session, role_id: str) -> bool:
        return self.has_permission(session, role_id, "can_edit_databases")
    
    def can_delete_databases(self, session: Session, role_id: str) -> bool:
        return self.has_permission(session, role_id, "can_delete_databases")
    
    def can_share_databases(self, session: Session, role_id: str) -> bool:
        return self.has_permission(session, role_id, "can_share_databases")
    
    def can_view_connection_details(self, session: Session, role_id: str) -> bool:
        return self.has_permission(session, role_id, "can_view_connection_details")
    
    # Variable Permissions
    def can_view_variables(self, session: Session, role_id: str) -> bool:
        return self.has_permission(session, role_id, "can_view_variables")
    
    def can_create_variables(self, session: Session, role_id: str) -> bool:
        return self.has_permission(session, role_id, "can_create_variables")
    
    def can_edit_variables(self, session: Session, role_id: str) -> bool:
        return self.has_permission(session, role_id, "can_edit_variables")
    
    def can_delete_variables(self, session: Session, role_id: str) -> bool:
        return self.has_permission(session, role_id, "can_delete_variables")
    
    def can_share_variables(self, session: Session, role_id: str) -> bool:
        return self.has_permission(session, role_id, "can_share_variables")
    
    def can_view_variable_values(self, session: Session, role_id: str) -> bool:
        return self.has_permission(session, role_id, "can_view_variable_values")
    
    # API Key Permissions
    def can_create_api_keys(self, session: Session, role_id: str) -> bool:
        return self.has_permission(session, role_id, "can_create_api_keys")
    
    def can_view_api_keys(self, session: Session, role_id: str) -> bool:
        return self.has_permission(session, role_id, "can_view_api_keys")
    
    def can_edit_api_keys(self, session: Session, role_id: str) -> bool:
        return self.has_permission(session, role_id, "can_edit_api_keys")
    
    def can_delete_api_keys(self, session: Session, role_id: str) -> bool:
        return self.has_permission(session, role_id, "can_delete_api_keys")
    
    def can_share_api_keys(self, session: Session, role_id: str) -> bool:
        return self.has_permission(session, role_id, "can_share_api_keys")
    
    def can_view_api_key_values(self, session: Session, role_id: str) -> bool:
        return self.has_permission(session, role_id, "can_view_api_key_values")

