from typing import List, Union, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..base_repository import BaseRepository
from ...models.resource_models.credential_model import Credential
from ...models.enums import CredentialType


class CredentialRepository(BaseRepository[Credential]):
    def __init__(self):
        super().__init__(Credential)

    @BaseRepository._handle_db_exceptions
    def _get_by_name(
        self,
        session: Session,
        *,
        workspace_id: str,
        name: str,
        include_deleted: bool = False
    ) -> Optional[Credential]:
        """Get credential by workspace_id and name."""
        query = select(Credential).where(
            Credential.workspace_id == workspace_id,
            Credential.name == name
        )
        query = self._apply_soft_delete_filter(query, include_deleted)
        return session.execute(query).scalar_one_or_none()

    