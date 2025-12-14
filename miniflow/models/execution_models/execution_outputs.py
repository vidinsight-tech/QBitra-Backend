from sqlalchemy import Column, String, ForeignKey, Integer, Enum, DateTime, JSON
from sqlalchemy.orm import relationship

from miniflow.database.models import Base
from miniflow.models.enums import ExecutionStatuses

class ExecutionOutput(Base):
    __prefix__ = "EXO"
    __tablename__ = "execution_outputs"

    # ---- Relationships ---- #
    execution_id = Column(String(20), ForeignKey("executions.id", ondelete="CASCADE"), nullable=False, index=True,
    comment="ExecutionOutput'in ait olduğu execution id'si")
    workspace_id = Column(String(20), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True,
    comment="ExecutionOutput'in ait olduğu workspace id'si")
    workflow_id = Column(String(20), ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False, index=True,
    comment="ExecutionOutput'in ait olduğu workflow id'si")
    node_id = Column(String(20), ForeignKey("nodes.id", ondelete="CASCADE"), nullable=False, index=True,
    comment="ExecutionOutput'in ait olduğu node id'si")
    script_id = Column(String(20), ForeignKey("scripts.id", ondelete="CASCADE"), nullable=False, index=True,
    comment="ExecutionOutput'in ait olduğu script id'si")

    # ---- Execution Output Content ---- #
    status = Column(Enum(ExecutionStatuses), nullable=False,
    comment="ExecutionOutput'in durumu")
    started_at = Column(DateTime(timezone=True), nullable=True, index=True,
    comment="ExecutionOutput'in başlangıç zamanı")
    ended_at = Column(DateTime(timezone=True), nullable=True,
    comment="ExecutionOutput'in bitiş zamanı")
    data = Column(JSON, nullable=True, default=lambda: {},
    comment="ExecutionOutput'in verileri")

    # ---- Execution Error Data ---- #
    error_message = Column(String(255), nullable=True,
    comment="ExecutionOutput'in hata mesajı")
    error_code = Column(Integer, nullable=True,
    comment="ExecutionOutput'in hata kodu")
    error_type = Column(String(255), nullable=True,
    comment="ExecutionOutput'in hata tipi")

    # ---- Relations ---- #
    execution = relationship("Execution", back_populates="execution_outputs")
    workspace = relationship("Workspace", back_populates="execution_outputs")
    workflow = relationship("Workflow", back_populates="execution_outputs")
    node = relationship("Node", back_populates="execution_outputs")
    script = relationship("Script", back_populates="execution_outputs")