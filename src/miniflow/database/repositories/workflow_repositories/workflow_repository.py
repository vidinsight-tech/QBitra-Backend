from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from sqlalchemy.sql import select

from ..base_repository import BaseRepository
from ...models.workflow_models.workflow_model import Workflow
from ...models.enums import WorkflowStatus


class WorkflowRepository(BaseRepository[Workflow]):    
    def __init__(self):
        super().__init__(Workflow)

    @BaseRepository._handle_db_exceptions
    def _get_by_name(
        self,
        session: Session,
        *,
        workspace_id: str,
        name: str,
        include_deleted: bool = False
    ) -> Optional[Workflow]:
        """Get workflow by workspace_id and name"""
        query = select(Workflow).where(
            Workflow.workspace_id == workspace_id,
            Workflow.name == name
        )
        query = self._apply_soft_delete_filter(query, include_deleted)
        return session.execute(query).scalar_one_or_none()