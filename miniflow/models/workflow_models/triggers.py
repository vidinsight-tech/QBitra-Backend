from enum import Enum
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Boolean, Text, JSON
from sqlalchemy.orm import relationship, ForeignKey

from miniflow.database.models import Base
from miniflow.database.models.mixins import SoftDeleteMixin
from miniflow.models.enums import TriggerTypes

class Trigger(Base, SoftDeleteMixin):
    """Workflow trigger modeli"""
    __prefix__ = "TR"
    __tablename__ = "triggers"
    __allow_unmapped__ = True

    # ---- Trigger ---- #
    workflow_id = Column(String(20), ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False, index=True,
    comment="Trigger'un ait olduğu workflow id'si")

    # ---- Trigger Content ---- #
    name = Column(String(255), nullable=False,
    comment="Trigger'un adı")
    description = Column(Text, nullable=True,
    comment="Trigger'un açıklaması")
    trigger_type = Column(Enum(TriggerTypes), nullable=False,
    comment="Trigger'un tipi")
    configuration = Column(JSON, nullable=True,
    comment="Trigger'un yapılandırması")
    is_active = Column(Boolean, default=True, nullable=False,
    comment="Trigger'un aktif mi?")
    input_schema = Column(JSON, nullable=True,
    comment="Trigger'un giriş şeması")

    # ---- Relations ---- #
    workflow = relationship("Workflow", back_populates="triggers")
    executions = relationship("Execution", back_populates="trigger")