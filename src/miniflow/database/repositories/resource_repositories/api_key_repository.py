from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.sql import select
from ..base_repository import BaseRepository
from ...models.resource_models.api_key_model import ApiKey
from src.miniflow.utils.helpers.encryption_helper import verify_password


class ApiKeyRepository(BaseRepository[ApiKey]):
    """Repository for ApiKey operations"""
    
    def __init__(self):
        super().__init__(ApiKey)

    @BaseRepository._handle_db_exceptions
    def _get_by_name(
        self,
        session: Session,
        *,
        workspace_id: str,
        name: str,
        include_deleted: bool = False
    ) -> Optional[ApiKey]:
        """Get API key by workspace_id and name"""
        query = select(ApiKey).where(
            ApiKey.workspace_id == workspace_id,
            ApiKey.name == name
        )
        query = self._apply_soft_delete_filter(query, include_deleted)
        return session.execute(query).scalar_one_or_none()

    @BaseRepository._handle_db_exceptions
    def _get_by_key_hash(
        self,
        session: Session,
        *,
        key_hash: str,
        include_deleted: bool = False
    ) -> Optional[ApiKey]:
        """Get API key by key hash"""
        query = select(ApiKey).where(ApiKey.key_hash == key_hash)
        query = self._apply_soft_delete_filter(query, include_deleted)
        return session.execute(query).scalar_one_or_none()

    @BaseRepository._handle_db_exceptions
    def _get_by_api_key(
        self,
        session: Session,
        *,
        full_api_key: str,
        include_deleted: bool = False
    ) -> Optional[ApiKey]:
        """
        Get API key by full API key string.
        This method checks all possible key hashes by trying to verify the key.
        """
        
        # Get all active API keys (this is not efficient, but necessary for security)
        # In production, you might want to optimize this with a better indexing strategy
        query = select(ApiKey).where(ApiKey.is_active == True)
        query = self._apply_soft_delete_filter(query, include_deleted)
        api_keys = session.execute(query).scalars().all()
        
        # Try to match the key by verifying against each hash
        for api_key in api_keys:
            if verify_password(full_api_key, api_key.key_hash):
                return api_key
        
        return None