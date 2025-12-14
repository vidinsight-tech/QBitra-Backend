from sqlalchemy import Column, String, ForeignKey, Integer, JSON
from sqlalchemy.orm import relationship

from miniflow.database.models import Base
from miniflow.database.models.mixins import TimestampMixin


class ExecutionInput(Base, TimestampMixin):
    """Execution input - Node çalıştırma için hazırlanan input verileri"""
    __prefix__ = "EXI"
    __tablename__ = "execution_inputs"
    __allow_unmapped__ = True

    # ---- Relationships ---- #
    execution_id = Column(String(20), ForeignKey("executions.id", ondelete="CASCADE"), nullable=False, index=True,
    comment="Execution id'si")
    workspace_id = Column(String(20), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True,
    comment="Workspace id'si")
    workflow_id = Column(String(20), ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False, index=True,
    comment="Workflow id'si")
    node_id = Column(String(20), ForeignKey("nodes.id", ondelete="CASCADE"), nullable=False, index=True,
    comment="Node id'si")
    global_script_id = Column(String(20), ForeignKey("scripts.id", ondelete="SET NULL"), nullable=True, index=True,
    comment="Global script id'si (global veya custom'dan biri)")
    custom_script_id = Column(String(20), ForeignKey("custom_scripts.id", ondelete="SET NULL"), nullable=True, index=True,
    comment="Custom script id'si (global veya custom'dan biri)")

    # ---- Execution Queue ---- #
    dependency_count = Column(Integer, nullable=False, default=0,
    comment="Bağımlılık sayısı")
    priority = Column(Integer, nullable=False, default=0,
    comment="Öncelik")
    waiting_for = Column(Integer, nullable=True, default=0,
    comment="Beklenen döngü sayısı")

    # ---- Node Configuration ---- #
    node_name = Column(String(255), nullable=False,
    comment="Node adı")
    max_retries = Column(Integer, nullable=False, default=3,
    comment="Maksimum retry sayısı")
    timeout_seconds = Column(Integer, nullable=False, default=300,
    comment="Timeout süresi (saniye)")

    # ---- Input Data ---- #
    input_schema = Column(JSON, nullable=True, default=lambda: {},
    comment="Doldurulmuş input schema (x-resource-bindings dahil)")
    resolved_input = Column(JSON, nullable=True, default=lambda: {},
    comment="Reference'ları çözülmüş input verileri")
    
    # ---- Script Info ---- #
    script_name = Column(String(255), nullable=False,
    comment="Script adı")
    script_path = Column(String(512), nullable=True,
    comment="Script dosya yolu")

    # ---- Relationships ---- #
    execution = relationship("Execution", back_populates="execution_inputs")
    workspace = relationship("Workspace", back_populates="execution_inputs")
    workflow = relationship("Workflow", back_populates="execution_inputs")
    node = relationship("Node", back_populates="execution_inputs")
    global_script = relationship("Script", back_populates="execution_inputs")
    custom_script = relationship("CustomScript", back_populates="execution_inputs")

    # ---- Helper Methods ---- #
    @property
    def script(self):
        """Aktif script'i döndürür"""
        return self.global_script or self.custom_script
    
    @property
    def script_id(self):
        """Aktif script ID'sini döndürür"""
        return self.global_script_id or self.custom_script_id