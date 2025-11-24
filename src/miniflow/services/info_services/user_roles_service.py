from typing import Optional, Dict, List, Any

from src.miniflow.database import RepositoryRegistry, with_transaction, with_readonly_session
from src.miniflow.database.utils.pagination_params import PaginationParams
from src.miniflow.core.exceptions import (
    ResourceNotFoundError,
    ResourceAlreadyExistsError,
    InvalidInputError,
)


class UserRolesService:

    def __init__(self):
        self._registry = RepositoryRegistry()
        self._user_roles_repository = self._registry.user_roles_repository
        self._workspace_member_repo = self._registry.workspace_member_repository

    @with_transaction(manager=None)
    def create_role(
        self,
        session,
        *,
        name: str,
        description: Optional[str] = None,
        is_system_role: bool = False,
        display_order: int = 0,
        created_by: str,
        # Workspace permissions
        can_view_workspace: bool = True,
        can_edit_workspace: bool = False,
        can_delete_workspace: bool = False,
        can_invite_members: bool = False,
        can_remove_members: bool = False,
        can_change_plan: bool = False,
        # Workflow permissions
        can_view_workflows: bool = True,
        can_create_workflows: bool = False,
        can_edit_workflows: bool = False,
        can_delete_workflows: bool = False,
        can_execute_workflows: bool = True,
        can_share_workflows: bool = False,
        # Credential permissions
        can_view_credentials: bool = True,
        can_create_credentials: bool = False,
        can_edit_credentials: bool = False,
        can_delete_credentials: bool = False,
        can_share_credentials: bool = False,
        can_view_credential_values: bool = False,
        # File permissions
        can_view_files: bool = True,
        can_upload_files: bool = False,
        can_download_files: bool = True,
        can_delete_files: bool = False,
        can_share_files: bool = False,
        # Database permissions
        can_view_databases: bool = True,
        can_create_databases: bool = False,
        can_edit_databases: bool = False,
        can_delete_databases: bool = False,
        can_share_databases: bool = False,
        can_view_connection_details: bool = False,
        # Variable permissions
        can_view_variables: bool = True,
        can_create_variables: bool = False,
        can_edit_variables: bool = False,
        can_delete_variables: bool = False,
        can_share_variables: bool = False,
        can_view_variable_values: bool = False,
        # API Key permissions
        can_view_api_keys: bool = True,
        can_create_api_keys: bool = False,
        can_edit_api_keys: bool = False,
        can_delete_api_keys: bool = False,
        can_share_api_keys: bool = False,
        can_view_api_key_values: bool = False,
    ) -> Dict[str, Any]:
        # Validate inputs
        if not name or not name.strip():
            raise InvalidInputError(field_name="name", message="Role name cannot be empty")
        
        # Check if name already exists
        existing_role = self._user_roles_repository._get_by_name(session, name=name)
        if existing_role:
            raise ResourceAlreadyExistsError(
                resource_name="user_role",
                conflicting_field="name",
                message=f"Role with name '{name}' already exists"
            )
        
        # Create role
        role = self._user_roles_repository._create(
            session,
            name=name,
            description=description,
            is_system_role=is_system_role,
            display_order=display_order,
            can_view_workspace=can_view_workspace,
            can_edit_workspace=can_edit_workspace,
            can_delete_workspace=can_delete_workspace,
            can_invite_members=can_invite_members,
            can_remove_members=can_remove_members,
            can_change_plan=can_change_plan,
            can_view_workflows=can_view_workflows,
            can_create_workflows=can_create_workflows,
            can_edit_workflows=can_edit_workflows,
            can_delete_workflows=can_delete_workflows,
            can_execute_workflows=can_execute_workflows,
            can_share_workflows=can_share_workflows,
            can_view_credentials=can_view_credentials,
            can_create_credentials=can_create_credentials,
            can_edit_credentials=can_edit_credentials,
            can_delete_credentials=can_delete_credentials,
            can_share_credentials=can_share_credentials,
            can_view_credential_values=can_view_credential_values,
            can_view_files=can_view_files,
            can_upload_files=can_upload_files,
            can_download_files=can_download_files,
            can_delete_files=can_delete_files,
            can_share_files=can_share_files,
            can_view_databases=can_view_databases,
            can_create_databases=can_create_databases,
            can_edit_databases=can_edit_databases,
            can_delete_databases=can_delete_databases,
            can_share_databases=can_share_databases,
            can_view_connection_details=can_view_connection_details,
            can_view_variables=can_view_variables,
            can_create_variables=can_create_variables,
            can_edit_variables=can_edit_variables,
            can_delete_variables=can_delete_variables,
            can_share_variables=can_share_variables,
            can_view_variable_values=can_view_variable_values,
            can_view_api_keys=can_view_api_keys,
            can_create_api_keys=can_create_api_keys,
            can_edit_api_keys=can_edit_api_keys,
            can_delete_api_keys=can_delete_api_keys,
            can_share_api_keys=can_share_api_keys,
            can_view_api_key_values=can_view_api_key_values,
            created_by=created_by,
        )
        
        return {
            "id": role.id,
        }

    @with_readonly_session(manager=None)
    def get_role(
        self,
        session,
        *,
        role_id: str,
    ) -> Dict[str, Any]:
        role = self._user_roles_repository._get_by_id(session, record_id=role_id, include_deleted=False)
        if not role:
            raise ResourceNotFoundError(resource_name="user_role", resource_id=role_id)
        
        return role.to_dict()

    @with_readonly_session(manager=None)
    def get_role_by_name(
        self,
        session,
        *,
        name: str,
    ) -> Dict[str, Any]:
        role = self._user_roles_repository._get_by_name(session, name=name)
        if not role:
            raise ResourceNotFoundError(
                resource_name="user_role",
                message=f"Role with name '{name}' not found"
            )
        
        return role.to_dict()

    @with_transaction(manager=None)
    def update_role(
        self,
        session,
        *,
        role_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        display_order: Optional[int] = None,
        updated_by: str,
        # Workspace permissions
        can_view_workspace: Optional[bool] = None,
        can_edit_workspace: Optional[bool] = None,
        can_delete_workspace: Optional[bool] = None,
        can_invite_members: Optional[bool] = None,
        can_remove_members: Optional[bool] = None,
        can_change_plan: Optional[bool] = None,
        # Workflow permissions
        can_view_workflows: Optional[bool] = None,
        can_create_workflows: Optional[bool] = None,
        can_edit_workflows: Optional[bool] = None,
        can_delete_workflows: Optional[bool] = None,
        can_execute_workflows: Optional[bool] = None,
        can_share_workflows: Optional[bool] = None,
        # Credential permissions
        can_view_credentials: Optional[bool] = None,
        can_create_credentials: Optional[bool] = None,
        can_edit_credentials: Optional[bool] = None,
        can_delete_credentials: Optional[bool] = None,
        can_share_credentials: Optional[bool] = None,
        can_view_credential_values: Optional[bool] = None,
        # File permissions
        can_view_files: Optional[bool] = None,
        can_upload_files: Optional[bool] = None,
        can_download_files: Optional[bool] = None,
        can_delete_files: Optional[bool] = None,
        can_share_files: Optional[bool] = None,
        # Database permissions
        can_view_databases: Optional[bool] = None,
        can_create_databases: Optional[bool] = None,
        can_edit_databases: Optional[bool] = None,
        can_delete_databases: Optional[bool] = None,
        can_share_databases: Optional[bool] = None,
        can_view_connection_details: Optional[bool] = None,
        # Variable permissions
        can_view_variables: Optional[bool] = None,
        can_create_variables: Optional[bool] = None,
        can_edit_variables: Optional[bool] = None,
        can_delete_variables: Optional[bool] = None,
        can_share_variables: Optional[bool] = None,
        can_view_variable_values: Optional[bool] = None,
        # API Key permissions
        can_view_api_keys: Optional[bool] = None,
        can_create_api_keys: Optional[bool] = None,
        can_edit_api_keys: Optional[bool] = None,
        can_delete_api_keys: Optional[bool] = None,
        can_share_api_keys: Optional[bool] = None,
        can_view_api_key_values: Optional[bool] = None,
    ) -> Dict[str, Any]:
        role = self._user_roles_repository._get_by_id(session, record_id=role_id, include_deleted=False)
        if not role:
            raise ResourceNotFoundError(resource_name="user_role", resource_id=role_id)
        
        # Check if system role (cannot be modified)
        if role.is_system_role:
            raise InvalidInputError(
                field_name="role_id",
                message="System roles cannot be modified"
            )
        
        # Validate name if provided
        if name is not None:
            if not name or not name.strip():
                raise InvalidInputError(field_name="name", message="Role name cannot be empty")
            if name != role.name:
                existing_role = self._user_roles_repository._get_by_name(session, name=name)
                if existing_role:
                    raise ResourceAlreadyExistsError(
                        resource_name="user_role",
                        conflicting_field="name",
                        message=f"Role with name '{name}' already exists"
                    )
                role.name = name
        
        # Update fields
        if description is not None:
            role.description = description
        
        if display_order is not None:
            role.display_order = display_order
        
        # Update permissions
        permission_fields = [
            "can_view_workspace", "can_edit_workspace", "can_delete_workspace",
            "can_invite_members", "can_remove_members", "can_change_plan",
            "can_view_workflows", "can_create_workflows", "can_edit_workflows",
            "can_delete_workflows", "can_execute_workflows", "can_share_workflows",
            "can_view_credentials", "can_create_credentials", "can_edit_credentials",
            "can_delete_credentials", "can_share_credentials", "can_view_credential_values",
            "can_view_files", "can_upload_files", "can_download_files",
            "can_delete_files", "can_share_files",
            "can_view_databases", "can_create_databases", "can_edit_databases",
            "can_delete_databases", "can_share_databases", "can_view_connection_details",
            "can_view_variables", "can_create_variables", "can_edit_variables",
            "can_delete_variables", "can_share_variables", "can_view_variable_values",
            "can_view_api_keys", "can_create_api_keys", "can_edit_api_keys",
            "can_delete_api_keys", "can_share_api_keys", "can_view_api_key_values",
        ]
        
        for field in permission_fields:
            value = locals().get(field)
            if value is not None:
                setattr(role, field, value)
        
        role.updated_by = updated_by
        session.flush()
        
        return role.to_dict()

    @with_transaction(manager=None)
    def delete_role(
        self,
        session,
        *,
        role_id: str,
    ):
        role = self._user_roles_repository._get_by_id(session, record_id=role_id, include_deleted=False)
        if not role:
            raise ResourceNotFoundError(resource_name="user_role", resource_id=role_id)
        
        # Check if system role
        if role.is_system_role:
            raise InvalidInputError(
                field_name="role_id",
                message="System roles cannot be deleted"
            )
        
        # Check if role is used by workspace members
        member_count = self._workspace_member_repo._count_by_role_id(session, role_id=role_id, include_deleted=False)
        if member_count > 0:
            raise InvalidInputError(
                field_name="role_id",
                message=f"Cannot delete role that is used by {member_count} workspace member(s). Please reassign or remove members first."
            )
        
        self._user_roles_repository._delete(session, record_id=role_id)
        
        return {
            "deleted": True,
            "role_id": role_id
        }

    @with_readonly_session(manager=None)
    def get_all_roles_with_pagination(
        self,
        session,
        *,
        page: int = 1,
        page_size: int = 100,
        order_by: Optional[str] = None,
        order_desc: bool = False,
        include_deleted: bool = False
    ) -> Dict[str, Any]:
        pagination_params = PaginationParams(
            page=page,
            page_size=page_size,
            order_by=order_by or "display_order",
            order_desc=order_desc,
            include_deleted=include_deleted
        )
        pagination_params.validate()
        
        result = self._user_roles_repository._paginate(session, pagination_params=pagination_params)
        
        items = [role.to_dict() for role in result.items]
        
        return {
            "items": items,
            "metadata": result.metadata.to_dict()
        }

    @with_transaction(manager=None)
    def seed_role(self, session, *, roles_data: List[Dict]):
        """Seed roles (legacy method for backward compatibility)"""
        stats = {"created": 0, "skipped": 0, "updated": 0}

        for role_data in roles_data:
            role_name = role_data.get("name")
            if not role_name:
                continue

            existing_role = self._user_roles_repository._get_by_name(session, name=role_name)

            if existing_role:
                stats["skipped"] += 1
            else:
                self._user_roles_repository._create(session, **role_data)
                stats["created"] += 1

        return stats