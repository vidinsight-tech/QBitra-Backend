from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from sqlalchemy.sql import select

from ..base_repository import BaseRepository
from ...models.workflow_models.trigger_model import Trigger


class TriggerRepository(BaseRepository[Trigger]):    
    def __init__(self):
        super().__init__(Trigger)

    @BaseRepository._handle_db_exceptions
    def _get_by_name(
        self,
        session: Session,
        *,
        workspace_id: str,
        name: str,
        include_deleted: bool = False
    ) -> Optional[Trigger]:
        """Get trigger by workspace_id and name"""
        query = select(Trigger).where(
            Trigger.workspace_id == workspace_id,
            Trigger.name == name
        )
        query = self._apply_soft_delete_filter(query, include_deleted)
        return session.execute(query).scalar_one_or_none()