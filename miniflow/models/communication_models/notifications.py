from sqlalchemy import Column, String, Text, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from miniflow.database.models import Base


class Notification(Base):
    """Kullanıcı bildirimleri"""
    __prefix__ = "NTC"
    __tablename__ = "notifications"
    __allow_unmapped__ = True

    # ---- User Relationship ---- #
    user_id = Column(String(20), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True,
    comment="Bildirimin gönderildiği kullanıcı")

    # ---- Notification Content ---- #
    title = Column(String(255), nullable=False,
    comment="Notification başlığı")
    content = Column(Text, nullable=True,
    comment="Notification metin içeriği")
    is_read = Column(Boolean, default=False,
    comment="Notification okundu mu")
    read_at = Column(DateTime(timezone=True), nullable=True,
    comment="Notification okunduğunda zamanı")
    sent_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=True,
    comment="Notification gönderildiğinde zamanı")

    # ---- Metadata ---- #
    metadata = Column(JSON, nullable=True,
    comment="Ek metadata bilgileri (icon, color, priority vb.)")

    # ---- Relationships ---- #
    user = relationship("User", back_populates="notifications")