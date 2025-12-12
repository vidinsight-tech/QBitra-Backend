from sqlalchemy import Column, String, ForeignKey, Integer, Enum, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import timezone

from miniflow.database.models import Base
from miniflow.models.enums import ExecutionStatuses

class Execution(Base):
    __prefix__ = "EXE"
    __tablename__ = "executions"

    # ---- Relationships ---- #
    workspace_id = Column(String(20), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True,
    comment="Execution'in ait olduğu workspace id'si")
    wokflow_id = Column(String(20), ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False, index=True,
    comment="Execution'in ait olduğu workflow id'si")
    trigger_id = Column(String(20), ForeignKey("triggers.id", ondelete="CASCADE"), nullable=False, index=True,
    comment="Execution'in ait olduğu trigger id'si")
    parent_execution_id = Column(String(20), ForeignKey("executions.id", ondelete="CASCADE"), nullable=True, index=True,
    comment="Execution'in ait olduğu parent execution id'si")

    # ---- Execution Content ---- #
    status = Column(Enum(ExecutionStatuses), nullable=False,
    comment="Execution'in durumu")
    start_time = Column(DateTime(timezone=True), nullable=False,
    comment="Execution'in başlangıç zamanı")
    end_time = Column(DateTime(timezone=True), nullable=True,
    comment="Execution'in bitiş zamanı")
    input_data = Column(JSON, nullable=True,
    comment="Execution'in giriş verileri")
    output_data = Column(JSON, nullable=True,
    comment="Execution'in çıktı verileri")
    
    # ---- Relations ---- #
    workspace = relationship("Workspace", back_populates="executions")
    workflow = relationship("Workflow", back_populates="executions")
    trigger = relationship("Trigger", back_populates="executions")
    parent_execution = relationship("Execution", back_populates="executions")
    child_executions = relationship("Execution", back_populates="parent_execution")
    execution_inputs = relationship("ExecutionInput", back_populates="executions", cascade="all, delete-orphan")
    execution_outputs = relationship("ExecutionOutput", back_populates="executions", cascade="all, delete-orphan")

    # Helper Methods ---- #
    @property
    def duration(self):
        if self.start_time and self.end_time:
            ended_at = self.end_time
            started_at = self.start_time

            if ended_at.tzinfo is None and started_at.tzinfo is not None:
                ended_at = ended_at.replace(tzinfo=timezone.utc)
            elif ended_at.tzinfo is not None and started_at.tzinfo is None:
                started_at = started_at.replace(tzinfo=timezone.utc)

            delta = ended_at - started_at
            return delta.total_seconds()
        return -1