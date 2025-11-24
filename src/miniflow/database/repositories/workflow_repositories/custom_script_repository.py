from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.sql import select
from sqlalchemy import and_
from ..base_repository import BaseRepository
from ...models.workflow_models.custom_script_model import CustomScript
from ...utils.filter_params import FilterParams


class CustomScriptRepository(BaseRepository[CustomScript]): 
    def __init__(self):
        super().__init__(CustomScript)

    @BaseRepository._handle_db_exceptions
    def _get_by_name(
        self,
        session: Session,
        *,
        workspace_id: str,
        name: str,
        include_deleted: bool = False
    ) -> Optional[CustomScript]:
        """Get custom script by workspace_id and name"""
        query = select(CustomScript).where(
            CustomScript.workspace_id == workspace_id,
            CustomScript.name == name
        )
        query = self._apply_soft_delete_filter(query, include_deleted)
        return session.execute(query).scalar_one_or_none()

    @BaseRepository._handle_db_exceptions
    def _get_by_name_and_category_and_subcategory(
        self,
        session: Session,
        *,
        workspace_id: str,
        name: str,
        category: Optional[str] = None,
        subcategory: Optional[str] = None,
        include_deleted: bool = False
    ) -> Optional[CustomScript]:
        """Get custom script by workspace_id, name, category and subcategory"""
        conditions = [
            CustomScript.workspace_id == workspace_id,
            CustomScript.name == name
        ]
        if category is not None:
            conditions.append(CustomScript.category == category)
        else:
            conditions.append(CustomScript.category.is_(None))
        
        if subcategory is not None:
            conditions.append(CustomScript.subcategory == subcategory)
        else:
            conditions.append(CustomScript.subcategory.is_(None))
        
        query = select(CustomScript).where(and_(*conditions))
        query = self._apply_soft_delete_filter(query, include_deleted)
        return session.execute(query).scalar_one_or_none()