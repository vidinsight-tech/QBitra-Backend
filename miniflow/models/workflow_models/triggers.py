from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Boolean, Text, JSON, Enum, Index
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from miniflow.database.models import Base
from miniflow.database.models.mixins import SoftDeleteMixin, TimestampMixin
from miniflow.models.enums import TriggerTypes

class Trigger(Base, SoftDeleteMixin, TimestampMixin):
    """Workflow trigger modeli"""
    __prefix__ = "TRG"
    __tablename__ = "triggers"
    
    # ---- Table Args ---- #
    __table_args__ = (
        Index('idx_triggers_workflow_active', 'workflow_id', 'is_active'),
        Index('idx_triggers_workflow_type', 'workflow_id', 'trigger_type'),
        Index('idx_triggers_softdelete', 'is_deleted', 'created_at'),
    )

    # ---- Trigger ---- #
    workflow_id = Column(String(20), ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False, index=True,
    comment="Trigger'un ait olduğu workflow id'si")

    # ---- Trigger Content ---- #
    name = Column(String(255), nullable=False, index=True,
    comment="Trigger'un adı")
    description = Column(Text, nullable=True,
    comment="Trigger'un açıklaması")
    trigger_type = Column(Enum(TriggerTypes), nullable=False, index=True,
    comment="Trigger'un tipi")
    configuration = Column(JSON, nullable=True,
    comment="Trigger'un yapılandırması")
    is_active = Column(Boolean, default=True, nullable=False, index=True,
    comment="Trigger'un aktif mi?")
    input_schema = Column(JSON, nullable=True,
    comment="Trigger'un giriş şeması")

    # ---- Relations ---- #
    workflow = relationship("Workflow", back_populates="triggers")
    executions = relationship("Execution", back_populates="trigger")