from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer, JSON
from sqlalchemy.orm import relationship, ForeignKey

from miniflow.database.models import Base
from miniflow.database.models.mixins import SoftDeleteMixin

class Workflow(Base, SoftDeleteMixin):
    """Workflow modeli"""
    __prefix__ = "WF"
    __tablename__ = "workflows"
    __allow_unmapped__ = True

    workspace_id = Column(String(20), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True,
    comment="Workflow'un ait olduğu workspace id'si")

    # ---- Workflow Content ---- #
    name = Column(String(255), nullable=False,
    comment="Workflow'un adı")
    description = Column(Text, nullable=True,
    comment="Workflow'un açıklaması")
    priority = Column(Integer, nullable=False, default=0,
    comment="Workflow'un önceliği")
    tags = Column(JSON, default=lambda: [], nullable=True,
    comment="Workflow'un etiketleri (JSON array)")

    # ---- Relations ---- #
    workspace = relationship("Workspace", back_populates="workflows")
    nodes = relationship("Node", back_populates="workflow", cascade="all, delete-orphan")
    edges = relationship("Edge", back_populates="workflow", cascade="all, delete-orphan")
    triggers = relationship("Trigger", back_populates="workflow", cascade="all, delete-orphan")
    executions = relationship("Execution", back_populates="workflow", cascade="all, delete-orphan")
    execution_inputs = relationship("ExecutionInput", back_populates="workflow")
    execution_outputs = relationship("ExecutionOutput", back_populates="workflow")