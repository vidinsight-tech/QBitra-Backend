from typing import List, Union, Optional
from sqlalchemy.orm import Session
from sqlalchemy.sql import select

from ..base_repository import BaseRepository
from ...models.resource_models.database_model import Database
from ...models.enums import DatabaseType


class DatabaseRepository(BaseRepository[Database]):
    """Repository for Database operations"""
    
    def __init__(self):
        super().__init__(Database)

    @BaseRepository._handle_db_exceptions
    def _get_by_name(self, session: Session, workspace_id: str, name: str, include_deleted: bool = False) -> Optional[Database]:
        query = select(Database).where(Database.workspace_id == workspace_id, Database.name == name)
        query = self._apply_soft_delete_filter(query, include_deleted)
        return session.execute(query).scalar_one_or_none()

    @BaseRepository._handle_db_exceptions
    def _get_by_connection_string(self, session: Session, connection_string: str) -> Optional[Database]:
        query = select(Database).where(Database.connection_string == connection_string)
        query = self._apply_soft_delete_filter(query)
        return session.execute(query).scalar_one_or_none()