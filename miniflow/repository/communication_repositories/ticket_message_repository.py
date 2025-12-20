"""
TicketMessage Repository - Ticket mesajları için repository.

Kullanım:
    >>> from miniflow.repository import TicketMessageRepository
    >>> message_repo = TicketMessageRepository()
    >>> messages = message_repo.get_all_by_ticket_id(session, "TCK-123")
"""

from __future__ import annotations

from typing import Optional, List

from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from miniflow.database.repository.base import BaseRepository, handle_db_exceptions
from miniflow.models import TicketMessage


class TicketMessageRepository(BaseRepository):
    """Ticket mesajları için repository."""
    
    def __init__(self):
        super().__init__(TicketMessage)
    
    # =========================================================================
    # LOOKUP METHODS
    # =========================================================================
    
    @handle_db_exceptions
    def get_all_by_ticket_id(
        self, 
        session: Session, 
        ticket_id: str, order_by: Optional[str] = "order", order_desc: bool = True
    ) -> List[TicketMessage]:
        """Ticket'ın tüm mesajlarını getirir (liste)."""
        return session.query(self.model).filter(
            self.model.ticket_id == ticket_id
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).all()
    
    @handle_db_exceptions
    def get_last_message(
        self, 
        session: Session, 
        ticket_id: str,
        order_by: Optional[str] = "created_at",
        order_desc: bool = True
    ) -> Optional[TicketMessage]:
        """Ticket'ın son mesajını getirir."""
        return session.query(self.model).filter(
            self.model.ticket_id == ticket_id
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).first()
    
    @handle_db_exceptions
    def count_by_ticket_id(self, session: Session, ticket_id: str) -> int:
        """Ticket'ın mesaj sayısını döndürür."""
        return session.query(func.count(self.model.id)).filter(
            self.model.ticket_id == ticket_id
        ).scalar()
    
    @handle_db_exceptions
    def get_next_order(self, session: Session, ticket_id: str) -> int:
        """Sonraki mesaj sırasını döndürür."""
        max_order = session.query(func.max(self.model.order)).filter(
            self.model.ticket_id == ticket_id
        ).scalar()
        return (max_order or 0) + 1
    
    # =========================================================================
    # DELETE METHODS
    # =========================================================================
    
    @handle_db_exceptions
    def delete_all_by_ticket_id(self, session: Session, ticket_id: str) -> int:
        """Ticket'ın tüm mesajlarını siler (hard delete)."""
        result = session.query(self.model).filter(
            self.model.ticket_id == ticket_id
        ).delete(synchronize_session=False)
        session.flush()
        return result

