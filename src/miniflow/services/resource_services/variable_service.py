from typing import Dict, List, Any, Optional

from src.miniflow.database import RepositoryRegistry, with_readonly_session, with_transaction
from src.miniflow.database.utils.pagination_params import PaginationParams
from src.miniflow.core.exceptions import (
    ResourceNotFoundError,
    ResourceAlreadyExistsError,
    InvalidInputError,
)
from src.miniflow.utils.helpers.encryption_helper import encrypt_data, decrypt_data


class VariableService:
    def __init__(self):
        self._registry = RepositoryRegistry()
        self._variable_repo = self._registry.variable_repository
        self._workspace_repo = self._registry.workspace_repository
        self._user_repo = self._registry.user_repository

    def _get_variable_dict(self, variable) -> Dict[str, Any]:
        """Helper method to convert variable to dict with proper decryption"""
        variable_dict = variable.to_dict()
        if variable.is_secret:
            variable_dict['value'] = decrypt_data(variable.value)
        else:
            variable_dict['value'] = variable.value
        return variable_dict

    @with_transaction(manager=None)
    def create_variable(
        self,
        session,
        *,
        workspace_id: str,
        owner_id: str,
        key: str,
        value: str,
        description: Optional[str] = None,
        is_secret: bool = False,
    ) -> Dict[str, Any]:
        # Validate inputs
        if not key or not key.strip():
            raise InvalidInputError(field_name="key", message="Variable key cannot be empty")
        if value is None:
            raise InvalidInputError(field_name="value", message="Variable value cannot be None")
        
        # Validate workspace exists
        workspace = self._workspace_repo._get_by_id(session, record_id=workspace_id, include_deleted=False)
        if not workspace:
            raise ResourceNotFoundError(resource_name="workspace", resource_id=workspace_id)
        
        # Validate owner exists
        owner = self._user_repo._get_by_id(session, record_id=owner_id, include_deleted=False)
        if not owner:
            raise ResourceNotFoundError(resource_name="user", resource_id=owner_id)
        
        # Check if key already exists
        existing_variable = self._variable_repo._get_by_key(session, workspace_id=workspace_id, key=key, include_deleted=False)
        if existing_variable:
            raise ResourceAlreadyExistsError(
                resource_name="variable",
                conflicting_field="key",
                message=f"Variable with key '{key}' already exists in this workspace"
            )
        
        # Encrypt value if secret
        encrypted_value = encrypt_data(value) if is_secret else value

        variable = self._variable_repo._create(
            session,
            workspace_id=workspace_id,
            owner_id=owner_id,
            key=key,
            value=encrypted_value,
            description=description,
            is_secret=is_secret,
            created_by=owner_id,
        )
        
        return {
            "id": variable.id,
        }

    @with_readonly_session(manager=None)
    def get_variable(
        self,
        session,
        *,
        variable_id: str,
    ) -> Dict[str, Any]:
        variable = self._variable_repo._get_by_id(session, record_id=variable_id, include_deleted=False)
        if not variable:
            raise ResourceNotFoundError(resource_name="variable", resource_id=variable_id)
        
        return self._get_variable_dict(variable)

    @with_transaction(manager=None)
    def update_variable(
        self,
        session,
        *,
        variable_id: str,
        key: Optional[str] = None,
        value: Optional[str] = None,
        description: Optional[str] = None,
        is_secret: Optional[bool] = None,
        updated_by: str,
    ) -> Dict[str, Any]:
        variable = self._variable_repo._get_by_id(session, record_id=variable_id, include_deleted=False)
        if not variable:
            raise ResourceNotFoundError(resource_name="variable", resource_id=variable_id)
        
        # Validate key if provided
        if key is not None:
            if not key or not key.strip():
                raise InvalidInputError(field_name="key", message="Variable key cannot be empty")
            if key != variable.key:
                existing_variable = self._variable_repo._get_by_key(
                    session, workspace_id=variable.workspace_id, key=key, include_deleted=False
                )
                if existing_variable:
                    raise ResourceAlreadyExistsError(
                        resource_name="variable",
                        conflicting_field="key",
                        message=f"Variable with key '{key}' already exists in this workspace"
                    )
                variable.key = key

        if description is not None:
            variable.description = description

        # Handle is_secret change - need to re-encrypt/decrypt existing value if needed
        is_secret_changed = is_secret is not None and is_secret != variable.is_secret
        
        if is_secret_changed:
            # If changing from secret to non-secret, decrypt the current value
            if variable.is_secret and not is_secret:
                current_value = decrypt_data(variable.value)
                variable.value = current_value
            # If changing from non-secret to secret, encrypt the current value
            elif not variable.is_secret and is_secret:
                current_value = variable.value
                variable.value = encrypt_data(current_value)
            variable.is_secret = is_secret

        # Handle value update - use current is_secret status (after potential change above)
        if value is not None:
            # Use variable.is_secret (which may have been updated above)
            variable.value = encrypt_data(value) if variable.is_secret else value

        variable.updated_by = updated_by

        session.flush()
        return {
            'id': variable_id
        }

    @with_transaction(manager=None)
    def delete_variable(
        self,
        session,
        *,
        variable_id: str,
    ):
        variable = self._variable_repo._get_by_id(session, record_id=variable_id, include_deleted=False)
        if not variable:
            raise ResourceNotFoundError(resource_name="variable", resource_id=variable_id)
        
        self._variable_repo._delete(session, record_id=variable_id)
        
        return {
            "deleted": True,
            "id": variable_id
        }

    @with_readonly_session(manager=None)
    def get_all_variables_with_pagination(
        self,
        session,
        *,
        workspace_id: str,
        page: int = 1,
        page_size: int = 100,
        order_by: Optional[str] = None,
        order_desc: bool = False,
        include_deleted: bool = False
    ) -> Dict[str, Any]:
        workspace = self._workspace_repo._get_by_id(session, record_id=workspace_id, include_deleted=False)
        if not workspace:
            raise ResourceNotFoundError(resource_name="workspace", resource_id=workspace_id)
        
        pagination_params = PaginationParams(page=page, page_size=page_size, order_by=order_by, order_desc=order_desc, include_deleted=include_deleted)
        pagination_params.validate()
        
        result = self._variable_repo._paginate(session, pagination_params=pagination_params, workspace_id=workspace_id)
        
        items = [self._get_variable_dict(variable) for variable in result.items]
        
        return {
            "items": items,
            "metadata": result.metadata.to_dict()
        }