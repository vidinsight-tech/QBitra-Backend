from typing import List, Optional
from sqlalchemy import select, func, and_
from sqlalchemy.orm import Session

from ..base_repository import BaseRepository
from ...models.resource_models.file_model import File


class FileRepository(BaseRepository[File]):
    """Repository for File operations"""
    
    def __init__(self):
        super().__init__(File)

    @BaseRepository._handle_db_exceptions
    def _get_by_name(self, session: Session, workspace_id: str, name: str, include_deleted: bool = False) -> Optional[File]:
        query = select(File).where(
            and_(
                File.workspace_id == workspace_id,
                File.name == name
            )
        )
        query = self._apply_soft_delete_filter(query, include_deleted)
        return session.execute(query).scalar_one_or_none()