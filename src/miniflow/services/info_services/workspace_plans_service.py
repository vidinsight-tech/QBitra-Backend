from typing import Optional, Dict, List, Any

from src.miniflow.database import RepositoryRegistry, with_transaction, with_readonly_session
from src.miniflow.database.utils.pagination_params import PaginationParams
from src.miniflow.core.exceptions import (
    ResourceNotFoundError,
    ResourceAlreadyExistsError,
    InvalidInputError,
)


class WorkspacePlansService:

    def __init__(self):
        self._registry = RepositoryRegistry()
        self.workspace_plans_repository = self._registry.workspace_plans_repository
        self._workspace_repo = self._registry.workspace_repository

    @with_transaction(manager=None)
    def create_plan(
        self,
        session,
        *,
        name: str,
        display_name: str,
        description: Optional[str] = None,
        is_popular: bool = False,
        display_order: int = 0,
        max_members_per_workspace: int,
        max_workflows_per_workspace: int,
        max_custom_scripts_per_workspace: Optional[int] = None,
        storage_limit_mb_per_workspace: int,
        max_file_size_mb_per_workspace: int,
        monthly_execution_limit: int,
        max_concurrent_executions: int,
        can_use_custom_scripts: bool = False,
        can_use_api_access: bool = False,
        can_use_webhooks: bool = False,
        can_use_scheduling: bool = False,
        can_export_data: bool = False,
        max_api_keys_per_workspace: Optional[int] = None,
        api_rate_limit_per_minute: Optional[int] = None,
        api_rate_limit_per_hour: Optional[int] = None,
        api_rate_limit_per_day: Optional[int] = None,
        monthly_price_usd: float,
        yearly_price_usd: Optional[float] = None,
        price_per_extra_member_usd: float = 0.0,
        price_per_extra_workflow_usd: float = 0.0,
        features: Optional[List[Dict[str, Any]]] = None,
        created_by: str,
    ) -> Dict[str, Any]:
        # Validate inputs
        if not name or not name.strip():
            raise InvalidInputError(field_name="name", message="Plan name cannot be empty")
        if not display_name or not display_name.strip():
            raise InvalidInputError(field_name="display_name", message="Display name cannot be empty")
        
        # Check if name already exists
        existing_plan = self.workspace_plans_repository._get_by_name(session, name=name)
        if existing_plan:
            raise ResourceAlreadyExistsError(
                resource_name="workspace_plan",
                conflicting_field="name",
                message=f"Plan with name '{name}' already exists"
            )
        
        # Create plan
        plan = self.workspace_plans_repository._create(
            session,
            name=name,
            display_name=display_name,
            description=description,
            is_popular=is_popular,
            display_order=display_order,
            max_members_per_workspace=max_members_per_workspace,
            max_workflows_per_workspace=max_workflows_per_workspace,
            max_custom_scripts_per_workspace=max_custom_scripts_per_workspace,
            storage_limit_mb_per_workspace=storage_limit_mb_per_workspace,
            max_file_size_mb_per_workspace=max_file_size_mb_per_workspace,
            monthly_execution_limit=monthly_execution_limit,
            max_concurrent_executions=max_concurrent_executions,
            can_use_custom_scripts=can_use_custom_scripts,
            can_use_api_access=can_use_api_access,
            can_use_webhooks=can_use_webhooks,
            can_use_scheduling=can_use_scheduling,
            can_export_data=can_export_data,
            max_api_keys_per_workspace=max_api_keys_per_workspace,
            api_rate_limit_per_minute=api_rate_limit_per_minute,
            api_rate_limit_per_hour=api_rate_limit_per_hour,
            api_rate_limit_per_day=api_rate_limit_per_day,
            monthly_price_usd=monthly_price_usd,
            yearly_price_usd=yearly_price_usd,
            price_per_extra_member_usd=price_per_extra_member_usd,
            price_per_extra_workflow_usd=price_per_extra_workflow_usd,
            features=features or [],
            created_by=created_by,
        )
        
        return {
            "id": plan.id,
        }

    @with_readonly_session(manager=None)
    def get_plan(
        self,
        session,
        *,
        plan_id: str,
    ) -> Dict[str, Any]:
        plan = self.workspace_plans_repository._get_by_id(session, record_id=plan_id, include_deleted=False)
        if not plan:
            raise ResourceNotFoundError(resource_name="workspace_plan", resource_id=plan_id)
        
        return plan.to_dict()

    @with_readonly_session(manager=None)
    def get_plan_by_name(
        self,
        session,
        *,
        name: str,
    ) -> Dict[str, Any]:
        plan = self.workspace_plans_repository._get_by_name(session, name=name)
        if not plan:
            raise ResourceNotFoundError(
                resource_name="workspace_plan",
                message=f"Plan with name '{name}' not found"
            )
        
        return plan.to_dict()

    @with_transaction(manager=None)
    def update_plan(
        self,
        session,
        *,
        plan_id: str,
        name: Optional[str] = None,
        display_name: Optional[str] = None,
        description: Optional[str] = None,
        is_popular: Optional[bool] = None,
        display_order: Optional[int] = None,
        max_members_per_workspace: Optional[int] = None,
        max_workflows_per_workspace: Optional[int] = None,
        max_custom_scripts_per_workspace: Optional[int] = None,
        storage_limit_mb_per_workspace: Optional[int] = None,
        max_file_size_mb_per_workspace: Optional[int] = None,
        monthly_execution_limit: Optional[int] = None,
        max_concurrent_executions: Optional[int] = None,
        can_use_custom_scripts: Optional[bool] = None,
        can_use_api_access: Optional[bool] = None,
        can_use_webhooks: Optional[bool] = None,
        can_use_scheduling: Optional[bool] = None,
        can_export_data: Optional[bool] = None,
        max_api_keys_per_workspace: Optional[int] = None,
        api_rate_limit_per_minute: Optional[int] = None,
        api_rate_limit_per_hour: Optional[int] = None,
        api_rate_limit_per_day: Optional[int] = None,
        monthly_price_usd: Optional[float] = None,
        yearly_price_usd: Optional[float] = None,
        price_per_extra_member_usd: Optional[float] = None,
        price_per_extra_workflow_usd: Optional[float] = None,
        features: Optional[List[Dict[str, Any]]] = None,
        updated_by: str,
    ) -> Dict[str, Any]:
        plan = self.workspace_plans_repository._get_by_id(session, record_id=plan_id, include_deleted=False)
        if not plan:
            raise ResourceNotFoundError(resource_name="workspace_plan", resource_id=plan_id)
        
        # Validate name if provided
        if name is not None:
            if not name or not name.strip():
                raise InvalidInputError(field_name="name", message="Plan name cannot be empty")
            if name != plan.name:
                existing_plan = self.workspace_plans_repository._get_by_name(session, name=name)
                if existing_plan:
                    raise ResourceAlreadyExistsError(
                        resource_name="workspace_plan",
                        conflicting_field="name",
                        message=f"Plan with name '{name}' already exists"
                    )
                plan.name = name
        
        # Update fields
        update_fields = [
            "display_name", "description", "is_popular", "display_order",
            "max_members_per_workspace", "max_workflows_per_workspace",
            "max_custom_scripts_per_workspace", "storage_limit_mb_per_workspace",
            "max_file_size_mb_per_workspace", "monthly_execution_limit",
            "max_concurrent_executions", "can_use_custom_scripts",
            "can_use_api_access", "can_use_webhooks", "can_use_scheduling",
            "can_export_data", "max_api_keys_per_workspace",
            "api_rate_limit_per_minute", "api_rate_limit_per_hour",
            "api_rate_limit_per_day", "monthly_price_usd", "yearly_price_usd",
            "price_per_extra_member_usd", "price_per_extra_workflow_usd", "features"
        ]
        
        for field in update_fields:
            value = locals().get(field)
            if value is not None:
                setattr(plan, field, value)
        
        plan.updated_by = updated_by
        session.flush()
        
        return plan.to_dict()

    @with_transaction(manager=None)
    def delete_plan(
        self,
        session,
        *,
        plan_id: str,
    ):
        plan = self.workspace_plans_repository._get_by_id(session, record_id=plan_id, include_deleted=False)
        if not plan:
            raise ResourceNotFoundError(resource_name="workspace_plan", resource_id=plan_id)
        
        # Check if plan is used by workspaces
        workspace_count = self._workspace_repo._count_by_plan_id(session, plan_id=plan_id, include_deleted=False)
        if workspace_count > 0:
            raise InvalidInputError(
                field_name="plan_id",
                message=f"Cannot delete plan that is used by {workspace_count} workspace(s). Please change workspace plans first."
            )
        
        self.workspace_plans_repository._delete(session, record_id=plan_id)
        
        return {
            "deleted": True,
            "plan_id": plan_id
        }

    @with_readonly_session(manager=None)
    def get_all_plans_with_pagination(
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
        
        result = self.workspace_plans_repository._paginate(session, pagination_params=pagination_params)
        
        items = [plan.to_dict() for plan in result.items]
        
        return {
            "items": items,
            "metadata": result.metadata.to_dict()
        }

    @with_transaction(manager=None)
    def seed_plan(self, session, *, plans_data: List[Dict]):
        """Seed plans (legacy method for backward compatibility)"""
        stats = {"created": 0, "skipped": 0, "updated": 0}

        for plan_data in plans_data:
            plan_name = plan_data.get("name")
            if not plan_name:
                continue

            existing_plan = self.workspace_plans_repository._get_by_name(session, name=plan_name)

            if existing_plan:
                stats["skipped"] += 1
            else:
                self.workspace_plans_repository._create(session, **plan_data)
                stats["created"] += 1

        return stats