from typing import Optional, Dict, Any, List

from src.miniflow.database import RepositoryRegistry, with_transaction, with_readonly_session
from src.miniflow.database.utils.pagination_params import PaginationParams
from src.miniflow.database.utils.filter_params import FilterParams
from src.miniflow.database.models.enums import WorkflowStatus, TriggerType
from src.miniflow.core.exceptions import (
    ResourceNotFoundError,
    ResourceAlreadyExistsError,
    InvalidInputError,
)


class WorkflowService:
    def __init__(self):
        self._registry = RepositoryRegistry()
        self._workflow_repo = self._registry.workflow_repository
        self._workspace_repo = self._registry.workspace_repository
        self._user_repo = self._registry.user_repository
        self._trigger_repo = self._registry.trigger_repository

    def _get_workflow_dict(self, workflow) -> Dict[str, Any]:
        """Helper method to convert workflow to dict"""
        return {
            "id": workflow.id,
            "name": workflow.name,
            "description": workflow.description,
            "priority": workflow.priority,
            "status": workflow.status.value if workflow.status else None,
            "status_message": workflow.status_message,
            "tags": workflow.tags or [],
            "workspace_id": workflow.workspace_id,
            "created_at": workflow.created_at.isoformat() if workflow.created_at else None,
            "updated_at": workflow.updated_at.isoformat() if workflow.updated_at else None,
            "created_by": workflow.created_by,
            "updated_by": workflow.updated_by,
        }

    @with_transaction(manager=None)
    def create_workflow(
        self,
        session,
        *,
        workspace_id: str,
        name: str,
        description: Optional[str] = None,
        priority: int = 1,
        status: WorkflowStatus = WorkflowStatus.DRAFT,
        status_message: Optional[str] = None,
        tags: Optional[List[str]] = None,
        created_by: str,
    ) -> Dict[str, Any]:
        """Create a new workflow"""
        # Validate inputs
        if not name or not name.strip():
            raise InvalidInputError(field_name="name", message="Workflow name cannot be empty")
        
        if not workspace_id or not workspace_id.strip():
            raise InvalidInputError(field_name="workspace_id", message="Workspace ID cannot be empty")
        
        if not created_by or not created_by.strip():
            raise InvalidInputError(field_name="created_by", message="Created by cannot be empty")
        
        if priority < 1:
            raise InvalidInputError(field_name="priority", message="Priority must be greater than 0")
        
        # Validate workspace exists
        workspace = self._workspace_repo._get_by_id(session, record_id=workspace_id, include_deleted=False)
        if not workspace:
            raise ResourceNotFoundError(resource_name="workspace", resource_id=workspace_id)
        
        # Validate user exists
        user = self._user_repo._get_by_id(session, record_id=created_by, include_deleted=False)
        if not user:
            raise ResourceNotFoundError(resource_name="user", resource_id=created_by)
        
        # Check if workflow name already exists in workspace
        existing = self._workflow_repo._get_by_name(session, workspace_id=workspace_id, name=name, include_deleted=False)
        if existing:
            raise ResourceAlreadyExistsError(
                resource_name="workflow",
                conflicting_field="name",
                message=f"Workflow with name '{name}' already exists in this workspace"
            )
        
        workflow = self._workflow_repo._create(
            session,
            workspace_id=workspace_id,
            name=name,
            description=description,
            priority=priority,
            status=status,
            status_message=status_message or 'Currently no error context is available',
            tags=tags or [],
            created_by=created_by,
        )
        
        # Create default API trigger automatically
        # Check if "DEFAULT" trigger name already exists in workspace (very unlikely but check anyway)
        existing_default_trigger = self._trigger_repo._get_by_name(
            session, 
            workspace_id=workspace_id, 
            name="DEFAULT", 
            include_deleted=False
        )
        
        if not existing_default_trigger:
            # Create default API trigger (using WEBHOOK type for API endpoints)
            self._trigger_repo._create(
                session,
                workspace_id=workspace_id,
                workflow_id=workflow.id,
                name="DEFAULT",
                trigger_type=TriggerType.WEBHOOK,
                config={},  # Empty config for default trigger
                description="Default API trigger created automatically with workflow",
                input_mapping={},
                is_enabled=True,
                created_by=created_by,
            )
        
        return self._get_workflow_dict(workflow)

    @with_readonly_session(manager=None)
    def get_workflow(
        self,
        session,
        *,
        workflow_id: str,
        workspace_id: str
    ) -> Dict[str, Any]:
        """Get workflow by ID"""
        workflow = self._workflow_repo._get_by_id(session, record_id=workflow_id, include_deleted=False)
        if not workflow:
            raise ResourceNotFoundError(resource_name="workflow", resource_id=workflow_id)
        
        if workflow.workspace_id != workspace_id:
            raise ResourceNotFoundError(
                resource_name="workflow",
                message="Workflow not found in this workspace"
            )
        
        return self._get_workflow_dict(workflow)

    @with_transaction(manager=None)
    def update_workflow(
        self,
        session,
        *,
        workflow_id: str,
        workspace_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        priority: Optional[int] = None,
        status: Optional[WorkflowStatus] = None,
        status_message: Optional[str] = None,
        tags: Optional[List[str]] = None,
        updated_by: str,
    ) -> Dict[str, Any]:
        """Update workflow"""
        workflow = self._workflow_repo._get_by_id(session, record_id=workflow_id, include_deleted=False)
        if not workflow:
            raise ResourceNotFoundError(resource_name="workflow", resource_id=workflow_id)
        
        if workflow.workspace_id != workspace_id:
            raise ResourceNotFoundError(
                resource_name="workflow",
                message="Workflow not found in this workspace"
            )
        
        # Validate user exists
        user = self._user_repo._get_by_id(session, record_id=updated_by, include_deleted=False)
        if not user:
            raise ResourceNotFoundError(resource_name="user", resource_id=updated_by)
        
        # Validate inputs
        if name is not None:
            if not name.strip():
                raise InvalidInputError(field_name="name", message="Workflow name cannot be empty")
            # Check if name change would cause duplicate
            if name != workflow.name:
                existing = self._workflow_repo._get_by_name(session, workspace_id=workflow.workspace_id, name=name, include_deleted=False)
                if existing:
                    raise ResourceAlreadyExistsError(
                        resource_name="workflow",
                        conflicting_field="name",
                        message=f"Workflow with name '{name}' already exists in this workspace"
                    )
        
        if priority is not None and priority < 1:
            raise InvalidInputError(field_name="priority", message="Priority must be greater than 0")
        
        update_data = {}
        if name is not None:
            update_data['name'] = name
        if description is not None:
            update_data['description'] = description
        if priority is not None:
            update_data['priority'] = priority
        if status is not None:
            update_data['status'] = status
        if status_message is not None:
            update_data['status_message'] = status_message
        if tags is not None:
            update_data['tags'] = tags
        
        if update_data:
            update_data['updated_by'] = updated_by
            self._workflow_repo._update(
                session,
                record_id=workflow_id,
                **update_data
            )
        
        # Refresh workflow
        workflow = self._workflow_repo._get_by_id(session, record_id=workflow_id, include_deleted=False)
        
        return self._get_workflow_dict(workflow)

    @with_transaction(manager=None)
    def delete_workflow(
        self,
        session,
        *,
        workflow_id: str,
        workspace_id: str
    ) -> Dict[str, Any]:
        """Delete workflow"""
        workflow = self._workflow_repo._get_by_id(session, record_id=workflow_id, include_deleted=False)
        if not workflow:
            raise ResourceNotFoundError(resource_name="workflow", resource_id=workflow_id)
        
        if workflow.workspace_id != workspace_id:
            raise ResourceNotFoundError(
                resource_name="workflow",
                message="Workflow not found in this workspace"
            )
        
        self._workflow_repo._delete(session, record_id=workflow_id)
        
        return {
            "deleted": True,
            "workflow_id": workflow_id
        }

    @with_readonly_session(manager=None)
    def get_all_workflows(
        self,
        session,
        *,
        workspace_id: str,
        page: int = 1,
        page_size: int = 100,
        order_by: Optional[str] = None,
        order_desc: bool = False,
        include_deleted: bool = False,
        status: Optional[WorkflowStatus] = None,
    ) -> Dict[str, Any]:
        """Get all workflows with pagination"""
        # Validate workspace exists
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
        
        # Build filters
        filter_params = FilterParams()
        filter_params.add_equality_filter('workspace_id', workspace_id)
        if status:
            filter_params.add_equality_filter('status', status)
        
        result = self._workflow_repo._paginate(
            session,
            pagination_params=pagination_params,
            filter_params=filter_params
        )
        
        items = [self._get_workflow_dict(workflow) for workflow in result.items]
        
        return {
            "items": items,
            "metadata": result.metadata.to_dict()
        }

