from typing import Optional, Dict, Any, List

from src.miniflow.database import RepositoryRegistry, with_transaction, with_readonly_session
from src.miniflow.database.utils.pagination_params import PaginationParams
from src.miniflow.database.utils.filter_params import FilterParams
from src.miniflow.core.exceptions import (
    ResourceNotFoundError,
    ResourceAlreadyExistsError,
    InvalidInputError,
)


class EdgeService:
    def __init__(self):
        self._registry = RepositoryRegistry()
        self._edge_repo = self._registry.edge_repository
        self._workflow_repo = self._registry.workflow_repository
        self._node_repo = self._registry.node_repository
        self._user_repo = self._registry.user_repository

    def _get_edge_dict(self, edge) -> Dict[str, Any]:
        """Helper method to convert edge to dict"""
        return {
            "id": edge.id,
            "workflow_id": edge.workflow_id,
            "from_node_id": edge.from_node_id,
            "to_node_id": edge.to_node_id,
            "created_at": edge.created_at.isoformat() if edge.created_at else None,
            "updated_at": edge.updated_at.isoformat() if edge.updated_at else None,
            "created_by": edge.created_by,
            "updated_by": edge.updated_by,
        }

    @with_transaction(manager=None)
    def create_edge(
        self,
        session,
        *,
        workflow_id: str,
        from_node_id: str,
        to_node_id: str,
        created_by: str,
    ) -> Dict[str, Any]:
        """Create a new edge"""
        # Validate inputs
        if not workflow_id or not workflow_id.strip():
            raise InvalidInputError(field_name="workflow_id", message="Workflow ID cannot be empty")
        
        if not from_node_id or not from_node_id.strip():
            raise InvalidInputError(field_name="from_node_id", message="From node ID cannot be empty")
        
        if not to_node_id or not to_node_id.strip():
            raise InvalidInputError(field_name="to_node_id", message="To node ID cannot be empty")
        
        if not created_by or not created_by.strip():
            raise InvalidInputError(field_name="created_by", message="Created by cannot be empty")
        
        # Check for self-loop (from_node_id == to_node_id)
        if from_node_id == to_node_id:
            raise InvalidInputError(field_name="edge", message="Edge cannot connect a node to itself")
        
        # Verify workflow exists
        workflow = self._workflow_repo._get_by_id(session, record_id=workflow_id, include_deleted=False)
        if not workflow:
            raise ResourceNotFoundError(resource_name="workflow", resource_id=workflow_id)
        
        # Validate user exists
        user = self._user_repo._get_by_id(session, record_id=created_by, include_deleted=False)
        if not user:
            raise ResourceNotFoundError(resource_name="user", resource_id=created_by)
        
        # Verify from_node exists and belongs to workflow
        from_node = self._node_repo._get_by_id(session, record_id=from_node_id, include_deleted=False)
        if not from_node:
            raise ResourceNotFoundError(resource_name="node", resource_id=from_node_id)
        if from_node.workflow_id != workflow_id:
            raise InvalidInputError(
                field_name="from_node_id",
                message="From node does not belong to this workflow"
            )
        
        # Verify to_node exists and belongs to workflow
        to_node = self._node_repo._get_by_id(session, record_id=to_node_id, include_deleted=False)
        if not to_node:
            raise ResourceNotFoundError(resource_name="node", resource_id=to_node_id)
        if to_node.workflow_id != workflow_id:
            raise InvalidInputError(
                field_name="to_node_id",
                message="To node does not belong to this workflow"
            )
        
        # Check if edge already exists
        existing = self._edge_repo._get_by_nodes(
            session,
            workflow_id=workflow_id,
            from_node_id=from_node_id,
            to_node_id=to_node_id,
            include_deleted=False
        )
        if existing:
            raise ResourceAlreadyExistsError(
                resource_name="edge",
                conflicting_field="nodes",
                message="Edge already exists between these nodes"
            )
        
        edge = self._edge_repo._create(
            session,
            workflow_id=workflow_id,
            from_node_id=from_node_id,
            to_node_id=to_node_id,
            created_by=created_by,
        )
        
        return self._get_edge_dict(edge)

    @with_readonly_session(manager=None)
    def get_edge(
        self,
        session,
        *,
        edge_id: str,
        workflow_id: str
    ) -> Dict[str, Any]:
        """Get edge by ID"""
        edge = self._edge_repo._get_by_id(session, record_id=edge_id, include_deleted=False)
        if not edge:
            raise ResourceNotFoundError(resource_name="edge", resource_id=edge_id)
        
        if edge.workflow_id != workflow_id:
            raise ResourceNotFoundError(
                resource_name="edge",
                message="Edge not found in this workflow"
            )
        
        return self._get_edge_dict(edge)

    @with_transaction(manager=None)
    def update_edge(
        self,
        session,
        *,
        edge_id: str,
        workflow_id: str,
        from_node_id: Optional[str] = None,
        to_node_id: Optional[str] = None,
        updated_by: str,
    ) -> Dict[str, Any]:
        """Update edge"""
        edge = self._edge_repo._get_by_id(session, record_id=edge_id, include_deleted=False)
        if not edge:
            raise ResourceNotFoundError(resource_name="edge", resource_id=edge_id)
        
        if edge.workflow_id != workflow_id:
            raise ResourceNotFoundError(
                resource_name="edge",
                message="Edge not found in this workflow"
            )
        
        # Validate user exists
        user = self._user_repo._get_by_id(session, record_id=updated_by, include_deleted=False)
        if not user:
            raise ResourceNotFoundError(resource_name="user", resource_id=updated_by)
        
        # Validate inputs
        if from_node_id is not None and not from_node_id.strip():
            raise InvalidInputError(field_name="from_node_id", message="From node ID cannot be empty")
        
        if to_node_id is not None and not to_node_id.strip():
            raise InvalidInputError(field_name="to_node_id", message="To node ID cannot be empty")
        
        new_from_node_id = from_node_id if from_node_id is not None else edge.from_node_id
        new_to_node_id = to_node_id if to_node_id is not None else edge.to_node_id
        
        # Check for self-loop
        if new_from_node_id == new_to_node_id:
            raise InvalidInputError(field_name="edge", message="Edge cannot connect a node to itself")
        
        # Verify nodes if changed
        if from_node_id is not None and from_node_id != edge.from_node_id:
            from_node = self._node_repo._get_by_id(session, record_id=from_node_id, include_deleted=False)
            if not from_node:
                raise ResourceNotFoundError(resource_name="node", resource_id=from_node_id)
            if from_node.workflow_id != edge.workflow_id:
                raise InvalidInputError(
                    field_name="from_node_id",
                    message="From node does not belong to this workflow"
                )
        
        if to_node_id is not None and to_node_id != edge.to_node_id:
            to_node = self._node_repo._get_by_id(session, record_id=to_node_id, include_deleted=False)
            if not to_node:
                raise ResourceNotFoundError(resource_name="node", resource_id=to_node_id)
            if to_node.workflow_id != edge.workflow_id:
                raise InvalidInputError(
                    field_name="to_node_id",
                    message="To node does not belong to this workflow"
                )
        
        # Check if edge already exists with new nodes
        if (from_node_id is not None or to_node_id is not None):
            existing = self._edge_repo._get_by_nodes(
                session,
                workflow_id=edge.workflow_id,
                from_node_id=new_from_node_id,
                to_node_id=new_to_node_id,
                include_deleted=False
            )
            if existing and existing.id != edge_id:
                raise ResourceAlreadyExistsError(
                    resource_name="edge",
                    conflicting_field="nodes",
                    message="Edge already exists between these nodes"
                )
        
        update_data = {}
        if from_node_id is not None:
            update_data['from_node_id'] = from_node_id
        if to_node_id is not None:
            update_data['to_node_id'] = to_node_id
        
        if update_data:
            update_data['updated_by'] = updated_by
            self._edge_repo._update(
                session,
                record_id=edge_id,
                **update_data
            )
        
        # Refresh edge
        edge = self._edge_repo._get_by_id(session, record_id=edge_id, include_deleted=False)
        
        return self._get_edge_dict(edge)

    @with_transaction(manager=None)
    def delete_edge(
        self,
        session,
        *,
        edge_id: str,
        workflow_id: str
    ) -> Dict[str, Any]:
        """Delete edge"""
        edge = self._edge_repo._get_by_id(session, record_id=edge_id, include_deleted=False)
        if not edge:
            raise ResourceNotFoundError(resource_name="edge", resource_id=edge_id)
        
        if edge.workflow_id != workflow_id:
            raise ResourceNotFoundError(
                resource_name="edge",
                message="Edge not found in this workflow"
            )
        
        self._edge_repo._delete(session, record_id=edge_id)
        
        return {
            "deleted": True,
            "id": edge_id
        }

    @with_readonly_session(manager=None)
    def get_all_edges(
        self,
        session,
        *,
        workflow_id: str,
        page: int = 1,
        page_size: int = 100,
        order_by: Optional[str] = None,
        order_desc: bool = False,
        include_deleted: bool = False,
        from_node_id: Optional[str] = None,
        to_node_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get all edges for a workflow with pagination"""
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
        if from_node_id:
            filter_params.add_equality_filter('from_node_id', from_node_id)
        if to_node_id:
            filter_params.add_equality_filter('to_node_id', to_node_id)
        
        result = self._edge_repo._paginate(
            session,
            pagination_params=pagination_params,
            filter_params=filter_params
        )
        
        items = [self._get_edge_dict(edge) for edge in result.items]
        
        return {
            "items": items,
            "metadata": result.metadata.to_dict()
        }

