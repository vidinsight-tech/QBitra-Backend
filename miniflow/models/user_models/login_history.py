from sqlalchemy import Column, String, DateTime, Boolean, Text, Enum, Index
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from miniflow.database.models import Base
from miniflow.database.models.mixins import SoftDeleteMixin, TimestampMixin
from miniflow.models.enums import LoginStatus, LoginMethod

class LoginHistory(Base, SoftDeleteMixin, TimestampMixin):
    """Kullanıcı giriş geçmişi modeli"""
    __prefix__ = "LGH"
    __tablename__ = "login_history"
    
    # ---- Table Args ---- #
    __table_args__ = (
        Index('idx_login_history_user_date', 'user_id', 'login_at'),
        Index('idx_login_history_softdelete', 'is_deleted', 'created_at'),
    )

    # ---- Login History  ---- #
    user_id = Column(String(20), ForeignKey("users.id", ondelete="CASCADE"), nullable=False,
    comment="Kullanıcı id'si (otomatik oturum yönetimi için)")
    session_id = Column(String(20), ForeignKey("auth_sessions.id", ondelete="CASCADE"), nullable=True, index=True,
    comment="Oturum id'si (otomatik oturum yönetimi için)")

    # ---- Login History Information ---- #
    login_at = Column(DateTime(timezone=True), nullable=False, index=True,
    comment="Giriş tarihi (otomatik oturum yönetimi için)")
    status = Column(Enum(LoginStatus), nullable=False, index=True,
    comment="Giriş denemesi sonucu (success, failed, locked, suspended)")
    login_method = Column(Enum(LoginMethod), nullable=False, default=LoginMethod.PASSWORD, index=True,
    comment="Giriş için kullanılan yöntem (password, google, other)")

    # ---- Login History Details ---- #
    ip_address = Column(String(64), nullable=False, index=True,
    comment="Giriş yapılan IP adresi")
    user_agent = Column(String(512), nullable=False,
    comment="Giriş yapılan user agent")
    location = Column(String(255), nullable=False,
    comment="Giriş yapılan konum")
    device_type = Column(String(50), nullable=False,
    comment="Giriş yapılan cihaz tipi")
    device_name = Column(String(255), nullable=False,
    comment="Giriş yapılan cihaz adı")

    # ---- Relations ---- #
    user = relationship("User", back_populates="login_history")
    session = relationship("AuthSession", back_populates="login_history")