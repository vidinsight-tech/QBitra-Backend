from typing import Optional, Dict, Any, List

from src.miniflow.database import RepositoryRegistry, with_transaction, with_readonly_session
from src.miniflow.database.utils.pagination_params import PaginationParams
from src.miniflow.database.utils.filter_params import FilterParams
from src.miniflow.database.models.enums import TriggerType
from src.miniflow.core.exceptions import (
    ResourceNotFoundError,
    ResourceAlreadyExistsError,
    InvalidInputError,
)


class TriggerService:
    def __init__(self):
        self._registry = RepositoryRegistry()
        self._trigger_repo = self._registry.trigger_repository
        self._workflow_repo = self._registry.workflow_repository
        self._workspace_repo = self._registry.workspace_repository
        self._user_repo = self._registry.user_repository

    def _get_trigger_dict(self, trigger) -> Dict[str, Any]:
        """Helper method to convert trigger to dict"""
        return {
            "id": trigger.id,
            "name": trigger.name,
            "description": trigger.description,
            "trigger_type": trigger.trigger_type.value if trigger.trigger_type else None,
            "config": trigger.config or {},
            "input_mapping": trigger.input_mapping or {},
            "is_enabled": trigger.is_enabled,
            "workspace_id": trigger.workspace_id,
            "workflow_id": trigger.workflow_id,
            "created_at": trigger.created_at.isoformat() if trigger.created_at else None,
            "updated_at": trigger.updated_at.isoformat() if trigger.updated_at else None,
            "created_by": trigger.created_by,
            "updated_by": trigger.updated_by,
        }

    def _validate_input_mapping(self, input_mapping: Dict[str, Any]) -> None:
        """
        Validate input mapping structure.
        Expected format: {VARIABLE_NAME: {type: str, value: Any}}
        
        Args:
            input_mapping: Input mapping dictionary to validate
            
        Raises:
            InvalidInputError: If input mapping structure is invalid
        """
        if not isinstance(input_mapping, dict):
            raise InvalidInputError(
                field_name="input_mapping",
                message="Input mapping must be a dictionary"
            )
        
        for variable_name, mapping_value in input_mapping.items():
            if not isinstance(variable_name, str) or not variable_name.strip():
                raise InvalidInputError(
                    field_name="input_mapping",
                    message=f"Variable name must be a non-empty string, got: {type(variable_name).__name__}"
                )
            
            if not isinstance(mapping_value, dict):
                raise InvalidInputError(
                    field_name="input_mapping",
                    message=f"Mapping value for '{variable_name}' must be a dictionary with 'type' and 'value' keys"
                )
            
            if 'type' not in mapping_value:
                raise InvalidInputError(
                    field_name="input_mapping",
                    message=f"Mapping value for '{variable_name}' must contain 'type' key"
                )
            
            if not isinstance(mapping_value['type'], str) or not mapping_value['type'].strip():
                raise InvalidInputError(
                    field_name="input_mapping",
                    message=f"Type for '{variable_name}' must be a non-empty string"
                )
            
            if 'value' not in mapping_value:
                raise InvalidInputError(
                    field_name="input_mapping",
                    message=f"Mapping value for '{variable_name}' must contain 'value' key"
                )

    @with_transaction(manager=None)
    def create_trigger(
        self,
        session,
        *,
        workspace_id: str,
        workflow_id: str,
        name: str,
        trigger_type: TriggerType,
        config: Dict[str, Any],
        description: Optional[str] = None,
        input_mapping: Optional[Dict[str, Any]] = None,
        is_enabled: bool = True,
        created_by: str,
    ) -> Dict[str, Any]:
        """Create a new trigger"""
        # Validate inputs
        if not name or not name.strip():
            raise InvalidInputError(field_name="name", message="Trigger name cannot be empty")
        
        if not workspace_id or not workspace_id.strip():
            raise InvalidInputError(field_name="workspace_id", message="Workspace ID cannot be empty")
        
        if not workflow_id or not workflow_id.strip():
            raise InvalidInputError(field_name="workflow_id", message="Workflow ID cannot be empty")
        
        if not created_by or not created_by.strip():
            raise InvalidInputError(field_name="created_by", message="Created by cannot be empty")
        
        if not isinstance(config, dict):
            raise InvalidInputError(field_name="config", message="Config must be a dictionary")
        
        # Validate workspace exists
        workspace = self._workspace_repo._get_by_id(session, record_id=workspace_id, include_deleted=False)
        if not workspace:
            raise ResourceNotFoundError(resource_name="workspace", resource_id=workspace_id)
        
        # Verify workflow exists and belongs to workspace
        workflow = self._workflow_repo._get_by_id(session, record_id=workflow_id, include_deleted=False)
        if not workflow:
            raise ResourceNotFoundError(resource_name="workflow", resource_id=workflow_id)
        
        if workflow.workspace_id != workspace_id:
            raise InvalidInputError(
                field_name="workflow_id",
                message="Workflow does not belong to this workspace"
            )
        
        # Validate user exists
        user = self._user_repo._get_by_id(session, record_id=created_by, include_deleted=False)
        if not user:
            raise ResourceNotFoundError(resource_name="user", resource_id=created_by)
        
        # Check if trigger name already exists in workspace
        existing = self._trigger_repo._get_by_name(session, workspace_id=workspace_id, name=name, include_deleted=False)
        if existing:
            raise ResourceAlreadyExistsError(
                resource_name="trigger",
                conflicting_field="name",
                message=f"Trigger with name '{name}' already exists in this workspace"
            )
        
        # Validate input mapping if provided
        if input_mapping:
            self._validate_input_mapping(input_mapping)
        
        trigger = self._trigger_repo._create(
            session,
            workspace_id=workspace_id,
            workflow_id=workflow_id,
            name=name,
            trigger_type=trigger_type,
            config=config,
            description=description,
            input_mapping=input_mapping or {},
            is_enabled=is_enabled,
            created_by=created_by,
        )
        
        return self._get_trigger_dict(trigger)

    @with_readonly_session(manager=None)
    def get_trigger(
        self,
        session,
        *,
        trigger_id: str,
        workspace_id: str
    ) -> Dict[str, Any]:
        """Get trigger by ID"""
        trigger = self._trigger_repo._get_by_id(session, record_id=trigger_id, include_deleted=False)
        if not trigger:
            raise ResourceNotFoundError(resource_name="trigger", resource_id=trigger_id)
        
        if trigger.workspace_id != workspace_id:
            raise ResourceNotFoundError(
                resource_name="trigger",
                message="Trigger not found in this workspace"
            )
        
        return self._get_trigger_dict(trigger)

    @with_transaction(manager=None)
    def update_trigger(
        self,
        session,
        *,
        trigger_id: str,
        workspace_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        trigger_type: Optional[TriggerType] = None,
        config: Optional[Dict[str, Any]] = None,
        input_mapping: Optional[Dict[str, Any]] = None,
        is_enabled: Optional[bool] = None,
        updated_by: str,
    ) -> Dict[str, Any]:
        """Update trigger"""
        trigger = self._trigger_repo._get_by_id(session, record_id=trigger_id, include_deleted=False)
        if not trigger:
            raise ResourceNotFoundError(resource_name="trigger", resource_id=trigger_id)
        
        if trigger.workspace_id != workspace_id:
            raise ResourceNotFoundError(
                resource_name="trigger",
                message="Trigger not found in this workspace"
            )
        
        # Validate user exists
        user = self._user_repo._get_by_id(session, record_id=updated_by, include_deleted=False)
        if not user:
            raise ResourceNotFoundError(resource_name="user", resource_id=updated_by)
        
        # Validate inputs
        if name is not None:
            if not name.strip():
                raise InvalidInputError(field_name="name", message="Trigger name cannot be empty")
            # Check if name change would cause duplicate
            if name != trigger.name:
                existing = self._trigger_repo._get_by_name(session, workspace_id=trigger.workspace_id, name=name, include_deleted=False)
                if existing:
                    raise ResourceAlreadyExistsError(
                        resource_name="trigger",
                        conflicting_field="name",
                        message=f"Trigger with name '{name}' already exists in this workspace"
                    )
        
        if config is not None and not isinstance(config, dict):
            raise InvalidInputError(field_name="config", message="Config must be a dictionary")
        
        # Validate input mapping if provided
        if input_mapping is not None:
            self._validate_input_mapping(input_mapping)
        
        update_data = {}
        if name is not None:
            update_data['name'] = name
        if description is not None:
            update_data['description'] = description
        if trigger_type is not None:
            update_data['trigger_type'] = trigger_type
        if config is not None:
            update_data['config'] = config
        if input_mapping is not None:
            update_data['input_mapping'] = input_mapping
        if is_enabled is not None:
            update_data['is_enabled'] = is_enabled
        
        if update_data:
            update_data['updated_by'] = updated_by
            self._trigger_repo._update(
                session,
                record_id=trigger_id,
                **update_data
            )
        
        # Refresh trigger
        trigger = self._trigger_repo._get_by_id(session, record_id=trigger_id, include_deleted=False)
        
        return self._get_trigger_dict(trigger)

    @with_transaction(manager=None)
    def delete_trigger(
        self,
        session,
        *,
        trigger_id: str,
        workspace_id: str
    ) -> Dict[str, Any]:
        """Delete trigger"""
        trigger = self._trigger_repo._get_by_id(session, record_id=trigger_id, include_deleted=False)
        if not trigger:
            raise ResourceNotFoundError(resource_name="trigger", resource_id=trigger_id)
        
        if trigger.workspace_id != workspace_id:
            raise ResourceNotFoundError(
                resource_name="trigger",
                message="Trigger not found in this workspace"
            )
        
        self._trigger_repo._delete(session, record_id=trigger_id)
        
        return {
            "deleted": True,
            "trigger_id": trigger_id
        }

    @with_readonly_session(manager=None)
    def get_all_triggers(
        self,
        session,
        *,
        workspace_id: str,
        page: int = 1,
        page_size: int = 100,
        order_by: Optional[str] = None,
        order_desc: bool = False,
        include_deleted: bool = False,
        workflow_id: Optional[str] = None,
        trigger_type: Optional[TriggerType] = None,
        is_enabled: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Get all triggers with pagination"""
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
        if workflow_id:
            filter_params.add_equality_filter('workflow_id', workflow_id)
        if trigger_type:
            filter_params.add_equality_filter('trigger_type', trigger_type)
        if is_enabled is not None:
            filter_params.add_equality_filter('is_enabled', is_enabled)
        
        result = self._trigger_repo._paginate(
            session,
            pagination_params=pagination_params,
            filter_params=filter_params
        )
        
        items = [self._get_trigger_dict(trigger) for trigger in result.items]
        
        return {
            "items": items,
            "metadata": result.metadata.to_dict()
        }

