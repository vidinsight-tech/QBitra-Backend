"""
WorkspacePlan Repository - Plan yönetimi için repository.

Kullanım:
    >>> from miniflow.repository import WorkspacePlanRepository
    >>> plan_repo = WorkspacePlanRepository()
    >>> plan = plan_repo.get_by_name(session, "pro")
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Dict, Any
from sqlalchemy.orm import Session

from miniflow.database.repository.advanced import AdvancedRepository
from miniflow.database.repository.base import handle_db_exceptions

if TYPE_CHECKING:
    from miniflow.models import WorkspacePlan


class WorkspacePlanRepository(AdvancedRepository):
    """Plan yönetimi için repository."""
    
    def __init__(self):
        from miniflow.models import WorkspacePlan
        super().__init__(WorkspacePlan)
    
    # =========================================================================
    # LOOKUP METHODS
    # =========================================================================
    
    @handle_db_exceptions
    def get_by_name(self, session: Session, name: str) -> Optional[WorkspacePlan]:
        """Plan adıyla getirir."""
        return session.query(self.model).filter(
            self.model.name == name
        ).first()
    
    # =========================================================================
    # LIMIT METHODS
    # =========================================================================
    
    @handle_db_exceptions
    def get_monthly_limits(self, session: Session, plan_id: str) -> Dict[str, Any]:
        """Aylık execution limitlerini döndürür."""
        plan = self.get_by_id(session, plan_id)
        if not plan:
            return {}
        
        return {
            "monthly_execution_limit": plan.monthly_execution_limit,
            "max_concurrent_executions": plan.max_concurrent_executions
        }
    
    @handle_db_exceptions
    def get_limits(self, session: Session, plan_id: str) -> Dict[str, Any]:
        """Genel limitleri döndürür (üye, workflow, storage)."""
        plan = self.get_by_id(session, plan_id)
        if not plan:
            return {}
        
        return {
            "member_limit": plan.member_limit,
            "workflow_limit": plan.workflow_limit,
            "nodes_per_workflow_limit": plan.nodes_per_workflow_limit,
            "storage_limit_mb": plan.storage_limit_mb,
            "max_file_size_mb": plan.max_file_size_mb
        }
    
    @handle_db_exceptions
    def get_feature_limits(self, session: Session, plan_id: str) -> Dict[str, Any]:
        """Özellik limitlerini döndürür (script, API, webhook)."""
        plan = self.get_by_id(session, plan_id)
        if not plan:
            return {}
        
        return {
            "custom_script_limit": plan.custom_script_limit,
            "api_key_limit": plan.api_key_limit
        }
    
    @handle_db_exceptions
    def get_api_limits(self, session: Session, plan_id: str) -> Dict[str, Any]:
        """API rate limitlerini döndürür."""
        plan = self.get_by_id(session, plan_id)
        if not plan:
            return {}
        
        return {
            "api_key_limit": plan.api_key_limit
        }
    
    @handle_db_exceptions
    def get_pricing(self, session: Session, plan_id: str) -> Dict[str, Any]:
        """Fiyatlandırma bilgilerini döndürür."""
        plan = self.get_by_id(session, plan_id)
        if not plan:
            return {}
        
        return {
            "name": plan.name,
            "price_monthly": getattr(plan, "price_monthly", None),
            "price_yearly": getattr(plan, "price_yearly", None)
        }

