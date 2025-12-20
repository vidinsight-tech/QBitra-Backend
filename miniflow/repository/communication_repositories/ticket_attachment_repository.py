"""
TicketAttachment Repository - Ticket ekleri için repository.

Kullanım:
    >>> from miniflow.repository import TicketAttachmentRepository
    >>> attachment_repo = TicketAttachmentRepository()
    >>> attachments = attachment_repo.get_all_by_ticket_id(session, "TCK-123")
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional, List

from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from miniflow.database.repository.base import BaseRepository, handle_db_exceptions


class TicketAttachmentRepository(BaseRepository):
    """Ticket ekleri için repository."""
    
    def __init__(self):
        from miniflow.models import TicketAttachment
        super().__init__(TicketAttachment)
    
    # =========================================================================
    # LOOKUP METHODS
    # =========================================================================
    
    @handle_db_exceptions
    def get_all_by_ticket_id(
        self, 
        session: Session, 
        ticket_id: str
    ) -> List[TicketAttachment]:
        """Ticket'ın tüm eklerini getirir (liste)."""
        return session.query(self.model).filter(
            self.model.ticket_id == ticket_id
        ).all()
    
    @handle_db_exceptions
    def get_all_by_message_id(
        self, 
        session: Session, 
        message_id: str
    ) -> List[TicketAttachment]:
        """Mesajın tüm eklerini getirir (liste)."""
        return session.query(self.model).filter(
            self.model.message_id == message_id
        ).all()
    
    @handle_db_exceptions
    def get_by_ticket_and_filename(
        self, 
        session: Session, 
        ticket_id: str,
        file_name: str
    ) -> Optional[TicketAttachment]:
        """Ticket ve dosya adı ile ek getirir."""
        return session.query(self.model).filter(
            self.model.ticket_id == ticket_id,
            self.model.file_name == file_name
        ).first()
    
    @handle_db_exceptions
    def count_by_ticket_id(self, session: Session, ticket_id: str) -> int:
        """Ticket'ın ek sayısını döndürür."""
        return session.query(func.count(self.model.id)).filter(
            self.model.ticket_id == ticket_id
        ).scalar()
    
    @handle_db_exceptions
    def get_total_size_by_ticket_id(self, session: Session, ticket_id: str) -> int:
        """Toplam ek boyutunu döndürür (bytes)."""
        result = session.query(func.sum(self.model.file_size)).filter(
            self.model.ticket_id == ticket_id
        ).scalar()
        return result or 0
    
    # =========================================================================
    # DELETE METHODS
    # =========================================================================
    
    @handle_db_exceptions
    def delete_all_by_ticket_id(self, session: Session, ticket_id: str) -> int:
        """Ticket'ın tüm eklerini siler (hard delete)."""
        result = session.query(self.model).filter(
            self.model.ticket_id == ticket_id
        ).delete(synchronize_session=False)
        session.flush()
        return result
    
    @handle_db_exceptions
    def delete_all_by_message_id(self, session: Session, message_id: str) -> int:
        """Mesajın tüm eklerini siler (hard delete)."""
        result = session.query(self.model).filter(
            self.model.message_id == message_id
        ).delete(synchronize_session=False)
        session.flush()
        return result

