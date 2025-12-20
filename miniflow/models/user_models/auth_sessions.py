from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey, Index
from sqlalchemy.orm import relationship

from miniflow.database.models import Base
from miniflow.database.models.mixins import SoftDeleteMixin, TimestampMixin

class AuthSession(Base, SoftDeleteMixin, TimestampMixin):
    """Kullanıcı giriş geçmişi modeli"""
    __prefix__ = "AUS"
    __tablename__ = "auth_sessions"
    
    # ---- Table Args ---- #
    __table_args__ = (
        Index('idx_auth_sessions_user_active', 'user_id', 'is_revoked', 'access_token_expires_at'),
        Index('idx_auth_sessions_softdelete', 'is_deleted', 'created_at'),
    )

    # ---- Auth Session ---- #
    user_id = Column(String(20), ForeignKey("users.id", ondelete="CASCADE"), nullable=False,
    comment="Kullanıcı id'si")
    
    # ---- Access Token Information ---- #
    access_token_jti = Column(String(100), nullable=False, unique=True, index=True,
    comment="Access token JWT ID")
    access_token_created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False,
    comment="Access token oluşturulma tarihi")
    access_token_expires_at = Column(DateTime(timezone=True), nullable=False, index=True,
    comment="Access token süresi dolma tarihi")
    access_token_last_used_at = Column(DateTime(timezone=True), nullable=True,
    comment="Access token son kullanım tarihi")

    # ---- Refresh Token Information ---- #
    refresh_token_jti = Column(String(100), nullable=False, unique=True, index=True,
    comment="Refresh token JWT ID")
    refresh_token_created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False,
    comment="Refresh token oluşturulma tarihi")
    refresh_token_expires_at = Column(DateTime(timezone=True), nullable=False, index=True,
    comment="Refresh token süresi dolma tarihi")
    refresh_token_last_used_at = Column(DateTime(timezone=True), nullable=True,
    comment="Refresh token son kullanım tarihi")

    # ---- Session Information ---- #
    is_revoked = Column(Boolean, default=False, nullable=False, index=True,
    comment="Oturum iptal edildi mi?")
    revoked_at = Column(DateTime(timezone=True), nullable=True,
    comment="Oturum iptal edildiği tarih")
    revoked_by = Column(String(20), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True,
    comment="Oturum iptal eden kullanıcı id'si")
    revocation_at = Column(DateTime(timezone=True), nullable=True,
    comment="Oturum iptal edilme tarihi")
    revocation_reason = Column(Text, nullable=True,
    comment="Oturum iptal edilme nedeni")

    # ---- Session Details ---- #
    ip_address = Column(String(64), nullable=False,
    comment="Oturum başlatıldığı IP adresi")
    user_agent = Column(String(512), nullable=False,
    comment="Oturum başlatıldığı user agent")
    location = Column(String(255), nullable=False,
    comment="Oturum başlatıldığı konum")
    device_type = Column(String(50), nullable=False,
    comment="Oturum başlatıldığı cihaz tipi")
    device_name = Column(String(255), nullable=False,
    comment="Oturum başlatıldığı cihaz adı")

    # ---- Relations ---- #
    user = relationship("User", foreign_keys=[user_id], back_populates="auth_sessions")
    revoker = relationship("User", foreign_keys=[revoked_by])
    login_history = relationship("LoginHistory", back_populates="session")