from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.sql import select
from sqlalchemy import and_
from ..base_repository import BaseRepository
from ...models.workflow_models.script_model import Script
from ...utils.filter_params import FilterParams


class ScriptRepository(BaseRepository[Script]):    
    def __init__(self):
        super().__init__(Script)

    @BaseRepository._handle_db_exceptions
    def _get_by_name(
        self,
        session: Session,
        *,
        name: str,
        include_deleted: bool = False
    ) -> Optional[Script]:
        """Get script by name"""
        query = select(Script).where(Script.name == name)
        query = self._apply_soft_delete_filter(query, include_deleted)
        return session.execute(query).scalar_one_or_none()

    @BaseRepository._handle_db_exceptions
    def _get_by_name_and_category_and_subcategory(
        self,
        session: Session,
        *,
        name: str,
        category: str,
        subcategory: Optional[str] = None,
        include_deleted: bool = False
    ) -> Optional[Script]:
        """Get script by name, category and subcategory"""
        conditions = [
            Script.name == name,
            Script.category == category
        ]
        if subcategory is not None:
            conditions.append(Script.subcategory == subcategory)
        else:
            conditions.append(Script.subcategory.is_(None))
        
        query = select(Script).where(and_(*conditions))
        query = self._apply_soft_delete_filter(query, include_deleted)
        return session.execute(query).scalar_one_or_none()
