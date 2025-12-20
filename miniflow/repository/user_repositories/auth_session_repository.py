"""
AuthSession Repository - Oturum yönetimi için repository.

Kullanım:
    >>> from miniflow.repository import AuthSessionRepository
    >>> session_repo = AuthSessionRepository()
    >>> auth_session = session_repo.get_by_access_token_jti(session, "jti_value")
"""

from __future__ import annotations

from typing import Optional, List
from datetime import datetime, timezone

from sqlalchemy import desc
from sqlalchemy.orm import Session

from miniflow.database.repository.advanced import AdvancedRepository
from miniflow.models import AuthSession
from miniflow.database.repository.base import handle_db_exceptions



class AuthSessionRepository(AdvancedRepository):
    """Oturum yönetimi için repository."""
    
    def __init__(self):
        super().__init__(AuthSession)
    
    # =========================================================================
    # LOOKUP METHODS
    # =========================================================================
    
    @handle_db_exceptions
    def get_by_access_token_jti(self, session: Session, jti: str) -> Optional[AuthSession]:
        """Access token JTI ile session getirir."""
        return session.query(self.model).filter(
            self.model.access_token_jti == jti,
            self.model.is_deleted == False
        ).first()
    
    @handle_db_exceptions
    def get_by_refresh_token_jti(self, session: Session, jti: str) -> Optional[AuthSession]:
        """Refresh token JTI ile session getirir."""
        return session.query(self.model).filter(
            self.model.refresh_token_jti == jti,
            self.model.is_deleted == False
        ).first()
    
    @handle_db_exceptions
    def get_all_active_user_sessions(
        self, 
        session: Session, 
        user_id: str,
        limit: int = 100, order_by: Optional[str] = "created_at", order_desc: bool = True
    ) -> List[AuthSession]:
        """Kullanıcının aktif session'larını getirir."""
        return session.query(self.model).filter(
            self.model.user_id == user_id,
            self.model.is_deleted == False,
            self.model.is_revoked == False
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).limit(limit).all()
    
    # =========================================================================
    # SESSION MANAGEMENT
    # =========================================================================
    
    @handle_db_exceptions
    def revoke_oldest_session(
        self, 
        session: Session, 
        user_id: str,
        order_by: Optional[str] = "created_at",
        order_desc: bool = False
    ) -> Optional[AuthSession]:
        """En eski session'ı iptal eder."""
        oldest = session.query(self.model).filter(
            self.model.user_id == user_id,
            self.model.is_deleted == False,
            self.model.is_revoked == False
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).first()
        
        if oldest:
            oldest.is_revoked = True
            oldest.revoked_at = datetime.now(timezone.utc)
            session.flush()
        
        return oldest
    
    @handle_db_exceptions
    def revoke_specific_session(self, session: Session, session_id: str) -> bool:
        """Belirli bir session'ı iptal eder."""
        auth_session = self.get_by_id(session, session_id)
        if auth_session:
            auth_session.is_revoked = True
            auth_session.revoked_at = datetime.now(timezone.utc)
            session.flush()
            return True
        return False
    
    @handle_db_exceptions
    def revoke_sessions(self, session: Session, user_id: str) -> int:
        """Kullanıcının tüm session'larını iptal eder."""
        now = datetime.now(timezone.utc)
        result = session.query(self.model).filter(
            self.model.user_id == user_id,
            self.model.is_deleted == False,
            self.model.is_revoked == False
        ).update({
            self.model.is_revoked: True,
            self.model.revoked_at: now
        }, synchronize_session=False)
        session.flush()
        return result

