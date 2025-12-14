from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Text, Boolean, DateTime, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.orm import relationship

from miniflow.database.models import Base
from miniflow.database.models.mixins import SoftDeleteMixin, TimestampMixin


class ApiKey(Base, SoftDeleteMixin, TimestampMixin):
    """API anahtarları - Workspace içinde kullanılan API key'leri yönetir"""
    __prefix__ = "API"
    __tablename__ = 'api_keys'
    __allow_unmapped__ = True


    # ---- Relationships ---- #
    workspace_id = Column(String(20), ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=False, index=True,
    comment="Hangi workspace'de")
    owner_id = Column(String(20), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True,
    comment="API key sahibi (kim oluşturdu)")

    # ---- Basic Information ---- #
    name = Column(String(100), nullable=False, index=True,
    comment="API key adı (user+workspace bazında benzersiz)")
    description = Column(Text, nullable=True,
    comment="API key açıklaması")
    
    # ---- Key Information - Security ---- #
    key_prefix = Column(String(20), nullable=False,
    comment="Görünen prefix (sk_live_, sk_test_)")
    key_hash = Column(String(255), nullable=False, unique=True, index=True,
    comment="Tam key hash (güvenli saklama - bcrypt veya argon2)")
    
    # ---- Permissions - Detailed permissions with JSON ---- #
    permissions = Column(JSON, default=lambda: {
        "workflows": {
            "execute": True,
            "read": True,
            "write": False,
            "delete": False
        },
        "credentials": {
            "read": True,
            "write": False,
            "delete": False
        },
        "databases": {
            "read": True,
            "write": False,
            "delete": False
        },
        "variables": {
            "read": True,
            "write": False,
            "delete": False
        },
        "files": {
            "read": True,
            "write": False,
            "delete": False
        }
    }, nullable=False,
        comment="API key izinleri")
    
    # ---- Status ---- #
    is_active = Column(Boolean, default=True, nullable=False, index=True,
    comment="API key aktif mi?")
    expires_at = Column(DateTime(timezone=True), nullable=True, index=True,
    comment="Geçerlilik süresi bitiş tarihi")
    last_used_at = Column(DateTime(timezone=True), nullable=True,
    comment="Son kullanım zamanı")
    usage_count = Column(Integer, default=0, nullable=False,
    comment="Kullanım sayısı")
    
    # ---- Request Limits ---- #
    rate_limit_per_minute = Column(Integer, nullable=True,
    comment="Dakikada maksimum istek sayısı (None = sınırsız)")
    rate_limit_per_hour = Column(Integer, nullable=True,
    comment="Saatte maksimum istek sayısı (None = sınırsız)")
    rate_limit_per_day = Column(Integer, nullable=True,
     comment="Günde maksimum istek sayısı (None = sınırsız)")
    
    # ---- Security - IP whitelist ---- #
    allowed_ips = Column(JSON, default=lambda: [], nullable=True,
    comment="İzin verilen IP adresleri (JSON array, [] = tüm IP'lere izin verilir)")
    
    # ---- Metadata ---- #
    tags = Column(JSON, default=lambda: [], nullable=True,
    comment="Etiketler (JSON array)")

    # ---- Relationships ---- #
    workspace = relationship("Workspace", back_populates="api_keys")
    owner = relationship("User", foreign_keys=[owner_id], back_populates="api_keys")
