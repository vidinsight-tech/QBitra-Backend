from sqlalchemy import Column, String, ForeignKey, Integer
from sqlalchemy.orm import relationship

from miniflow.database.models import Base


class TicketAttachment(Base):
    __prefix__ = "TCA"
    __tablename__ = "ticket_attachments"

    # ---- Relationships ---- #
    ticket_id = Column(String(20), ForeignKey("tickets.id", ondelete="CASCADE"), nullable=True, index=True,
    comment="Ekin ait olduğu ticket id'si (mesaj eklenmişse null olabilir)")
    message_id = Column(String(20), ForeignKey("ticket_messages.id", ondelete="CASCADE"), nullable=True, index=True,
    comment="Ekin ait olduğu mesaj id'si (ticket'a direkt eklenmişse null olabilir)")

    # ---- File Information ---- #
    file_name = Column(String(255), nullable=False,
    comment="Dosya adı")
    file_path = Column(String(512), nullable=False,
    comment="Dosyanın saklandığı path")
    file_size = Column(Integer, nullable=False,
    comment="Dosya boyutu (byte)")
    file_type = Column(String(100), nullable=True,
    comment="Dosya MIME type'ı (örn: image/png, application/pdf)")
    file_extension = Column(String(10), nullable=True,
    comment="Dosya uzantısı (örn: .png, .pdf)")

    # ---- Relations ---- #
    ticket = relationship("Ticket", back_populates="attachments")
    message = relationship("TicketMessage", back_populates="attachments")