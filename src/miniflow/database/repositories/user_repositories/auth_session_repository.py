from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy import select, func, delete
from sqlalchemy.orm import Session

from ..base_repository import BaseRepository
from ...models.user_models.auth_session_model import AuthSession


class AuthSessionRepository(BaseRepository[AuthSession]):
    def __init__(self):
        super().__init__(AuthSession)

    def _get_by_access_token_jti(self, session: Session, access_token_jti: str, include_deleted: bool = False) -> Optional[AuthSession]:
        query = select(AuthSession).where(AuthSession.access_token_jti == access_token_jti)
        query = self._apply_soft_delete_filter(query, include_deleted)
        return session.execute(query).scalar_one_or_none()
    
    def _get_by_refresh_token_jti(self, session: Session, refresh_token_jti: str, include_deleted: bool = False) -> Optional[AuthSession]:
        query = select(AuthSession).where(AuthSession.refresh_token_jti == refresh_token_jti)
        query = self._apply_soft_delete_filter(query, include_deleted)
        return session.execute(query).scalar_one_or_none()

    def _revoke_sessions(self, session: Session, user_id: str) -> None:
        query = select(AuthSession).where(AuthSession.user_id == user_id, AuthSession.is_revoked == False)
        query = self._apply_soft_delete_filter(query, include_deleted=False)
        sessions = session.execute(query).scalars().all()
        
        for auth_session in sessions:
            auth_session.is_revoked = True
            auth_session.revoked_at = datetime.now(timezone.utc)
            auth_session.revoked_by = user_id
            session.add(auth_session)
        session.commit()

        return len(sessions)