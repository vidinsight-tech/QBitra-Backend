"""
Agreement Repository - Sözleşme işlemleri için repository.

Kullanım:
    >>> from miniflow.repository import AgreementRepository
    >>> agreement_repo = AgreementRepository()
    >>> agreement = agreement_repo.get_by_type(session, AgreementType.TERMS_OF_SERVICE)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional, List

from sqlalchemy import desc
from sqlalchemy.orm import Session

from miniflow.database.repository.advanced import AdvancedRepository
from miniflow.database.repository.base import handle_db_exceptions

if TYPE_CHECKING:
    from miniflow.models import Agreement


class AgreementRepository(AdvancedRepository):
    """Sözleşme işlemleri için repository."""
    
    def __init__(self):
        from miniflow.models import Agreement
        super().__init__(Agreement)
    
    # =========================================================================
    # LOOKUP METHODS
    # =========================================================================
    
    @handle_db_exceptions
    def get_by_type_and_language(
        self, 
        session: Session, 
        agreement_type,
        language: str = "tr"
    ) -> Optional[Agreement]:
        """Tip ve dil ile sözleşme getirir."""
        return session.query(self.model).filter(
            self.model.agreement_type == agreement_type,
            self.model.language == language
        ).first()
    
    @handle_db_exceptions
    def get_all_by_type(
        self, 
        session: Session, 
        agreement_type, order_by: Optional[str] = "display_order", order_desc: bool = False
    ) -> List[Agreement]:
        """Tipe göre tüm sözleşmeleri getirir (liste)."""
        return session.query(self.model).filter(
            self.model.agreement_type == agreement_type
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).all()
    
    @handle_db_exceptions
    def get_all_by_status(
        self, 
        session: Session, 
        status, order_by: Optional[str] = "display_order", order_desc: bool = False
    ) -> List[Agreement]:
        """Duruma göre sözleşmeleri getirir (liste)."""
        return session.query(self.model).filter(
            self.model.status == status
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).all()
    
    @handle_db_exceptions
    def get_active_agreements(
        self, 
        session: Session,
        language: Optional[str] = None, order_by: Optional[str] = "display_order", order_desc: bool = False
    ) -> List[Agreement]:
        """Aktif sözleşmeleri getirir."""
        from miniflow.models.enums import AgreementStatus
        query = session.query(self.model).filter(
            self.model.status == AgreementStatus.ACTIVE
        )
        if language:
            query = query.filter(self.model.language == language)
        return query.order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).all()
    
    @handle_db_exceptions
    def get_required_agreements(
        self, 
        session: Session,
        language: str = "tr", order_by: Optional[str] = "display_order", order_desc: bool = False
    ) -> List[Agreement]:
        """Zorunlu sözleşmeleri getirir."""
        from miniflow.models.enums import AgreementStatus
        return session.query(self.model).filter(
            self.model.status == AgreementStatus.ACTIVE,
            self.model.is_required == True,
            self.model.language == language
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).all()
    
    @handle_db_exceptions
    def get_signup_agreements(
        self, 
        session: Session,
        language: str = "tr", order_by: Optional[str] = "display_order", order_desc: bool = False
    ) -> List[Agreement]:
        """Kayıt sırasında gösterilecek sözleşmeleri getirir."""
        from miniflow.models.enums import AgreementStatus
        return session.query(self.model).filter(
            self.model.status == AgreementStatus.ACTIVE,
            self.model.show_on_signup == True,
            self.model.language == language
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).all()
    
    # =========================================================================
    # UPDATE METHODS
    # =========================================================================
    
    @handle_db_exceptions
    def update_current_version(
        self, 
        session: Session, 
        agreement_id: str,
        version_id: str
    ) -> Optional[Agreement]:
        """Aktif versiyonu günceller."""
        agreement = self.get_by_id(session, agreement_id)
        if agreement:
            agreement.current_version_id = version_id
            session.flush()
        return agreement
    
    @handle_db_exceptions
    def update_status(
        self, 
        session: Session, 
        agreement_id: str,
        status
    ) -> Optional[Agreement]:
        """Sözleşme durumunu günceller."""
        agreement = self.get_by_id(session, agreement_id)
        if agreement:
            agreement.status = status
            session.flush()
        return agreement

