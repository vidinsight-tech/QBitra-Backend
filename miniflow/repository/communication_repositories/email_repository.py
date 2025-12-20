"""
Email Repository - E-posta işlemleri için repository.

Kullanım:
    >>> from miniflow.repository import EmailRepository
    >>> email_repo = EmailRepository()
    >>> emails = email_repo.get_all_by_status(session, "pending")
"""

from __future__ import annotations

from typing import Optional, List
from datetime import datetime, timezone, timedelta

from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from miniflow.database.repository.advanced import AdvancedRepository
from miniflow.models import Email
from miniflow.database.repository.base import handle_db_exceptions



class EmailRepository(AdvancedRepository):
    """E-posta işlemleri için repository."""
    
    def __init__(self):
        super().__init__(Email)
    
    # =========================================================================
    # LOOKUP METHODS
    # =========================================================================
    
    @handle_db_exceptions
    def get_by_provider_message_id(
        self, 
        session: Session, 
        provider: str,
        provider_message_id: str
    ) -> Optional[Email]:
        """Provider message ID ile e-posta getirir."""
        return session.query(self.model).filter(
            self.model.provider == provider,
            self.model.provider_message_id == provider_message_id
        ).first()
    
    @handle_db_exceptions
    def get_all_by_to_email(
        self, 
        session: Session, 
        to_email: str,
        limit: int = 100, order_by: Optional[str] = "sent_at", order_desc: bool = True
    ) -> List[Email]:
        """Alıcı adresine göre e-postaları getirir (liste)."""
        return session.query(self.model).filter(
            self.model.to_email == to_email
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).limit(limit).all()
    
    @handle_db_exceptions
    def get_all_by_status(
        self, 
        session: Session, 
        status: str,
        limit: int = 100, order_by: Optional[str] = "sent_at", order_desc: bool = True
    ) -> List[Email]:
        """Duruma göre e-postaları getirir (liste)."""
        return session.query(self.model).filter(
            self.model.status == status
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).limit(limit).all()
    
    @handle_db_exceptions
    def count_by_status(self, session: Session, status: str) -> int:
        """Duruma göre e-posta sayısını döndürür."""
        return session.query(func.count(self.model.id)).filter(
            self.model.status == status
        ).scalar()
    
    # =========================================================================
    # PENDING/RETRY METHODS
    # =========================================================================
    
    @handle_db_exceptions
    def get_pending_emails(
        self, 
        session: Session,
        limit: int = 100
    ) -> List[Email]:
        """Bekleyen e-postaları getirir."""
        return self.get_all_by_status(session, "pending", limit)
    
    @handle_db_exceptions
    def get_failed_emails_for_retry(
        self, 
        session: Session,
        max_retry_count: int = 3,
        limit: int = 100,
        order_by: Optional[str] = "created_at",
        order_desc: bool = True
    ) -> List[Email]:
        """Tekrar denenebilecek başarısız e-postaları getirir."""
        return session.query(self.model).filter(
            self.model.status == "failed",
            self.model.retry_count < max_retry_count
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).limit(limit).all()
    
    @handle_db_exceptions
    def increment_retry_count(
        self, 
        session: Session, 
        email_id: str
    ) -> Optional[Email]:
        """Retry sayısını artırır."""
        email = self.get_by_id(session, email_id)
        if email:
            email.retry_count = (email.retry_count or 0) + 1
            session.flush()
        return email
    
    # =========================================================================
    # STATUS UPDATE METHODS
    # =========================================================================
    
    @handle_db_exceptions
    def mark_as_sent(
        self, 
        session: Session, 
        email_id: str,
        provider_message_id: Optional[str] = None
    ) -> Optional[Email]:
        """E-postayı gönderildi olarak işaretler."""
        email = self.get_by_id(session, email_id)
        if email:
            email.status = "sent"
            email.sent_at = datetime.now(timezone.utc)
            if provider_message_id:
                email.provider_message_id = provider_message_id
            session.flush()
        return email
    
    @handle_db_exceptions
    def mark_as_delivered(
        self, 
        session: Session, 
        email_id: str
    ) -> Optional[Email]:
        """E-postayı teslim edildi olarak işaretler."""
        email = self.get_by_id(session, email_id)
        if email:
            email.status = "delivered"
            email.delivered_at = datetime.now(timezone.utc)
            session.flush()
        return email
    
    @handle_db_exceptions
    def mark_as_failed(
        self, 
        session: Session, 
        email_id: str,
        error_code: Optional[str] = None,
        error_message: Optional[str] = None
    ) -> Optional[Email]:
        """E-postayı başarısız olarak işaretler."""
        email = self.get_by_id(session, email_id)
        if email:
            email.status = "failed"
            email.failed_at = datetime.now(timezone.utc)
            if error_code:
                email.last_error_code = error_code
            if error_message:
                email.last_error_message = error_message
            session.flush()
        return email

