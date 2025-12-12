from sqlalchemy import Column, String, ForeignKey, Integer
from sqlalchemy.orm import relationship

from miniflow.database.models import Base


class EmailAttachment(Base):
    """E-posta ekleri modeli - E-postalara eklenen dosyalar."""
    __prefix__ = "EMA"
    __tablename__ = "email_attachments"
    __allow_unmapped__ = True

    # ---- Email Relationship ---- #
    email_id = Column(String(20), ForeignKey("emails.id", ondelete="CASCADE"), nullable=False, index=True,
    comment="Ekin ait olduğu e-posta id'si")

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
    
    # ---- Content ID (for inline attachments in HTML emails) ---- #
    content_id = Column(String(255), nullable=True,
    comment="HTML e-postalarda inline attachment için Content-ID (cid:)")

    # ---- Relations ---- #
    email = relationship("Email", back_populates="attachments")

