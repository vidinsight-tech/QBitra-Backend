from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Boolean, Text, JSON, UniqueConstraint, Enum
from sqlalchemy.orm import relationship, ForeignKey

from miniflow.database.models import Base
from miniflow.database.models.mixins import SoftDeleteMixin, TimestampMixin
from miniflow.models.enums import VariableType


class Variable(Base, SoftDeleteMixin, TimestampMixin):
    """Workspace environment variable'ları - Workspace içinde kullanılan environment variable'ları yönetir"""
    __prefix__ = "ENV"
    __tablename__ = "variables"
    __allow_unmapped__ = True

    # İlişkiler
    workspace_id = Column(String(20), ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=False, index=True,
    comment="Hangi workspace'de")
    owner_id = Column(String(20), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True,
    comment="Variable'ı oluşturan kullanıcı")

    # Variable verisi
    key = Column(String(100), nullable=False, index=True,
    comment="Variable anahtarı (workspace içinde benzersiz)")
    type = Column(Enum(VariableType), nullable=False, index=True,
    comment="Variable tipi (STRING, NUMBER, BOOLEAN, JSON, LIST, DICT)")
    value = Column(Text, nullable=False,
    comment="Variable değeri (is_secret=True ise şifrelenmiş)")
    description = Column(Text, nullable=True,
    comment="Variable açıklaması")
    is_secret = Column(Boolean, default=False, nullable=False, index=True,
    comment="Gizli mi? (şifreler, token'lar için - is_secret=True ise value şifrelenmiş saklanmalı)")

    # İlişkiler
    workspace = relationship("Workspace", back_populates="variables")
    owner = relationship("User", foreign_keys=[owner_id], back_populates="created_variables")
