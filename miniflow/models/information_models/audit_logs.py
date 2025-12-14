from sqlalchemy import Column, String, Text, JSON, ForeignKey, Enum
from sqlalchemy.orm import relationship

from miniflow.database.models import Base
from miniflow.database.models.mixins import TimestampMixin
from miniflow.models.enums import AuditActionTypes


class AuditLog(Base, TimestampMixin):
    """Audit log - Workspace'te yapılan tüm işlemlerin kaydı"""
    __prefix__ = "AUD"
    __tablename__ = "audit_logs"
    __allow_unmapped__ = True

    # ---- Workspace Context ---- #
    workspace_id = Column(String(20), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True,
    comment="İşlemin yapıldığı workspace")

    # ---- User Context ---- #
    user_id = Column(String(20), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True,
    comment="İşlemi yapan kullanıcı")
    user_email = Column(String(255), nullable=True,
    comment="Kullanıcı email (user silinse bile kayıt için)")
    user_name = Column(String(255), nullable=True,
    comment="Kullanıcı adı (user silinse bile kayıt için)")

    # ---- Action Details ---- #
    action_type = Column(Enum(AuditActionTypes), nullable=False, index=True,
    comment="İşlem tipi (CREATE, UPDATE, DELETE, EXECUTE, vb.)")
    action_description = Column(Text, nullable=True,
    comment="İşlem açıklaması")

    # ---- Resource Context ---- #
    resource_type = Column(String(50), nullable=False, index=True,
    comment="Kaynak tipi (workflow, node, credential, database, file, variable, api_key, member)")
    resource_id = Column(String(20), nullable=True, index=True,
    comment="Kaynak ID'si")
    resource_name = Column(String(255), nullable=True,
    comment="Kaynak adı (kaynak silinse bile kayıt için)")

    # ---- Change Tracking ---- #
    old_value = Column(JSON, nullable=True,
    comment="Değişiklik öncesi değer (JSON)")
    new_value = Column(JSON, nullable=True,
    comment="Değişiklik sonrası değer (JSON)")

    # ---- Additional Context ---- #
    metadata = Column(JSON, nullable=True,
    comment="Ek bilgiler (JSON)")

    # ---- Relationships ---- #
    workspace = relationship("Workspace", back_populates="audit_logs")
    user = relationship("User", back_populates="audit_logs")