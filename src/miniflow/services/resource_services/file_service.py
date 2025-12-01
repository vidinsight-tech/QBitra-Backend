from typing import Optional, Dict, Any, List, Union, BinaryIO, TextIO

from src.miniflow.database import RepositoryRegistry, with_readonly_session, with_transaction
from src.miniflow.database.utils.pagination_params import PaginationParams
from src.miniflow.core.exceptions import (
    ResourceNotFoundError,
    ResourceAlreadyExistsError,
    InvalidInputError,
)
from src.miniflow.utils.helpers.file_helper import (
    upload_file,
    delete_file as delete_file_from_storage,
    file_exists,
    read_file,
    get_workspace_file_path,
    get_folder_size,
)


class FileService:
    def __init__(self):
        self._registry = RepositoryRegistry()
        self._file_repo = self._registry.file_repository
        self._workspace_repo = self._registry.workspace_repository
        self._user_repo = self._registry.user_repository

    @with_transaction(manager=None)
    def create_file(
        self,
        session,
        *,
        workspace_id: str,
        owner_id: str,
        uploaded_file: Union[BinaryIO, TextIO],
        name: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        file_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        # Validate workspace exists
        workspace = self._workspace_repo._get_by_id(session, record_id=workspace_id, include_deleted=False)
        if not workspace:
            raise ResourceNotFoundError(resource_name="workspace", resource_id=workspace_id)
        
        # Validate owner exists
        owner = self._user_repo._get_by_id(session, record_id=owner_id, include_deleted=False)
        if not owner:
            raise ResourceNotFoundError(resource_name="user", resource_id=owner_id)
        
        # Get workspace limits
        max_file_size_mb_per_file = workspace.max_file_size_mb_per_workspace
        storage_limit_mb = workspace.storage_limit_mb
        current_storage_mb = workspace.current_storage_mb or 0.0
        
        # Calculate current workspace folder size (files folder)
        try:
            workspace_file_path = get_workspace_file_path(workspace_id)
            current_folder_size_bytes = get_folder_size(workspace_file_path)
            current_folder_size_mb = current_folder_size_bytes / (1024 * 1024)
        except ResourceNotFoundError:
            # Folder doesn't exist yet, will be created by upload_file
            current_folder_size_mb = 0.0
        
        # Upload file using helper (validates file size, extensions, mime types)
        try:
            upload_result = upload_file(
                uploaded_file=uploaded_file,
                workspace_id=workspace_id,
                max_file_size_mb=max_file_size_mb_per_file,
            )
        except InvalidInputError as e:
            raise e
        except Exception as e:
            raise InvalidInputError(
                field_name="file",
                message=f"File upload failed: {str(e)}"
            )
        
        file_size_bytes = upload_result["file_size"]
        file_size_mb = file_size_bytes / (1024 * 1024)
        
        # Check storage limit (after upload)
        new_storage_mb = current_folder_size_mb + file_size_mb
        if new_storage_mb > storage_limit_mb:
            # Cleanup uploaded file
            try:
                delete_file_from_storage(upload_result["file_path"])
            except Exception:
                pass
            raise InvalidInputError(
                field_name="file",
                message=f"Storage limit exceeded. Current: {current_folder_size_mb:.2f} MB, "
                        f"Limit: {storage_limit_mb} MB, File size: {file_size_mb:.2f} MB"
            )
        
        # Determine file name (use provided name or generated unique name)
        file_name = name if name else upload_result["file_name"]
        # Get original filename from uploaded_file
        original_filename = getattr(uploaded_file, 'filename', upload_result["file_name"])
        
        # Check if name already exists in workspace
        existing_file = self._file_repo._get_by_name(
            session, workspace_id=workspace_id, name=file_name, include_deleted=False
        )
        if existing_file:
            # Cleanup uploaded file
            try:
                delete_file_from_storage(upload_result["file_path"])
            except Exception:
                pass
            raise ResourceAlreadyExistsError(
                resource_name="file",
                conflicting_field="name",
                message=f"File with name '{file_name}' already exists in this workspace"
            )
        
        # Create file record in database
        file_record = self._file_repo._create(
            session,
            workspace_id=workspace_id,
            owner_id=owner_id,
            name=file_name,
            original_filename=original_filename,
            file_path=upload_result["file_path"],
            file_size=file_size_bytes,
            mime_type=upload_result["mime_type"],
            file_extension=upload_result["extension"],
            description=description,
            tags=tags or [],
            file_metadata=file_metadata or {},
            created_by=owner_id,
        )
        
        # Update workspace storage (use calculated folder size for accuracy)
        workspace.current_storage_mb = new_storage_mb
        session.flush()
        
        return {
            "id": file_record.id,
        }

    @with_readonly_session(manager=None)
    def get_file(
        self,
        session,
        *,
        file_id: str,
    ) -> Dict[str, Any]:
        file_record = self._file_repo._get_by_id(session, record_id=file_id, include_deleted=False)
        if not file_record:
            raise ResourceNotFoundError(resource_name="file", resource_id=file_id)
        
        return file_record.to_dict()
    
    @with_transaction(manager=None)
    def update_file(
        self,
        session,
        *,
        file_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        updated_by: str,
    ) -> Dict[str, Any]:
        file_record = self._file_repo._get_by_id(session, record_id=file_id, include_deleted=False)
        if not file_record:
            raise ResourceNotFoundError(resource_name="file", resource_id=file_id)
        
        # Validate name if provided
        if name is not None:
            if not name or not name.strip():
                raise InvalidInputError(field_name="name", message="File name cannot be empty")
            if name != file_record.name:
                existing_file = self._file_repo._get_by_name(
                    session, workspace_id=file_record.workspace_id, name=name, include_deleted=False
                )
                if existing_file:
                    raise ResourceAlreadyExistsError(
                        resource_name="file",
                        conflicting_field="name",
                        message=f"File with name '{name}' already exists in this workspace"
                    )
                file_record.name = name

        if description is not None:
            file_record.description = description
        
        if tags is not None:
            file_record.tags = tags
        
        file_record.updated_by = updated_by
        session.flush()
        
        return file_record.to_dict()
    

    @with_transaction(manager=None)
    def delete_file(
        self,
        session,
        *,
        file_id: str,
    ) -> Dict[str, Any]:
        file_record = self._file_repo._get_by_id(session, record_id=file_id, include_deleted=False)
        if not file_record:
            raise ResourceNotFoundError(resource_name="file", resource_id=file_id)
        
        workspace_id = file_record.workspace_id
        file_path = file_record.file_path
        file_size_mb = file_record.file_size / (1024 * 1024)
        
        # Delete file from storage
        try:
            if file_exists(file_path):
                delete_file_from_storage(file_path)
        except Exception as e:
            # Log error but continue with database deletion
            # File might already be deleted or not accessible
            pass
        
        # Delete from database
        self._file_repo._delete(session, record_id=file_id)
        
        # Update workspace storage
        workspace = self._workspace_repo._get_by_id(session, record_id=workspace_id, include_deleted=False)
        if workspace:
            # Recalculate folder size for accuracy
            try:
                workspace_file_path = get_workspace_file_path(workspace_id)
                current_folder_size_bytes = get_folder_size(workspace_file_path)
                workspace.current_storage_mb = current_folder_size_bytes / (1024 * 1024)
            except ResourceNotFoundError:
                # Folder doesn't exist, set to 0
                workspace.current_storage_mb = 0.0
            session.flush()
        
        return {
            "deleted": True,
            "id": file_id
        }

    
    @with_readonly_session(manager=None)
    def get_all_files_with_pagination(
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
        
        result = self._file_repo._paginate(
            session,
            pagination_params=pagination_params,
            workspace_id=workspace_id
        )
        
        items = [file_record.to_dict() for file_record in result.items]
        
        return {
            "items": items,
            "metadata": result.metadata.to_dict()
        }


    @with_readonly_session(manager=None)
    def get_file_content(
        self,
        session,
        *,
        file_id: str,
    ) -> bytes:
        file_record = self._file_repo._get_by_id(session, record_id=file_id, include_deleted=False)
        if not file_record:
            raise ResourceNotFoundError(resource_name="file", resource_id=file_id)
        
        if not file_exists(file_record.file_path):
            raise ResourceNotFoundError(
                resource_name="file",
                resource_id=file_id,
                message="File not found on storage"
            )
        
        return read_file(file_record.file_path)