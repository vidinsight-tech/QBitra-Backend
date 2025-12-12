from sqlalchemy import Column, String, Text, JSON, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship

from miniflow.database.models import Base
from miniflow.models.enums import TicketTypes, TicketStatus

class Ticket(Base):
    __prefix__ = "TCK"
    __tablename__ = "tickets"

    # ---- User Context ---- #
    user_id = Column(String(20), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True,
    comment="Ticket açan kullanıcını id'si")
    user_email = Column(String(255), nullable=True,
    comment="Ticket açan kullanıcının e-posta adresi")
    user_name = Column(String(255), nullable=True,
    comment="Ticket açan kullanıcının adı")

    # ---- Ticket Content ---- #
    ticket_type = Column(Enum(TicketTypes), nullable=False,
    comment="Açılan ticket tipi")
    title = Column(String(255), nullable=False,
    comment="Ticket başlığı")
    description = Column(Text, nullable=True,
    comment="Ticket metin içeriği")
    status = Column(Enum(TicketStatus), nullable=False, default=TicketStatus.OPEN,
    comment="Ticket durumu")
    closed_at = Column(DateTime(timezone=True), nullable=True,
    comment="Ticket çözüldüğünde zamanı")

    # ---- Auto Context ---- #
    context = Column(JSON, nullable=True,
    comment="Sistem tarafında takip için oluşturulan otomatik dosya")
    user_agent = Column(String(512), nullable=True,
    comment="Kullanıcıya dair user agent bilgisi")
    ip_address = Column(String(64), nullable=True,
    comment="Kullanıcıya dair ip bilgisi")

    # ---- Relations ---- #
    user = relationship("User", back_populates="tickets")
    messages = relationship("TicketMessage", back_populates="ticket", cascade="all, delete-orphan", order_by="TicketMessage.order")
    attachments = relationship("TicketAttachment", back_populates="ticket", cascade="all, delete-orphan")
