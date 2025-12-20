"""
Credential Repository - Credential işlemleri için repository.

Kullanım:
    >>> from miniflow.repository import CredentialRepository
    >>> credential_repo = CredentialRepository()
    >>> credential = credential_repo.get_by_name(session, "WSP-123", "my_api_credential")
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional, List
from datetime import datetime, timezone

from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from miniflow.database.repository.advanced import AdvancedRepository
from miniflow.database.repository.base import handle_db_exceptions

if TYPE_CHECKING:
    from miniflow.models import Credential


class CredentialRepository(AdvancedRepository):
    """Credential işlemleri için repository."""
    
    def __init__(self):
        from miniflow.models import Credential
        super().__init__(Credential)
    
    # =========================================================================
    # LOOKUP METHODS
    # =========================================================================
    
    @handle_db_exceptions
    def get_by_name(
        self, 
        session: Session, 
        workspace_id: str, 
        name: str
    ) -> Optional[Credential]:
        """İsim ile credential getirir."""
        return session.query(self.model).filter(
            self.model.workspace_id == workspace_id,
            self.model.name == name,
            self.model.is_deleted == False
        ).first()
    
    @handle_db_exceptions
    def get_all_by_workspace_id(
        self, 
        session: Session, 
        workspace_id: str, order_by: Optional[str] = "created_at", order_desc: bool = True
    ) -> List[Credential]:
        """Workspace'in tüm credential'larını getirir."""
        return session.query(self.model).filter(
            self.model.workspace_id == workspace_id,
            self.model.is_deleted == False
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).all()
    
    @handle_db_exceptions
    def get_all_by_type(
        self, 
        session: Session, 
        workspace_id: str, 
        credential_type: str, order_by: Optional[str] = "created_at", order_desc: bool = True
    ) -> List[Credential]:
        """Tipe göre credential'ları getirir (liste)."""
        return session.query(self.model).filter(
            self.model.workspace_id == workspace_id,
            self.model.credential_type == credential_type,
            self.model.is_deleted == False
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).all()
    
    @handle_db_exceptions
    def count_by_workspace_id(self, session: Session, workspace_id: str) -> int:
        """Credential sayısını döndürür."""
        return session.query(func.count(self.model.id)).filter(
            self.model.workspace_id == workspace_id,
            self.model.is_deleted == False
        ).scalar()
    
    # =========================================================================
    # STATUS METHODS
    # =========================================================================
    
    @handle_db_exceptions
    def update_last_used(
        self, 
        session: Session, 
        credential_id: str
    ) -> Optional[Credential]:
        """Son kullanım zamanını günceller."""
        credential = self.get_by_id(session, credential_id)
        if credential:
            credential.last_used_at = datetime.now(timezone.utc)
            session.flush()
        return credential
    
    @handle_db_exceptions
    def deactivate(self, session: Session, credential_id: str) -> Optional[Credential]:
        """Credential'ı deaktif eder."""
        credential = self.get_by_id(session, credential_id)
        if credential:
            credential.is_active = False
            session.flush()
        return credential
    
    @handle_db_exceptions
    def activate(self, session: Session, credential_id: str) -> Optional[Credential]:
        """Credential'ı aktif eder."""
        credential = self.get_by_id(session, credential_id)
        if credential:
            credential.is_active = True
            session.flush()
        return credential

