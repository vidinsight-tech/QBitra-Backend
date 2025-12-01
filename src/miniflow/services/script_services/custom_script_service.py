from typing import Optional, Dict, Any, List
from datetime import datetime, timezone

from src.miniflow.database import RepositoryRegistry, with_transaction, with_readonly_session
from src.miniflow.database.utils.pagination_params import PaginationParams
from src.miniflow.database.models.enums import ScriptApprovalStatus, ScriptTestStatus
from src.miniflow.core.exceptions import (
    ResourceNotFoundError,
    ResourceAlreadyExistsError,
    InvalidInputError,
)
from src.miniflow.utils.helpers.file_helper import (
    upload_custom_script,
    delete_file,
)


class CustomScriptService:
    def __init__(self):
        self._registry = RepositoryRegistry()
        self._custom_script_repo = self._registry.custom_script_repository
        self._workspace_repo = self._registry.workspace_repository
        self._user_repo = self._registry.user_repository

    def _get_custom_script_dict(self, custom_script) -> Dict[str, Any]:
        """Helper method to convert custom script to dict"""
        return {
            "id": custom_script.id,
            "name": custom_script.name,
            "description": custom_script.description,
            "file_extension": custom_script.file_extension,
            "file_size": custom_script.file_size,
            "file_path": custom_script.file_path,
            "category": custom_script.category,
            "subcategory": custom_script.subcategory,
            "required_packages": custom_script.required_packages,
            "tags": custom_script.tags,
            "documentation_url": custom_script.documentation_url,
            "approval_status": custom_script.approval_status.value if custom_script.approval_status else None,
            "test_status": custom_script.test_status.value if custom_script.test_status else None,
        }

    @with_transaction(manager=None)
    def create_custom_script(
        self,
        session,
        *,
        workspace_id: str,
        uploaded_by: str,
        name: str,
        content: str,
        description: Optional[str] = None,
        category: Optional[str] = None,
        subcategory: Optional[str] = None,
        required_packages: Optional[List[str]] = None,
        input_schema: Optional[Dict[str, Any]] = None,
        output_schema: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        documentation_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new custom script"""
        # Validate inputs
        if not name or not name.strip():
            raise InvalidInputError(field_name="name", message="Custom script name cannot be empty")
        
        if content is None or not content.strip():
            raise InvalidInputError(field_name="content", message="Custom script content cannot be empty")
        
        # Validate workspace exists
        workspace = self._workspace_repo._get_by_id(session, record_id=workspace_id, include_deleted=False)
        if not workspace:
            raise ResourceNotFoundError(resource_name="workspace", resource_id=workspace_id)
        
        # Check custom script limit
        if workspace.current_custom_script_count >= workspace.custom_script_limit:
            raise InvalidInputError(
                field_name="workspace_id",
                message=f"Custom script limit reached. Maximum: {workspace.custom_script_limit}, Current: {workspace.current_custom_script_count}"
            )
        
        # Validate user exists
        user = self._user_repo._get_by_id(session, record_id=uploaded_by, include_deleted=False)
        if not user:
            raise ResourceNotFoundError(resource_name="user", resource_id=uploaded_by)
        
        # Check if custom script name already exists in workspace
        existing = self._custom_script_repo._get_by_name(
            session,
            workspace_id=workspace_id,
            name=name,
            include_deleted=False
        )
        if existing:
            raise ResourceAlreadyExistsError(
                resource_name="custom_script",
                conflicting_field="name",
                message=f"Custom script with name '{name}' already exists in this workspace"
            )

        # Check if custom script exists in this category and subcategory
        existing_in_category = self._custom_script_repo._get_by_name_and_category_and_subcategory(
            session,
            workspace_id=workspace_id,
            name=name,
            category=category,
            subcategory=subcategory,
            include_deleted=False
        )
        if existing_in_category:
            raise ResourceAlreadyExistsError(
                resource_name="custom_script",
                conflicting_field="name",
                message=f"Custom script with name '{name}' already exists in this workspace, category '{category or 'None'}' and subcategory '{subcategory or 'None'}'"
            )

        # Upload script file using file helper (handles all file operations, validation, etc.)
        file_extension = ".py"
        upload_result = upload_custom_script(
            content=content,
            script_name=name,
            extension=file_extension,
            workspace_id=workspace_id,
            category=category,
            subcategory=subcategory
        )
        file_path = upload_result["file_path"]
        file_size = upload_result["file_size"]
        
        # Create custom script
        custom_script = self._custom_script_repo._create(
            session,
            workspace_id=workspace_id,
            uploaded_by=uploaded_by,
            name=name,
            content=content,
            description=description,
            file_extension=file_extension,
            file_size=file_size,
            file_path=file_path,
            category=category,
            subcategory=subcategory,
            required_packages=required_packages or [],
            input_schema=input_schema or {},
            output_schema=output_schema or {},
            tags=tags or [],
            documentation_url=documentation_url,
            created_by=uploaded_by,
        )
        
        # Update workspace custom script count
        workspace.current_custom_script_count += 1
        session.flush()
        
        return self._get_custom_script_dict(custom_script)

    @with_readonly_session(manager=None)
    def get_custom_script(
        self,
        session,
        *,
        custom_script_id: str,
        workspace_id: str
    ) -> Dict[str, Any]:
        """Get custom script by ID"""
        custom_script = self._custom_script_repo._get_by_id(session, record_id=custom_script_id, include_deleted=False)
        if not custom_script:
            raise ResourceNotFoundError(resource_name="custom_script", resource_id=custom_script_id)
        
        if custom_script.workspace_id != workspace_id:
            raise ResourceNotFoundError(
                resource_name="custom_script",
                message="Custom script not found in this workspace"
            )
        
        return self._get_custom_script_dict(custom_script)

    @with_readonly_session(manager=None)
    def get_custom_script_content(
        self,
        session,
        *,
        custom_script_id: str,
        workspace_id: str
    ) -> Dict[str, Any]:
        """Get custom script content, input schema and output schema"""
        custom_script = self._custom_script_repo._get_by_id(session, record_id=custom_script_id, include_deleted=False)
        if not custom_script:
            raise ResourceNotFoundError(resource_name="custom_script", resource_id=custom_script_id)
        
        if custom_script.workspace_id != workspace_id:
            raise ResourceNotFoundError(
                resource_name="custom_script",
                message="Custom script not found in this workspace"
            )
        
        return {
            "content": custom_script.content,
            "input_schema": custom_script.input_schema,
            "output_schema": custom_script.output_schema,
        }

    @with_transaction(manager=None)
    def update_custom_script(
        self,
        session,
        *,
        custom_script_id: str,
        workspace_id: str,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        documentation_url: Optional[str] = None,
        updated_by: str
    ) -> Dict[str, Any]:
        """Update custom script metadata"""
        custom_script = self._custom_script_repo._get_by_id(session, record_id=custom_script_id, include_deleted=False)
        if not custom_script:
            raise ResourceNotFoundError(resource_name="custom_script", resource_id=custom_script_id)
        
        if custom_script.workspace_id != workspace_id:
            raise ResourceNotFoundError(
                resource_name="custom_script",
                message="Custom script not found in this workspace"
            )

        update_data = {}
        if description is not None:
            update_data["description"] = description
        if tags is not None:
            update_data["tags"] = tags
        if documentation_url is not None:
            update_data["documentation_url"] = documentation_url
        
        update_data["updated_by"] = updated_by
        
        updated_custom_script = self._custom_script_repo._update(session, record_id=custom_script_id, **update_data)
        
        return self._get_custom_script_dict(updated_custom_script)

    @with_transaction(manager=None)
    def delete_custom_script(
        self,
        session,
        *,
        custom_script_id: str,
        workspace_id: str
    ) -> Dict[str, Any]:
        """Delete custom script and its file"""
        custom_script = self._custom_script_repo._get_by_id(session, record_id=custom_script_id, include_deleted=False)
        if not custom_script:
            raise ResourceNotFoundError(resource_name="custom_script", resource_id=custom_script_id)
        
        if custom_script.workspace_id != workspace_id:
            raise ResourceNotFoundError(
                resource_name="custom_script",
                message="Custom script not found in this workspace"
            )
        
        workspace = self._workspace_repo._get_by_id(session, record_id=workspace_id, include_deleted=False)
        if not workspace:
            raise ResourceNotFoundError(resource_name="workspace", resource_id=workspace_id)
        
        # Delete file if it exists
        if custom_script.file_path:
            try:
                delete_file(custom_script.file_path)
            except Exception as e:
                # Log error but continue with deletion
                # File might already be deleted or not exist
                pass
        
        self._custom_script_repo._delete(session, record_id=custom_script_id)
        
        # Update workspace custom script count
        workspace.current_custom_script_count = max(0, workspace.current_custom_script_count - 1)
        session.flush()
        
        return {
            "deleted": True,
            "id": custom_script_id
        }

    @with_readonly_session(manager=None)
    def get_all_custom_scripts(
        self,
        session,
        *,
        workspace_id: str,
        page: int = 1,
        page_size: int = 100,
        order_by: Optional[str] = None,
        order_desc: bool = False,
        include_deleted: bool = False,
        category: Optional[str] = None,
        subcategory: Optional[str] = None,
        approval_status: Optional[ScriptApprovalStatus] = None,
        test_status: Optional[ScriptTestStatus] = None
    ) -> Dict[str, Any]:
        """Get all custom scripts with pagination and filters"""
        # Validate workspace exists
        workspace = self._workspace_repo._get_by_id(session, record_id=workspace_id, include_deleted=False)
        if not workspace:
            raise ResourceNotFoundError(resource_name="workspace", resource_id=workspace_id)
        
        pagination_params = PaginationParams(
            page=page,
            page_size=page_size,
            order_by=order_by or "created_at",
            order_desc=order_desc,
            include_deleted=include_deleted
        )
        pagination_params.validate()
        
        filter_kwargs = {'workspace_id': workspace_id}
        if category:
            filter_kwargs['category'] = category
        if subcategory:
            filter_kwargs['subcategory'] = subcategory
        if approval_status:
            filter_kwargs['approval_status'] = approval_status
        if test_status:
            filter_kwargs['test_status'] = test_status
        
        result = self._custom_script_repo._paginate(
            session,
            pagination_params=pagination_params,
            **filter_kwargs
        )
        
        items = [self._get_custom_script_dict(custom_script) for custom_script in result.items]
        
        return {
            "items": items,
            "metadata": result.metadata.to_dict()
        }