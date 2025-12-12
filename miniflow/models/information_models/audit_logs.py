from sqlalchemy import Column, String, Text, JSON, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship

from miniflow.database.models import Base
from miniflow.database.models.mixins import TimestampMixin
from miniflow.models.enums import AuditActionTypes


class AuditLog(Base, TimestampMixin):
    __prefix__ = "EXE"
    __tablename__ = "executions"

    # ---- User Context ---- #
    user_id = Column(String(20), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True,
    comment="AuditLog'un ait olduğu kullanıcının id'si")
    user_email = Column(String(255), nullable=True,
    comment="AuditLog'un ait olduğu kullanıcının e-posta adresi")
    user_name = Column(String(255), nullable=True,
    comment="İşlemi yapan kullanıcının adı")

    # ---- Action Context ---- #
    action_type = Column(Enum(AuditActionTypes), nullable=False, index=True,
    comment="Yapılan işlem tipi")
    action_description = Column(Text, nullable=True,
    comment="Yapılan işlemin açıklaması")
    resource_type = Column(String(100), nullable=False, index=True,
    comment="İşlem yapılan kaynak tipi (user, workflow, ticket vb.)")
    resource_id = Column(String(20), nullable=True, index=True,
    comment="İşlem yapılan kaynağın id'si")

    # ---- Relations ---- #
    user = relationship("User", back_populates="audit_logs")