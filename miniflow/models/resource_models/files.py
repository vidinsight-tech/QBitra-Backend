from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer, JSON, BigInteger, UniqueConstraint, Index
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from miniflow.database.models import Base
from miniflow.database.models.mixins import SoftDeleteMixin, TimestampMixin


class File(Base, SoftDeleteMixin, TimestampMixin):
    """Yüklenen dosyalar - Workspace içinde upload edilen dosyaları yönetir"""
    __prefix__ = "FLE"
    __tablename__ = "files"
    
    # ---- Table Args ---- #
    __table_args__ = (
        UniqueConstraint('workspace_id', 'name', name='uq_file_workspace_name'),
        Index('idx_files_workspace_mime', 'workspace_id', 'mime_type'),
        Index('idx_files_owner_created', 'owner_id', 'created_at'),
        Index('idx_files_softdelete', 'is_deleted', 'created_at'),
    )

    # ---- Relationships ---- #
    workspace_id = Column(String(20), ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=False, index=True,
    comment="Hangi workspace'de")
    owner_id = Column(String(20), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True,
    comment="Dosyayı upload eden kullanıcı")

    # ---- File Information - File helper compatible ---- #
    name = Column(String(255), nullable=False, index=True,
    comment="Dosya adı (workspace içinde benzersiz)")
    original_filename = Column(String(255), nullable=False,
    comment="Orijinal dosya adı")
    file_path = Column(String(512), nullable=False, unique=True, index=True,
    comment="Dosya yolu (file helper formatında)")
    file_size = Column(BigInteger, nullable=False,
    comment="Dosya boyutu (byte)")
    mime_type = Column(String(100), nullable=True, index=True,
    comment="Dosya MIME tipi")
    file_extension = Column(String(20), nullable=True,
    comment="Dosya uzantısı")
    file_hash = Column(String(64), nullable=True, index=True,
    comment="Dosyanın hash değeri (SHA-256)")

    # ---- Metadata ---- #
    description = Column(Text, nullable=True,
    comment="Dosya açıklaması")
    tags = Column(JSON, default=lambda: [], nullable=True,
    comment="Etiketler (JSON array)")
    file_metadata = Column(JSON, default=lambda: {}, nullable=True,
    comment="Ek metadata (JSON object)")

    # ---- Relationships ---- #
    workspace = relationship("Workspace", back_populates="files")
    owner = relationship("User", foreign_keys=[owner_id], back_populates="uploaded_files")
