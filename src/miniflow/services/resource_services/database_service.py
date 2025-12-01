from typing import Dict, List, Any, Optional

from src.miniflow.database import RepositoryRegistry, with_readonly_session, with_transaction
from src.miniflow.database.models.enums import DatabaseType
from src.miniflow.database.utils.pagination_params import PaginationParams
from src.miniflow.core.exceptions import (
    ResourceNotFoundError,
    ResourceAlreadyExistsError,
    InvalidInputError,
)
from src.miniflow.utils.helpers.encryption_helper import encrypt_data, decrypt_data


class DatabaseService:
    def __init__(self):        
        self._registry = RepositoryRegistry()
        self._database_repo = self._registry.database_repository
        self._workspace_repo = self._registry.workspace_repository
        self._user_repo = self._registry.user_repository

    def _get_database_dict(self, database) -> Dict[str, Any]:
        """Helper method to convert database to dict with proper decryption"""
        database_dict = database.to_dict()
        if database.password:
            database_dict['password'] = decrypt_data(database.password)
        return database_dict

    @with_transaction(manager=None)
    def create_database(
        self,
        session,
        *,
        workspace_id: str,
        owner_id: str,
        name: str,
        database_type: DatabaseType,
        host: Optional[str] = None,
        port: Optional[int] = None,
        database_name: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        connection_string: Optional[str] = None,
        ssl_enabled: bool = False,
        additional_params: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        is_active: bool = True,
    ) -> Dict[str, Any]:
        # Validate inputs
        if not name or not name.strip():
            raise InvalidInputError(field_name="name", message="Database name cannot be empty")
        
        # Validate workspace exists
        workspace = self._workspace_repo._get_by_id(session, record_id=workspace_id, include_deleted=False)
        if not workspace:
            raise ResourceNotFoundError(resource_name="workspace", resource_id=workspace_id)
        
        # Validate owner exists
        owner = self._user_repo._get_by_id(session, record_id=owner_id, include_deleted=False)
        if not owner:
            raise ResourceNotFoundError(resource_name="user", resource_id=owner_id)
        
        # Check if name already exists in workspace
        existing_database = self._database_repo._get_by_name(
            session, workspace_id=workspace_id, name=name, include_deleted=False
        )
        if existing_database:
            raise ResourceAlreadyExistsError(
                resource_name="database",
                conflicting_field="name",
                message=f"Database with name '{name}' already exists in this workspace"
            )
        
        # Validate that either connection_string or host is provided
        if not connection_string and not host:
            raise InvalidInputError(
                field_name="connection_string",
                message="Either connection_string or host must be provided"
            )
        
        # Encrypt password if provided
        encrypted_password = encrypt_data(password) if password else None

        database = self._database_repo._create(
            session,
            workspace_id=workspace_id,
            owner_id=owner_id,
            name=name,
            database_type=database_type,
            host=host,
            port=port,
            database_name=database_name,
            username=username,
            password=encrypted_password,
            connection_string=connection_string,
            ssl_enabled=ssl_enabled,
            additional_params=additional_params or {},
            description=description,
            tags=tags or [],
            is_active=is_active,
            created_by=owner_id,
        )
        
        return {
            "id": database.id,
        }

    @with_readonly_session(manager=None)
    def get_database(
        self,
        session,
        *,
        database_id: str,
    ) -> Dict[str, Any]:
        database = self._database_repo._get_by_id(session, record_id=database_id, include_deleted=False)
        if not database:
            raise ResourceNotFoundError(resource_name="database", resource_id=database_id)
        
        return self._get_database_dict(database)

    @with_transaction(manager=None)
    def update_database(
        self,
        session,
        *,
        database_id: str,
        name: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
        database_name: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        connection_string: Optional[str] = None,
        ssl_enabled: Optional[bool] = None,
        additional_params: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        is_active: Optional[bool] = None,
        updated_by: str,
    ) -> Dict[str, Any]:
        database = self._database_repo._get_by_id(session, record_id=database_id, include_deleted=False)
        if not database:
            raise ResourceNotFoundError(resource_name="database", resource_id=database_id)
        
        # Validate name if provided
        if name is not None:
            if not name or not name.strip():
                raise InvalidInputError(field_name="name", message="Database name cannot be empty")
            if name != database.name:
                existing_database = self._database_repo._get_by_name(
                    session, workspace_id=database.workspace_id, name=name, include_deleted=False
                )
                if existing_database:
                    raise ResourceAlreadyExistsError(
                        resource_name="database",
                        conflicting_field="name",
                        message=f"Database with name '{name}' already exists in this workspace"
                    )
                database.name = name

        if host is not None:
            database.host = host
        
        if port is not None:
            database.port = port
        
        if database_name is not None:
            database.database_name = database_name
        
        if username is not None:
            database.username = username
        
        if password is not None:
            database.password = encrypt_data(password)
        
        if connection_string is not None:
            database.connection_string = connection_string
        
        if ssl_enabled is not None:
            database.ssl_enabled = ssl_enabled
        
        if additional_params is not None:
            database.additional_params = additional_params
        
        if description is not None:
            database.description = description
        
        if tags is not None:
            database.tags = tags
        
        if is_active is not None:
            database.is_active = is_active

        database.updated_by = updated_by

        session.flush()
        return {
            'id': database_id
        }

    @with_transaction(manager=None)
    def delete_database(
        self,
        session,
        *,
        database_id: str,
    ):
        database = self._database_repo._get_by_id(session, record_id=database_id, include_deleted=False)
        if not database:
            raise ResourceNotFoundError(resource_name="database", resource_id=database_id)
        
        self._database_repo._delete(session, record_id=database_id)
        
        return {
            "deleted": True,
            "id": database_id
        }

    @with_readonly_session(manager=None)
    def get_all_databases_with_pagination(
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
        
        pagination_params = PaginationParams(
            page=page, 
            page_size=page_size, 
            order_by=order_by, 
            order_desc=order_desc, 
            include_deleted=include_deleted
        )
        pagination_params.validate()
        
        result = self._database_repo._paginate(
            session, 
            pagination_params=pagination_params, 
            workspace_id=workspace_id
        )
        
        items = [self._get_database_dict(database) for database in result.items]
        
        return {
            "items": items,
            "metadata": result.metadata.to_dict()
        }