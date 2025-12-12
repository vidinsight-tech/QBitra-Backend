from sqlalchemy import Column, String, Text, JSON, ForeignKey, Integer, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from miniflow.database.models import Base


class TicketMessage(Base):
    __prefix__ = "TCKM"
    __tablename__ = "ticket_messages"

    # ---- Ticket (Parent) Relationship ---- #
    ticket_id = Column(String(20), ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False, index=True,
    comment="Ticket'in id'si")

    # ---- Message Content ---- #
    message = Column(Text, nullable=True,
    comment="Ticket metin içeriği")
    order = Column(Integer, nullable=False, default=0, index=True,
    comment="Mesajın sırası")
    date_time = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False,
    comment="Mesajın gönderildiği tarih ve saat")


    # ---- Auto Context ---- #
    context = Column(JSON, nullable=True,
    comment="Sistem tarafında takip için oluşturulan otomatik dosya")
    user_agent = Column(String(512), nullable=True,
    comment="Kullanıcıya dair user agent bilgisi")
    ip_address = Column(String(64), nullable=True,
    comment="Kullanıcıya dair ip bilgisi")

    # ---- Relations ---- #
    ticket = relationship("Ticket", back_populates="messages")
    attachments = relationship("TicketAttachment", back_populates="message", cascade="all, delete-orphan")