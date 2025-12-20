"""
AgreementVersion Repository - Sözleşme versiyonları için repository.

Kullanım:
    >>> from miniflow.repository import AgreementVersionRepository
    >>> agreement_repo = AgreementVersionRepository()
    >>> latest = agreement_repo.get_latest(session, "terms_of_service")
"""

from __future__ import annotations

from typing import Optional, List

from sqlalchemy import desc
from sqlalchemy.orm import Session

from miniflow.database.repository.advanced import AdvancedRepository
from miniflow.models import AgreementVersion
from miniflow.database.repository.base import handle_db_exceptions



class AgreementVersionRepository(AdvancedRepository):
    """Sözleşme versiyonları için repository."""
    
    def __init__(self):
        super().__init__(AgreementVersion)
    
    # =========================================================================
    # LOOKUP METHODS
    # =========================================================================
    
    @handle_db_exceptions
    def get_by_agreement_and_version(
        self, 
        session: Session, 
        agreement_id: str, 
        version_number: int
    ) -> Optional[AgreementVersion]:
        """Sözleşme id'si ve versiyon numarasıyla getirir."""
        return session.query(self.model).filter(
            self.model.agreement_id == agreement_id,
            self.model.version_number == version_number
        ).first()
    
    @handle_db_exceptions
    def get_latest_by_agreement_id(self, session: Session, agreement_id: str) -> Optional[AgreementVersion]:
        """Agreement'ın en son versiyonunu getirir."""
        return session.query(self.model).filter(
            self.model.agreement_id == agreement_id
        ).order_by(desc(self.model.version_number)).first()
    
    @handle_db_exceptions
    def get_all_by_agreement_id(
        self, 
        session: Session, 
        agreement_id: str, order_by: Optional[str] = "version_number", order_desc: bool = True
    ) -> List[AgreementVersion]:
        """Agreement'ın tüm versiyonlarını getirir (liste)."""
        return session.query(self.model).filter(
            self.model.agreement_id == agreement_id
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).all()
    
    @handle_db_exceptions
    def get_active_by_agreement_id(
        self, 
        session: Session, 
        agreement_id: str
    ) -> Optional[AgreementVersion]:
        """Agreement'ın aktif versiyonunu getirir."""
        return session.query(self.model).filter(
            self.model.agreement_id == agreement_id,
            self.model.is_active == True
        ).first()

