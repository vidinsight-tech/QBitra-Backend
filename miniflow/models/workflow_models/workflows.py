from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer, JSON, UniqueConstraint, Index
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from miniflow.database.models import Base
from miniflow.database.models.mixins import SoftDeleteMixin, TimestampMixin

class Workflow(Base, SoftDeleteMixin, TimestampMixin):
    """Workflow modeli"""
    __prefix__ = "WFL"
    __tablename__ = "workflows"
    
    # ---- Table Args ---- #
    __table_args__ = (
        UniqueConstraint('workspace_id', 'name', name='uq_workflow_workspace_name'),
        Index('idx_workflows_softdelete', 'is_deleted', 'created_at'),
    )

    workspace_id = Column(String(20), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True,
    comment="Workflow'un ait olduğu workspace id'si")

    # ---- Workflow Content ---- #
    name = Column(String(255), nullable=False, index=True,
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