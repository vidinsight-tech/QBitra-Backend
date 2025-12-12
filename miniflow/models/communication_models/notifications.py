from sqlalchemy import Column, String, Text, Boolean, DateTime, JSON
from datetime import datetime, timezone

from miniflow.database.models import Base


class Notification(Base):
    __prefix__ = "NTC"
    __tablename__ = "notifications"

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