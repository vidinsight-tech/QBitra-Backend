"""
UserAgreementAcceptance Repository - Kullanıcı sözleşme kabulleri için repository.

Kullanım:
    >>> from miniflow.repository import UserAgreementAcceptanceRepository
    >>> acceptance_repo = UserAgreementAcceptanceRepository()
    >>> acceptances = acceptance_repo.get_all_by_user_id(session, "USR-123")
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional, List
from datetime import datetime, timezone

from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from miniflow.database.repository.advanced import AdvancedRepository
from miniflow.database.repository.base import handle_db_exceptions

if TYPE_CHECKING:
    from miniflow.models import UserAgreementAcceptance


class UserAgreementAcceptanceRepository(AdvancedRepository):
    """Kullanıcı sözleşme kabulleri için repository."""
    
    def __init__(self):
        from miniflow.models import UserAgreementAcceptance
        super().__init__(UserAgreementAcceptance)
    
    # =========================================================================
    # LOOKUP METHODS
    # =========================================================================
    
    @handle_db_exceptions
    def get_all_by_user_id(
        self, 
        session: Session, 
        user_id: str, order_by: Optional[str] = "accepted_at", order_desc: bool = True
    ) -> List[UserAgreementAcceptance]:
        """Kullanıcının tüm kabullerini getirir (liste)."""
        return session.query(self.model).filter(
            self.model.user_id == user_id
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).all()
    
    @handle_db_exceptions
    def get_active_by_user_id(
        self, 
        session: Session, 
        user_id: str
    ) -> List[UserAgreementAcceptance]:
        """Kullanıcının aktif kabullerini getirir (liste)."""
        return session.query(self.model).filter(
            self.model.user_id == user_id,
            self.model.is_active == True,
            self.model.is_revoked == False
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).all()
    
    @handle_db_exceptions
    def get_by_user_and_agreement(
        self, 
        session: Session, 
        user_id: str,
        agreement_id: str
    ) -> Optional[UserAgreementAcceptance]:
        """Kullanıcı ve sözleşme ile kabul getirir."""
        return session.query(self.model).filter(
            self.model.user_id == user_id,
            self.model.agreement_id == agreement_id,
            self.model.is_active == True,
            self.model.is_revoked == False
        ).first()
    
    @handle_db_exceptions
    def get_by_user_agreement_version(
        self, 
        session: Session, 
        user_id: str,
        agreement_id: str,
        agreement_version_id: str
    ) -> Optional[UserAgreementAcceptance]:
        """Kullanıcı, sözleşme ve versiyon ile kabul getirir."""
        return session.query(self.model).filter(
            self.model.user_id == user_id,
            self.model.agreement_id == agreement_id,
            self.model.agreement_version_id == agreement_version_id
        ).first()
    
    @handle_db_exceptions
    def get_all_by_agreement_id(
        self, 
        session: Session, 
        agreement_id: str,
        limit: int = 1000, order_by: Optional[str] = "created_at", order_desc: bool = True
    ) -> List[UserAgreementAcceptance]:
        """Sözleşmenin tüm kabullerini getirir (liste)."""
        return session.query(self.model).filter(
            self.model.agreement_id == agreement_id
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).limit(limit).all()
    
    @handle_db_exceptions
    def count_by_agreement_id(self, session: Session, agreement_id: str) -> int:
        """Sözleşme kabul sayısını döndürür."""
        return session.query(func.count(self.model.id)).filter(
            self.model.agreement_id == agreement_id,
            self.model.is_active == True
        ).scalar()
    
    # =========================================================================
    # ACCEPTANCE CHECK METHODS
    # =========================================================================
    
    @handle_db_exceptions
    def has_accepted(
        self, 
        session: Session, 
        user_id: str,
        agreement_id: str
    ) -> bool:
        """Kullanıcı sözleşmeyi kabul etmiş mi kontrol eder."""
        acceptance = self.get_by_user_and_agreement(session, user_id, agreement_id)
        return acceptance is not None
    
    @handle_db_exceptions
    def has_accepted_version(
        self, 
        session: Session, 
        user_id: str,
        agreement_id: str,
        agreement_version_id: str
    ) -> bool:
        """Kullanıcı belirli versiyonu kabul etmiş mi kontrol eder."""
        acceptance = self.get_by_user_agreement_version(
            session, user_id, agreement_id, agreement_version_id
        )
        return acceptance is not None
    
    # =========================================================================
    # STATUS UPDATE METHODS
    # =========================================================================
    
    @handle_db_exceptions
    def revoke_acceptance(
        self, 
        session: Session, 
        acceptance_id: str,
        reason: Optional[str] = None
    ) -> Optional[UserAgreementAcceptance]:
        """Kabulu iptal eder."""
        acceptance = self.get_by_id(session, acceptance_id)
        if acceptance:
            acceptance.is_revoked = True
            acceptance.revoked_at = datetime.now(timezone.utc)
            if reason:
                acceptance.revocation_reason = reason
            session.flush()
        return acceptance
    
    @handle_db_exceptions
    def deactivate_old_acceptances(
        self, 
        session: Session, 
        user_id: str,
        agreement_id: str
    ) -> int:
        """Eski kabulleri deaktif eder (yeni versiyon için)."""
        result = session.query(self.model).filter(
            self.model.user_id == user_id,
            self.model.agreement_id == agreement_id,
            self.model.is_active == True
        ).update({
            self.model.is_active: False
        }, synchronize_session=False)
        session.flush()
        return result

