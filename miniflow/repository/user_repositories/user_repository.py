"""
User Repository - Kullanıcı işlemleri için repository.

Kullanım:
    >>> from miniflow.repository import UserRepository
    >>> user_repo = UserRepository()
    >>> user = user_repo.get_by_email(session, "test@example.com")
"""

from __future__ import annotations

from typing import Optional, List
from datetime import datetime, timezone

from sqlalchemy import or_
from sqlalchemy.orm import Session

from miniflow.database.repository.bulk import BulkRepository
from miniflow.models import User
from miniflow.database.repository.base import handle_db_exceptions



class UserRepository(BulkRepository):
    """Kullanıcı işlemleri için repository."""
    
    def __init__(self):
        super().__init__(User)
        self._model_class = User
    
    # =========================================================================
    # LOOKUP METHODS
    # =========================================================================
    
    @handle_db_exceptions
    def get_by_email(self, session: Session, email: str) -> Optional[User]:
        """Email ile kullanıcı getirir."""
        return session.query(self.model).filter(
            self.model.email == email,
            self.model.is_deleted == False
        ).first()
    
    @handle_db_exceptions
    def get_by_username(self, session: Session, username: str) -> Optional[User]:
        """Username ile kullanıcı getirir."""
        return session.query(self.model).filter(
            self.model.username == username,
            self.model.is_deleted == False
        ).first()
    
    @handle_db_exceptions
    def get_by_email_or_username(self, session: Session, identifier: str) -> Optional[User]:
        """Email veya username ile kullanıcı getirir."""
        return session.query(self.model).filter(
            or_(
                self.model.email == identifier,
                self.model.username == identifier
            ),
            self.model.is_deleted == False
        ).first()
    
    @handle_db_exceptions
    def get_by_email_verification_token(self, session: Session, token: str) -> Optional[User]:
        """Email doğrulama token'ı ile kullanıcı getirir."""
        return session.query(self.model).filter(
            self.model.email_verification_token == token,
            self.model.is_deleted == False
        ).first()
    
    @handle_db_exceptions
    def get_by_password_reset_token(self, session: Session, token: str) -> Optional[User]:
        """Şifre sıfırlama token'ı ile kullanıcı getirir."""
        return session.query(self.model).filter(
            self.model.password_reset_token == token,
            self.model.is_deleted == False
        ).first()

