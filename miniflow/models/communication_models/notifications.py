from sqlalchemy import Column, String, Text, Boolean, DateTime, JSON, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from miniflow.database.models import Base
from miniflow.database.models.mixins import TimestampMixin


class Notification(Base, TimestampMixin):
    """Kullanıcı bildirimleri"""
    __prefix__ = "NTC"
    __tablename__ = "notifications"
    
    # ---- Table Args ---- #
    __table_args__ = (
        Index('idx_notifications_user_read_sent', 'user_id', 'is_read', 'sent_at'),
        Index('idx_notifications_user_sent', 'user_id', 'sent_at'),
    )

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
    read_at = Column(DateTime(timezone=True), nullable=True, index=True,
    comment="Notification okunduğunda zamanı")
    sent_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=True, index=True,
    comment="Notification gönderildiğinde zamanı")

    # ---- Metadata ---- #
    notification_metadata = Column(JSON, nullable=True,
    comment="Ek metadata bilgileri (icon, color, priority vb.)")

    # ---- Relationships ---- #
    user = relationship("User", back_populates="notifications")