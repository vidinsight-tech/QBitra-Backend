"""
Ticket Repository - Destek ticket işlemleri için repository.

Kullanım:
    >>> from miniflow.repository import TicketRepository
    >>> ticket_repo = TicketRepository()
    >>> tickets = ticket_repo.get_all_by_user_id(session, "USR-123")
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional, List
from datetime import datetime, timezone

from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from miniflow.database.repository.advanced import AdvancedRepository
from miniflow.database.repository.base import handle_db_exceptions

if TYPE_CHECKING:
    from miniflow.models import Ticket


class TicketRepository(AdvancedRepository):
    """Destek ticket işlemleri için repository."""
    
    def __init__(self):
        from miniflow.models import Ticket
        super().__init__(Ticket)
    
    # =========================================================================
    # LOOKUP METHODS
    # =========================================================================
    
    @handle_db_exceptions
    def get_all_by_user_id(
        self, 
        session: Session, 
        user_id: str,
        limit: int = 100, order_by: Optional[str] = "opened_at", order_desc: bool = True
    ) -> List[Ticket]:
        """Kullanıcının ticket'larını getirir (liste)."""
        return session.query(self.model).filter(
            self.model.user_id == user_id
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).limit(limit).all()
    
    @handle_db_exceptions
    def get_all_by_status(
        self, 
        session: Session, 
        status,
        limit: int = 100, order_by: Optional[str] = "opened_at", order_desc: bool = True
    ) -> List[Ticket]:
        """Duruma göre ticket'ları getirir (liste)."""
        return session.query(self.model).filter(
            self.model.status == status
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).limit(limit).all()
    
    @handle_db_exceptions
    def get_all_by_type(
        self, 
        session: Session, 
        ticket_type,
        limit: int = 100, order_by: Optional[str] = "opened_at", order_desc: bool = True
    ) -> List[Ticket]:
        """Tipe göre ticket'ları getirir (liste)."""
        return session.query(self.model).filter(
            self.model.ticket_type == ticket_type
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).limit(limit).all()
    
    @handle_db_exceptions
    def count_by_status(self, session: Session, status) -> int:
        """Duruma göre ticket sayısını döndürür."""
        return session.query(func.count(self.model.id)).filter(
            self.model.status == status
        ).scalar()
    
    @handle_db_exceptions
    def count_by_user_id(self, session: Session, user_id: str) -> int:
        """Kullanıcının ticket sayısını döndürür."""
        return session.query(func.count(self.model.id)).filter(
            self.model.user_id == user_id
        ).scalar()
    
    # =========================================================================
    # OPEN TICKETS
    # =========================================================================
    
    @handle_db_exceptions
    def get_open_tickets(
        self, 
        session: Session,
        limit: int = 100
    ) -> List[Ticket]:
        """Açık ticket'ları getirir."""
        from miniflow.models.enums import TicketStatus
        return session.query(self.model).filter(
            self.model.status == TicketStatus.OPEN
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).limit(limit).all()
    
    @handle_db_exceptions
    def get_open_tickets_by_user_id(
        self, 
        session: Session, 
        user_id: str,
        limit: int = 100
    ) -> List[Ticket]:
        """Kullanıcının açık ticket'larını getirir."""
        from miniflow.models.enums import TicketStatus
        return session.query(self.model).filter(
            self.model.user_id == user_id,
            self.model.status == TicketStatus.OPEN
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).limit(limit).all()
    
    # =========================================================================
    # STATUS UPDATE METHODS
    # =========================================================================
    
    @handle_db_exceptions
    def close_ticket(
        self, 
        session: Session, 
        ticket_id: str
    ) -> Optional[Ticket]:
        """Ticket'ı kapatır."""
        from miniflow.models.enums import TicketStatus
        ticket = self.get_by_id(session, ticket_id)
        if ticket:
            ticket.status = TicketStatus.CLOSED
            ticket.closed_at = datetime.now(timezone.utc)
            session.flush()
        return ticket
    
    @handle_db_exceptions
    def update_status(
        self, 
        session: Session, 
        ticket_id: str,
        status
    ) -> Optional[Ticket]:
        """Ticket durumunu günceller."""
        from miniflow.models.enums import TicketStatus
        ticket = self.get_by_id(session, ticket_id)
        if ticket:
            ticket.status = status
            if status == TicketStatus.CLOSED:
                ticket.closed_at = datetime.now(timezone.utc)
            session.flush()
        return ticket

