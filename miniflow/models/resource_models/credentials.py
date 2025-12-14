from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, JSON, Enum, UniqueConstraint
from sqlalchemy.orm import relationship

from miniflow.database.models import Base
from miniflow.database.models.mixins import SoftDeleteMixin, TimestampMixin
from miniflow.models.enums import CredentialType


class Credential(Base, SoftDeleteMixin, TimestampMixin):
    """API credentials ve secrets - Workspace içinde kullanılan API credentials ve secrets'ı yönetir"""
    __prefix__ = "CRD"
    __tablename__ = 'credentials'
    __allow_unmapped__ = True

    # ---- Relationships ---- #
    workspace_id = Column(String(20), ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=False, index=True,
    comment="Hangi workspace'de")
    owner_id = Column(String(20), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True,
    comment="Credential sahibinin ID'si")

    # ---- Basic Information ---- #
    name = Column(String(100), nullable=False, index=True,
    comment="Credential adı (workspace içinde benzersiz)")
    credential_type = Column(Enum(CredentialType), nullable=False, index=True,
    comment="Credential tipi (API_KEY, OAUTH2, BASIC_AUTH, vb.)")
    credential_provider = Column(String(50), nullable=True, index=True,
    comment="Credential provider (sadece OAuth2 için: GOOGLE, MICROSOFT, GITHUB)")
    description = Column(Text, nullable=True,
    comment="Credential açıklaması")

    # ---- Credential Information - All JSON encrypted ---- #
    credential_data = Column(JSON, nullable=False,
    comment="Tüm credential detayları ile şifrelenmiş JSON")

    # ---- Status ---- #
    is_active = Column(Boolean, default=True, nullable=False, index=True,
    comment="Credential aktif mi?")
    expires_at = Column(DateTime(timezone=True), nullable=True, index=True,
    comment="Geçerlilik süresi bitiş tarihi")
    last_used_at = Column(DateTime(timezone=True), nullable=True,
    comment="Son kullanım zamanı")

    # ---- Metadata ---- #
    tags = Column(JSON, default=lambda: [], nullable=True,
    comment="Etiketler (JSON array)")

    # ---- Relationships ---- #
    workspace = relationship("Workspace", back_populates="credentials")
    owner = relationship("User", foreign_keys=[owner_id], back_populates="credentials")
