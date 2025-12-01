from typing import Optional, Dict, Any, List

from src.miniflow.database import RepositoryRegistry, with_transaction, with_readonly_session
from src.miniflow.database.utils.pagination_params import PaginationParams
from src.miniflow.database.utils.filter_params import FilterParams
from src.miniflow.core.exceptions import (
    ResourceNotFoundError,
    ResourceAlreadyExistsError,
    InvalidInputError,
)


class NodeService:
    def __init__(self):
        self._registry = RepositoryRegistry()
        self._node_repo = self._registry.node_repository
        self._workflow_repo = self._registry.workflow_repository
        self._script_repo = self._registry.script_repository
        self._custom_script_repo = self._registry.custom_script_repository
        self._user_repo = self._registry.user_repository

    def _get_node_dict(self, node) -> Dict[str, Any]:
        """Helper method to convert node to dict"""
        return {
            "id": node.id,
            "name": node.name,
            "description": node.description,
            "workflow_id": node.workflow_id,
            "script_id": node.script_id,
            "custom_script_id": node.custom_script_id,
            "input_params": node.input_params or {},
            "output_params": node.output_params or {},
            "meta_data": node.meta_data or {},
            "max_retries": node.max_retries,
            "timeout_seconds": node.timeout_seconds,
            "created_at": node.created_at.isoformat() if node.created_at else None,
            "updated_at": node.updated_at.isoformat() if node.updated_at else None,
            "created_by": node.created_by,
            "updated_by": node.updated_by,
        }

    def _map_schema_type_to_frontend_type(self, schema_type: str) -> str:
        """
        Schema type'ı frontend input type'a map eder.
        
        Args:
            schema_type: Schema'daki type (string, number, boolean, array, object)
        
        Returns:
            Frontend input type (text, number, checkbox, textarea, select, radio)
        """
        type_mapping = {
            "string": "text",
            "number": "number",
            "integer": "number",
            "float": "number",
            "boolean": "checkbox",
            "array": "textarea",  # JSON array için
            "object": "textarea",  # JSON object için
            "email": "email",
            "url": "url",
            "password": "password",
        }
        return type_mapping.get(schema_type.lower(), "text")

    def _convert_schema_to_frontend_format(
        self,
        input_schema: Dict[str, Any],
        existing_input_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Script'in input_schema'sını frontend formatına dönüştürür.
        
        Args:
            input_schema: Script'in input_schema'sı
            existing_input_params: Varsa mevcut node'un input_params'i (override için)
        
        Returns:
            Frontend formatında input_mapping benzeri yapı
        """
        frontend_params = {}
        order = 0
        
        for param_name, param_schema in input_schema.items():
            if not isinstance(param_schema, dict):
                # Eğer schema sadece type string ise, dict'e çevir
                if isinstance(param_schema, str):
                    param_schema = {"type": param_schema}
                else:
                    continue
            
            # Mevcut değerleri kontrol et (override)
            existing_value = None
            if existing_input_params and param_name in existing_input_params:
                existing_param = existing_input_params[param_name]
                if isinstance(existing_param, dict):
                    existing_value = existing_param.get('value')
                else:
                    existing_value = existing_param
            
            # Frontend tipini belirle (schema type'dan)
            schema_type = param_schema.get('type', 'string')
            front_type = self._map_schema_type_to_frontend_type(schema_type)
            
            # Enum varsa select/radio yap
            if 'enum' in param_schema and param_schema['enum']:
                if front_type == "text":
                    front_type = "select"  # Default olarak select
            
            # Frontend formatını oluştur
            frontend_params[param_name] = {
                "front": {
                    "order": order,
                    "type": front_type,
                    "values": param_schema.get('enum'),  # Select/radio için
                    "placeholder": param_schema.get('placeholder') or param_schema.get('description') or f"Enter {param_name}..."
                },
                "type": schema_type,  # Backend type
                "default_value": existing_value if existing_value is not None else param_schema.get('default'),
                "value": existing_value,  # Runtime değeri
                "required": param_schema.get('required', False),
                "description": param_schema.get('description')
            }
            order += 1
        
        return frontend_params

    def _validate_and_convert_frontend_params(
        self,
        frontend_params: Dict[str, Any],
        script_input_schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Frontend form verilerini validate eder ve backend formatına dönüştürür.
        
        Frontend formatı:
        {
            "param1": {
                "front": {...},
                "type": "string",
                "value": "actual_value",
                ...
            }
        }
        
        Backend formatı (node.input_params):
        {
            "param1": {
                "type": "string",
                "value": "actual_value",
                "default_value": "...",
                "required": true
            }
        }
        """
        validated_params = {}
        
        # Önce script schema'daki tüm required parametrelerin frontend_params'te olduğunu kontrol et
        for param_name, schema_def in script_input_schema.items():
            # Eğer schema sadece type string ise, dict'e çevir
            if isinstance(schema_def, str):
                schema_def = {"type": schema_def}
            
            # Required parametre kontrolü
            if schema_def.get('required', False):
                if param_name not in frontend_params:
                    raise InvalidInputError(
                        field_name=param_name,
                        message=f"Required parameter '{param_name}' is missing"
                    )
        
        # Şimdi frontend_params'teki parametreleri validate et ve dönüştür
        for param_name, param_data in frontend_params.items():
            # Script schema'da bu parametre var mı kontrol et
            if param_name not in script_input_schema:
                raise InvalidInputError(
                    field_name="input_params",
                    message=f"Parameter '{param_name}' is not defined in script's input_schema"
                )
            
            schema_def = script_input_schema[param_name]
            # Eğer schema sadece type string ise, dict'e çevir
            if isinstance(schema_def, str):
                schema_def = {"type": schema_def}
            
            # Value'yu al
            value = None
            if isinstance(param_data, dict):
                value = param_data.get('value')
            else:
                value = param_data
            
            # Required kontrolü
            if schema_def.get('required', False) and (value is None or value == ''):
                raise InvalidInputError(
                    field_name=param_name,
                    message=f"Parameter '{param_name}' is required"
                )
            
            # Type validation
            param_type = schema_def.get('type', 'string')
            if value is not None:
                self._validate_param_type(param_name, value, param_type, schema_def)
            
            # Backend formatına dönüştür
            validated_params[param_name] = {
                "type": param_type,
                "value": value,
                "default_value": param_data.get('default_value') if isinstance(param_data, dict) else None,
                "required": schema_def.get('required', False),
                "description": param_data.get('description') if isinstance(param_data, dict) else schema_def.get('description')
            }
        
        return validated_params

    def _validate_param_type(self, param_name: str, value: Any, param_type: str, schema_def: Optional[Dict[str, Any]] = None) -> None:
        """
        Parametre tipini validate eder.
        
        Args:
            param_name: Parametre adı
            value: Değer
            param_type: Beklenen tip
            schema_def: Schema tanımı (enum kontrolü için)
        
        Raises:
            InvalidInputError: Tip uyumsuzluğu varsa
        """
        type_lower = param_type.lower()
        
        # Enum validation
        if schema_def and 'enum' in schema_def and schema_def['enum']:
            if value not in schema_def['enum']:
                raise InvalidInputError(
                    field_name=param_name,
                    message=f"Parameter '{param_name}' must be one of {schema_def['enum']}, got {value}"
                )
            return  # Enum kontrolü geçtiyse tip kontrolüne gerek yok
        
        if type_lower in ('string', 'text'):
            if not isinstance(value, str):
                raise InvalidInputError(
                    field_name=param_name,
                    message=f"Parameter '{param_name}' must be a string, got {type(value).__name__}"
                )
        elif type_lower in ('number', 'integer', 'float'):
            if not isinstance(value, (int, float)):
                raise InvalidInputError(
                    field_name=param_name,
                    message=f"Parameter '{param_name}' must be a number, got {type(value).__name__}"
                )
        elif type_lower == 'boolean':
            if not isinstance(value, bool):
                raise InvalidInputError(
                    field_name=param_name,
                    message=f"Parameter '{param_name}' must be a boolean, got {type(value).__name__}"
                )
        # array ve object için JSON string kontrolü yapılabilir ama şimdilik skip

    @with_transaction(manager=None)
    def create_node(
        self,
        session,
        *,
        workflow_id: str,
        name: str,
        script_id: Optional[str] = None,
        custom_script_id: Optional[str] = None,
        description: Optional[str] = None,
        input_params: Optional[Dict[str, Any]] = None,
        output_params: Optional[Dict[str, Any]] = None,
        meta_data: Optional[Dict[str, Any]] = None,
        max_retries: int = 3,
        timeout_seconds: int = 300,
        created_by: str,
    ) -> Dict[str, Any]:
        """Create a new node"""
        # Validate inputs
        if not name or not name.strip():
            raise InvalidInputError(field_name="name", message="Node name cannot be empty")
        
        if not workflow_id or not workflow_id.strip():
            raise InvalidInputError(field_name="workflow_id", message="Workflow ID cannot be empty")
        
        if not created_by or not created_by.strip():
            raise InvalidInputError(field_name="created_by", message="Created by cannot be empty")
        
        if max_retries < 0:
            raise InvalidInputError(field_name="max_retries", message="Max retries must be greater than or equal to 0")
        
        if timeout_seconds <= 0:
            raise InvalidInputError(field_name="timeout_seconds", message="Timeout seconds must be greater than 0")
        
        # Verify workflow exists
        workflow = self._workflow_repo._get_by_id(session, record_id=workflow_id, include_deleted=False)
        if not workflow:
            raise ResourceNotFoundError(resource_name="workflow", resource_id=workflow_id)
        
        # Validate user exists
        user = self._user_repo._get_by_id(session, record_id=created_by, include_deleted=False)
        if not user:
            raise ResourceNotFoundError(resource_name="user", resource_id=created_by)
        
        # Check if node name already exists in workflow
        existing = self._node_repo._get_by_name(session, workflow_id=workflow_id, name=name, include_deleted=False)
        if existing:
            raise ResourceAlreadyExistsError(
                resource_name="node",
                conflicting_field="name",
                message=f"Node with name '{name}' already exists in this workflow"
            )
        
        # Validate script_id XOR custom_script_id (exactly one must be provided)
        if not script_id and not custom_script_id:
            raise InvalidInputError(field_name="script", message="Either script_id or custom_script_id must be provided")
        if script_id and custom_script_id:
            raise InvalidInputError(field_name="script", message="Only one of script_id or custom_script_id can be provided")
        
        script = None
        custom_script = None
        
        # Verify script exists if provided
        if script_id:
            script = self._script_repo._get_by_id(session, record_id=script_id, include_deleted=False)
            if not script:
                raise ResourceNotFoundError(resource_name="script", resource_id=script_id)
        
        # Verify custom_script exists if provided
        if custom_script_id:
            custom_script = self._custom_script_repo._get_by_id(session, record_id=custom_script_id, include_deleted=False)
            if not custom_script:
                raise ResourceNotFoundError(resource_name="custom_script", resource_id=custom_script_id)
            # Verify custom_script belongs to same workspace as workflow
            if custom_script.workspace_id != workflow.workspace_id:
                raise InvalidInputError(
                    field_name="custom_script_id",
                    message="Custom script does not belong to the same workspace as workflow"
                )
        
        # Validate input_params if provided and script exists
        validated_input_params = input_params or {}
        executable_script = script or custom_script
        if executable_script and input_params:
            validated_input_params = self._validate_and_convert_frontend_params(
                frontend_params=input_params,
                script_input_schema=executable_script.input_schema or {}
            )
        
        node = self._node_repo._create(
            session,
            workflow_id=workflow_id,
            name=name,
            script_id=script_id,
            custom_script_id=custom_script_id,
            description=description,
            input_params=validated_input_params,
            output_params=output_params or {},
            meta_data=meta_data or {},
            max_retries=max_retries,
            timeout_seconds=timeout_seconds,
            created_by=created_by,
        )
        
        return self._get_node_dict(node)

    @with_readonly_session(manager=None)
    def get_node(
        self,
        session,
        *,
        node_id: str,
        workflow_id: str
    ) -> Dict[str, Any]:
        """Get node by ID"""
        node = self._node_repo._get_by_id(session, record_id=node_id, include_deleted=False)
        if not node:
            raise ResourceNotFoundError(resource_name="node", resource_id=node_id)
        
        if node.workflow_id != workflow_id:
            raise ResourceNotFoundError(
                resource_name="node",
                message="Node not found in this workflow"
            )
        
        return self._get_node_dict(node)

    @with_readonly_session(manager=None)
    def get_node_form_schema(
        self,
        session,
        *,
        node_id: str,
        workflow_id: str
    ) -> Dict[str, Any]:
        """
        Node'un frontend form şemasını döndürür.
        Script'in input_schema'sından türetilir ve node'un mevcut input_params'i ile merge edilir.
        """
        node = self._node_repo._get_by_id(session, record_id=node_id, include_deleted=False)
        if not node:
            raise ResourceNotFoundError(resource_name="node", resource_id=node_id)
        
        if node.workflow_id != workflow_id:
            raise ResourceNotFoundError(
                resource_name="node",
                message="Node not found in this workflow"
            )
        
        # Script'i güvenli bir şekilde al
        script = None
        if node.script_id:
            script = self._script_repo._get_by_id(session, record_id=node.script_id, include_deleted=False)
        elif node.custom_script_id:
            script = self._custom_script_repo._get_by_id(session, record_id=node.custom_script_id, include_deleted=False)
        
        if not script:
            raise InvalidInputError(
                field_name="node",
                message="Node has no associated script"
            )
        
        # Script'in input_schema'sını frontend formatına dönüştür
        frontend_schema = self._convert_schema_to_frontend_format(
            input_schema=script.input_schema or {},
            existing_input_params=node.input_params
        )
        
        return {
            "id": node.id,
            "node_name": node.name,
            "script_id": node.script_id,
            "custom_script_id": node.custom_script_id,
            "script_name": script.name,
            "script_type": "GLOBAL" if node.script_id else "CUSTOM",
            "form_schema": frontend_schema,
            "output_schema": script.output_schema or {}
        }

    @with_transaction(manager=None)
    def update_node(
        self,
        session,
        *,
        node_id: str,
        workflow_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        script_id: Optional[str] = None,
        custom_script_id: Optional[str] = None,
        input_params: Optional[Dict[str, Any]] = None,
        output_params: Optional[Dict[str, Any]] = None,
        meta_data: Optional[Dict[str, Any]] = None,
        max_retries: Optional[int] = None,
        timeout_seconds: Optional[int] = None,
        updated_by: str,
    ) -> Dict[str, Any]:
        """Update node"""
        node = self._node_repo._get_by_id(session, record_id=node_id, include_deleted=False)
        if not node:
            raise ResourceNotFoundError(resource_name="node", resource_id=node_id)
        
        if node.workflow_id != workflow_id:
            raise ResourceNotFoundError(
                resource_name="node",
                message="Node not found in this workflow"
            )
        
        # Validate user exists
        user = self._user_repo._get_by_id(session, record_id=updated_by, include_deleted=False)
        if not user:
            raise ResourceNotFoundError(resource_name="user", resource_id=updated_by)
        
        workflow = self._workflow_repo._get_by_id(session, record_id=node.workflow_id, include_deleted=False)
        
        # Validate inputs
        if name is not None:
            if not name.strip():
                raise InvalidInputError(field_name="name", message="Node name cannot be empty")
            # Check if name change would cause duplicate
            if name != node.name:
                existing = self._node_repo._get_by_name(session, workflow_id=node.workflow_id, name=name, include_deleted=False)
                if existing:
                    raise ResourceAlreadyExistsError(
                        resource_name="node",
                        conflicting_field="name",
                        message=f"Node with name '{name}' already exists in this workflow"
                    )
        
        if max_retries is not None and max_retries < 0:
            raise InvalidInputError(field_name="max_retries", message="Max retries must be greater than or equal to 0")
        
        if timeout_seconds is not None and timeout_seconds <= 0:
            raise InvalidInputError(field_name="timeout_seconds", message="Timeout seconds must be greater than 0")
        
        # Handle script_id and custom_script_id updates
        new_script_id = script_id if script_id is not None else node.script_id
        new_custom_script_id = custom_script_id if custom_script_id is not None else node.custom_script_id
        
        # Validate XOR constraint
        if new_script_id and new_custom_script_id:
            raise InvalidInputError(field_name="script", message="Only one of script_id or custom_script_id can be provided")
        if not new_script_id and not new_custom_script_id:
            raise InvalidInputError(field_name="script", message="Either script_id or custom_script_id must be provided")
        
        # Verify script exists if changed
        if script_id is not None and script_id != node.script_id:
            script = self._script_repo._get_by_id(session, record_id=script_id, include_deleted=False)
            if not script:
                raise ResourceNotFoundError(resource_name="script", resource_id=script_id)
        
        # Verify custom_script exists if changed
        if custom_script_id is not None and custom_script_id != node.custom_script_id:
            custom_script = self._custom_script_repo._get_by_id(session, record_id=custom_script_id, include_deleted=False)
            if not custom_script:
                raise ResourceNotFoundError(resource_name="custom_script", resource_id=custom_script_id)
            if custom_script.workspace_id != workflow.workspace_id:
                raise InvalidInputError(
                    field_name="custom_script_id",
                    message="Custom script does not belong to the same workspace as workflow"
                )
        
        # Validate input_params if provided
        validated_input_params = input_params
        if input_params is not None:
            # Get current or new script
            executable_script = None
            if script_id is not None:
                executable_script = self._script_repo._get_by_id(session, record_id=script_id, include_deleted=False)
            elif custom_script_id is not None:
                executable_script = self._custom_script_repo._get_by_id(session, record_id=custom_script_id, include_deleted=False)
            else:
                # Get current script
                if node.script_id:
                    executable_script = self._script_repo._get_by_id(session, record_id=node.script_id, include_deleted=False)
                elif node.custom_script_id:
                    executable_script = self._custom_script_repo._get_by_id(session, record_id=node.custom_script_id, include_deleted=False)
            
            if executable_script:
                validated_input_params = self._validate_and_convert_frontend_params(
                    frontend_params=input_params,
                    script_input_schema=executable_script.input_schema or {}
                )
            else:
                # Script yoksa input_params kullanılamaz
                raise InvalidInputError(
                    field_name="input_params",
                    message="Cannot set input_params without an associated script"
                )
        
        update_data = {}
        if name is not None:
            update_data['name'] = name
        if description is not None:
            update_data['description'] = description
        if script_id is not None:
            update_data['script_id'] = script_id
            update_data['custom_script_id'] = None  # Clear custom_script_id when script_id is set
        if custom_script_id is not None:
            update_data['custom_script_id'] = custom_script_id
            update_data['script_id'] = None  # Clear script_id when custom_script_id is set
        if input_params is not None:
            update_data['input_params'] = validated_input_params
        if output_params is not None:
            update_data['output_params'] = output_params
        if meta_data is not None:
            update_data['meta_data'] = meta_data
        if max_retries is not None:
            update_data['max_retries'] = max_retries
        if timeout_seconds is not None:
            update_data['timeout_seconds'] = timeout_seconds
        
        if update_data:
            update_data['updated_by'] = updated_by
            self._node_repo._update(
                session,
                record_id=node_id,
                **update_data
            )
        
        # Refresh node
        node = self._node_repo._get_by_id(session, record_id=node_id, include_deleted=False)
        
        return self._get_node_dict(node)

    @with_transaction(manager=None)
    def update_node_input_params(
        self,
        session,
        *,
        node_id: str,
        workflow_id: str,
        input_params: Dict[str, Any],
        updated_by: str,
    ) -> Dict[str, Any]:
        """
        Update only input_params of a node.
        Frontend'den gelen form verilerini validate eder ve node'un input_params'ine kaydeder.
        """
        # Validate input
        if not isinstance(input_params, dict):
            raise InvalidInputError(
                field_name="input_params",
                message="Input params must be a dictionary"
            )
        
        node = self._node_repo._get_by_id(session, record_id=node_id, include_deleted=False)
        if not node:
            raise ResourceNotFoundError(resource_name="node", resource_id=node_id)
        
        if node.workflow_id != workflow_id:
            raise ResourceNotFoundError(
                resource_name="node",
                message="Node not found in this workflow"
            )
        
        # Validate user exists
        user = self._user_repo._get_by_id(session, record_id=updated_by, include_deleted=False)
        if not user:
            raise ResourceNotFoundError(resource_name="user", resource_id=updated_by)
        
        # Script'i güvenli bir şekilde al
        script = None
        if node.script_id:
            script = self._script_repo._get_by_id(session, record_id=node.script_id, include_deleted=False)
        elif node.custom_script_id:
            script = self._custom_script_repo._get_by_id(session, record_id=node.custom_script_id, include_deleted=False)
        
        if not script:
            raise InvalidInputError(
                field_name="node",
                message="Node has no associated script"
            )
        
        # Frontend verilerini validate et ve dönüştür
        validated_params = self._validate_and_convert_frontend_params(
            frontend_params=input_params,
            script_input_schema=script.input_schema or {}
        )
        
        # Node'u güncelle
        self._node_repo._update(
            session,
            record_id=node_id,
            input_params=validated_params,
            updated_by=updated_by,
        )
        
        # Güncellenmiş node'u döndür
        node = self._node_repo._get_by_id(session, record_id=node_id, include_deleted=False)
        return self._get_node_dict(node)

    @with_transaction(manager=None)
    def delete_node(
        self,
        session,
        *,
        node_id: str,
        workflow_id: str
    ) -> Dict[str, Any]:
        """Delete node"""
        node = self._node_repo._get_by_id(session, record_id=node_id, include_deleted=False)
        if not node:
            raise ResourceNotFoundError(resource_name="node", resource_id=node_id)
        
        if node.workflow_id != workflow_id:
            raise ResourceNotFoundError(
                resource_name="node",
                message="Node not found in this workflow"
            )
        
        self._node_repo._delete(session, record_id=node_id)
        
        return {
            "deleted": True,
            "id": node_id
        }

    @with_readonly_session(manager=None)
    def get_all_nodes(
        self,
        session,
        *,
        workflow_id: str,
        page: int = 1,
        page_size: int = 100,
        order_by: Optional[str] = None,
        order_desc: bool = False,
        include_deleted: bool = False,
    ) -> Dict[str, Any]:
        """Get all nodes for a workflow with pagination"""
        # Verify workflow exists
        workflow = self._workflow_repo._get_by_id(session, record_id=workflow_id, include_deleted=False)
        if not workflow:
            raise ResourceNotFoundError(resource_name="workflow", resource_id=workflow_id)
        
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
        filter_params.add_equality_filter('workflow_id', workflow_id)
        
        result = self._node_repo._paginate(
            session,
            pagination_params=pagination_params,
            filter_params=filter_params
        )
        
        items = [self._get_node_dict(node) for node in result.items]
        
        return {
            "items": items,
            "metadata": result.metadata.to_dict()
        }

