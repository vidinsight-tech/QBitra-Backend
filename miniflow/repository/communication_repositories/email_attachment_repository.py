"""
EmailAttachment Repository - E-posta ekleri için repository.

Kullanım:
    >>> from miniflow.repository import EmailAttachmentRepository
    >>> attachment_repo = EmailAttachmentRepository()
    >>> attachments = attachment_repo.get_all_by_email_id(session, "EML-123")
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional, List

from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from miniflow.database.repository.base import BaseRepository, handle_db_exceptions


class EmailAttachmentRepository(BaseRepository):
    """E-posta ekleri için repository."""
    
    def __init__(self):
        from miniflow.models import EmailAttachment
        super().__init__(EmailAttachment)
    
    # =========================================================================
    # LOOKUP METHODS
    # =========================================================================
    
    @handle_db_exceptions
    def get_all_by_email_id(
        self, 
        session: Session, 
        email_id: str
    ) -> List[EmailAttachment]:
        """E-postanın tüm eklerini getirir (liste)."""
        return session.query(self.model).filter(
            self.model.email_id == email_id
        ).all()
    
    @handle_db_exceptions
    def get_by_email_and_filename(
        self, 
        session: Session, 
        email_id: str,
        file_name: str
    ) -> Optional[EmailAttachment]:
        """E-posta ve dosya adı ile ek getirir."""
        return session.query(self.model).filter(
            self.model.email_id == email_id,
            self.model.file_name == file_name
        ).first()
    
    @handle_db_exceptions
    def count_by_email_id(self, session: Session, email_id: str) -> int:
        """Ek sayısını döndürür."""
        return session.query(func.count(self.model.id)).filter(
            self.model.email_id == email_id
        ).scalar()
    
    @handle_db_exceptions
    def get_total_size_by_email_id(self, session: Session, email_id: str) -> int:
        """Toplam ek boyutunu döndürür (bytes)."""
        result = session.query(func.sum(self.model.file_size)).filter(
            self.model.email_id == email_id
        ).scalar()
        return result or 0
    
    # =========================================================================
    # DELETE METHODS
    # =========================================================================
    
    @handle_db_exceptions
    def delete_all_by_email_id(self, session: Session, email_id: str) -> int:
        """E-postanın tüm eklerini siler (hard delete)."""
        result = session.query(self.model).filter(
            self.model.email_id == email_id
        ).delete(synchronize_session=False)
        session.flush()
        return result

