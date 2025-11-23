from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from ..base_repository import BaseRepository
from ...models.user_models.login_history import LoginHistory
from ...models.enums import LoginStatus


class LoginHistoryRepository(BaseRepository[LoginHistory]):
    def __init__(self):
        super().__init__(LoginHistory)

    @BaseRepository._handle_db_exceptions
    def _get_by_user_id(self, session: Session, user_id: str, last_n: int = 10, include_deleted: bool = False) -> Optional[List[LoginHistory]]:
        query = select(LoginHistory).where(LoginHistory.user_id == user_id).order_by(LoginHistory.created_at.desc()).limit(last_n)
        query = self._apply_soft_delete_filter(query, include_deleted)
        return session.execute(query).scalars().all()

    @BaseRepository._handle_db_exceptions
    def _check_user_rate_limit(self, session, *, user_id: str, max_attempts: int = 5, window_minutes: int = 5) -> bool:
         cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=window_minutes)

         query = select(func.count()).select_from(LoginHistory).where(
             LoginHistory.user_id == user_id,
             LoginHistory.created_at > cutoff_time,
             LoginHistory.status != LoginStatus.SUCCESS
         )
         query = self._apply_soft_delete_filter(query, include_deleted=False)
         return session.execute(query).scalar() >= max_attempts