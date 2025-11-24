from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import json

from src.miniflow.database import RepositoryRegistry, with_readonly_session, with_transaction
from src.miniflow.database.models.enums import CredentialType, CredentialProvider
from src.miniflow.database.utils.pagination_params import PaginationParams
from src.miniflow.core.exceptions import (
    ResourceNotFoundError,
    ResourceAlreadyExistsError,
    InvalidInputError,
)
from src.miniflow.utils.helpers.encryption_helper import encrypt_data, decrypt_data


class CredentialService:
    def __init__(self):
        self._registry = RepositoryRegistry()
        self._credential_repo = self._registry.credential_repository
        self._workspace_repo = self._registry.workspace_repository
        self._user_repo = self._registry.user_repository

    def _get_credential_dict(self, credential) -> Dict[str, Any]:
        """Helper method to convert credential to dict with proper decryption"""
        credential_dict = credential.to_dict()
        # Decrypt credential_data
        # credential_data is stored as encrypted string in JSON column
        if credential.credential_data:
            try:
                # credential_data might be stored as string (encrypted) or already as dict
                if isinstance(credential.credential_data, str):
                    # It's encrypted string, decrypt it
                    decrypted_data = decrypt_data(credential.credential_data)
                    credential_dict['credential_data'] = json.loads(decrypted_data)
                elif isinstance(credential.credential_data, dict):
                    # Already decrypted (shouldn't happen, but handle it)
                    credential_dict['credential_data'] = credential.credential_data
                else:
                    # Fallback
                    credential_dict['credential_data'] = credential.credential_data
            except (json.JSONDecodeError, Exception):
                # If decryption fails or invalid JSON, return as is
                credential_dict['credential_data'] = credential.credential_data
        return credential_dict

    def _prepare_credential_data(self, data: Dict[str, Any]) -> str:
        """Prepare and encrypt credential data"""
        json_str = json.dumps(data, ensure_ascii=False)
        return encrypt_data(json_str)

    @with_transaction(manager=None)
    def create_api_key_credential(
        self,
        session,
        *,
        workspace_id: str,
        owner_id: str,
        name: str,
        api_key: str,
        credential_provider: str,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        expires_at: Optional[datetime] = None,
        is_active: bool = True,
    ) -> Dict[str, Any]:

        # Validate inputs
        if not name or not name.strip():
            raise InvalidInputError(field_name="name", message="Credential name cannot be empty")
        if not api_key or not api_key.strip():
            raise InvalidInputError(field_name="api_key", message="API key cannot be empty")
        if not credential_provider or not credential_provider.strip():
            raise InvalidInputError(field_name="credential_provider", message="Credential provider cannot be empty")
        
        # Validate workspace exists
        workspace = self._workspace_repo._get_by_id(session, record_id=workspace_id, include_deleted=False)
        if not workspace:
            raise ResourceNotFoundError(resource_name="workspace", resource_id=workspace_id)
        
        # Validate user exists
        user = self._user_repo._get_by_id(session, record_id=owner_id, include_deleted=False)
        if not user:
            raise ResourceNotFoundError(resource_name="user", resource_id=owner_id)
        
        # Check if name already exists in workspace
        existing = self._credential_repo._get_by_name(
            session, workspace_id=workspace_id, name=name, include_deleted=False
        )
        if existing:
            raise ResourceAlreadyExistsError(
                resource_name="credential",
                conflicting_field="name",
                message=f"Credential with name '{name}' already exists in this workspace"
            )
        
        # Prepare credential data
        credential_data = {
            "api_key": api_key,
        }
        
        # Encrypt credential data
        encrypted_data = self._prepare_credential_data(credential_data)
        
        # Create credential
        credential = self._credential_repo._create(
            session,
            workspace_id=workspace_id,
            owner_id=owner_id,
            name=name,
            credential_type=CredentialType.API_KEY,
            credential_provider=credential_provider,
            description=description,
            credential_data=encrypted_data,
            is_active=is_active,
            expires_at=expires_at,
            tags=tags or [],
            created_by=owner_id,
        )
        
        return {
            "id": credential.id,
        }


    @with_readonly_session(manager=None)
    def get_credential(
        self,
        session,
        *,
        credential_id: str,
    ) -> Dict[str, Any]:
        """Get credential by ID"""
        credential = self._credential_repo._get_by_id(session, record_id=credential_id, include_deleted=False)
        if not credential:
            raise ResourceNotFoundError(resource_name="credential", resource_id=credential_id)
        
        return self._get_credential_dict(credential)

    @with_readonly_session(manager=None)
    def get_all_credentials_with_pagination(
        self,
        session,
        *,
        workspace_id: Optional[str] = None,
        credential_type: Optional[CredentialType] = None,
        page: int = 1,
        page_size: int = 100,
        order_by: Optional[str] = None,
        order_desc: bool = True,
        include_deleted: bool = False
    ) -> Dict[str, Any]:
        """Get all credentials with pagination"""
        pagination_params = PaginationParams(
            page=page,
            page_size=page_size,
            order_by=order_by or "created_at",
            order_desc=order_desc,
            include_deleted=include_deleted
        )
        pagination_params.validate()
        
        # Apply filters if provided
        filter_params = None
        if workspace_id or credential_type:
            from src.miniflow.database.utils.filter_params import FilterParams
            filter_params = FilterParams()
            if workspace_id:
                filter_params.add_equality_filter("workspace_id", workspace_id)
            if credential_type:
                filter_params.add_equality_filter("credential_type", credential_type)
        
        result = self._credential_repo._paginate(
            session,
            pagination_params=pagination_params,
            filter_params=filter_params
        )
        
        items = [self._get_credential_dict(credential) for credential in result.items]
        
        return {
            "items": items,
            "metadata": result.metadata.to_dict()
        }

    @with_transaction(manager=None)
    def delete_credential(
        self,
        session,
        *,
        credential_id: str,
    ):
        """Delete credential"""
        credential = self._credential_repo._get_by_id(session, record_id=credential_id, include_deleted=False)
        if not credential:
            raise ResourceNotFoundError(resource_name="credential", resource_id=credential_id)
        
        self._credential_repo._delete(session, record_id=credential_id)
        
        return {
            "deleted": True,
            "credential_id": credential_id
        }

