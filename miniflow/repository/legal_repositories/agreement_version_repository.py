"""
AgreementVersion Repository - Sözleşme versiyonları için repository.

Kullanım:
    >>> from miniflow.repository import AgreementVersionRepository
    >>> agreement_repo = AgreementVersionRepository()
    >>> latest = agreement_repo.get_latest(session, "terms_of_service")
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional, List

from sqlalchemy import desc
from sqlalchemy.orm import Session

from miniflow.database.repository.advanced import AdvancedRepository
from miniflow.database.repository.base import handle_db_exceptions

if TYPE_CHECKING:
    from miniflow.models import AgreementVersion


class AgreementVersionRepository(AdvancedRepository):
    """Sözleşme versiyonları için repository."""
    
    def __init__(self):
        from miniflow.models import AgreementVersion
        super().__init__(AgreementVersion)
    
    # =========================================================================
    # LOOKUP METHODS
    # =========================================================================
    
    @handle_db_exceptions
    def get_by_type_and_version(
        self, 
        session: Session, 
        agreement_type: str, 
        version: str
    ) -> Optional[AgreementVersion]:
        """Sözleşme tipi ve versiyonuyla getirir."""
        return session.query(self.model).filter(
            self.model.agreement_type == agreement_type,
            self.model.version == version
        ).first()
    
    @handle_db_exceptions
    def get_latest(self, session: Session, agreement_type: str) -> Optional[AgreementVersion]:
        """En son sözleşme versiyonunu getirir."""
        return session.query(self.model).filter(
            self.model.agreement_type == agreement_type
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).first()
    
    @handle_db_exceptions
    def get_active(self, session: Session, agreement_type: str) -> Optional[AgreementVersion]:
        """Aktif sözleşme versiyonunu getirir."""
        return session.query(self.model).filter(
            self.model.agreement_type == agreement_type,
            self.model.is_active == True
        ).first()
    
    @handle_db_exceptions
    def get_all_by_type(self, session: Session, agreement_type: str, order_by: Optional[str] = "order", order_desc: bool = True
    ) -> List[AgreementVersion]:
        """Bir tipteki tüm versiyonları getirir."""
        return session.query(self.model).filter(
            self.model.agreement_type == agreement_type
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).all()
    
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

