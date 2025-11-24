from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.sql import select
from ..base_repository import BaseRepository
from ...models.resource_models.variable_model import Variable


class VariableRepository(BaseRepository[Variable]):
    """Repository for Variable operations"""
    
    def __init__(self):
        super().__init__(Variable)

    @BaseRepository._handle_db_exceptions
    def _get_by_key(self, session: Session, workspace_id: str, key: str, include_deleted: bool = False) -> Optional[Variable]:
        query = select(Variable).where(Variable.workspace_id == workspace_id, Variable.key == key)
        query = self._apply_soft_delete_filter(query, include_deleted)
        return session.execute(query).scalar_one_or_none()