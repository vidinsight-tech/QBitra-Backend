from sqlalchemy import Column, String, ForeignKey, Integer, Enum, DateTime, JSON
from sqlalchemy.orm import relationship

from miniflow.database.models import Base

class ExecutionInput(Base):
    __prefix__ = "EXI"
    __tablename__ = "execution_inputs"

    # ---- Relationships ---- #
    execution_id = Column(String(20), ForeignKey("executions.id", ondelete="CASCADE"), nullable=False, index=True,
    comment="ExecutionInput'in ait olduğu execution id'si")
    workspace_id = Column(String(20), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True,
    comment="ExecutionInput'in ait olduğu workspace id'si")
    wokflow_id = Column(String(20), ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False, index=True,
    comment="ExecutionInput'in ait olduğu workflow id'si")
    node_id = Column(String(20), ForeignKey("nodes.id", ondelete="CASCADE"), nullable=False, index=True,
    comment="ExecutionInput'in ait olduğu node id'si")
    script_id = Column(String(20), ForeignKey("scripts.id", ondelete="CASCADE"), nullable=False, index=True,
    comment="ExecutionInput'in ait olduğu script id'si")

    # ---- Execution Input Content ---- #
    dependecy_count = Column(Integer, nullable=False, default=0,
    comment="ExecutionInput'in bağımlılık sayısı")
    priority = Column(Integer, nullable=False, default=0,
    comment="ExecutionInput'in önceliği")
    waiting_for = Column(Integer, nullable=True, default=0,
    comment="ExecutionInput'in hazır olup beklediği tur sayısı")

    # ---- Execution Input Parameters ---- #
    max_retries = Column(Integer, nullable=False, default=3,
    comment="ExecutionInput'in maksimum retry sayısı")
    timeout_seconds = Column(Integer, nullable=False, default=300,
    comment="ExecutionInput'in timeout süresi (saniye)")

    # ---- Execution Input Node Parameters ---- #
    node_name = Column(String(255), nullable=False,
    comment="ExecutionInput'in ait olduğu node adı")
    node_parameters = Column(JSON, nullable=True,
    comment="ExecutionInput'in ait olduğu node parametreleri")
    
    # ---- Execution Input Script Parameters ---- #
    script_name = Column(String(255), nullable=False,
    comment="ExecutionInput'in ait olduğu script adı")
    script_path = Column(String(512), nullable=False,
    comment="ExecutionInput'in ait olduğu script path")

    # ---- Relations ---- #
    execution = relationship("Execution", back_populates="execution_inputs")
    workspace = relationship("Workspace", back_populates="execution_inputs")
    workflow = relationship("Workflow", back_populates="execution_inputs")
    node = relationship("Node", back_populates="execution_inputs")
    script = relationship("Script", back_populates="execution_inputs")