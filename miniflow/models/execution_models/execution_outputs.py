from sqlalchemy import Column, String, ForeignKey, Integer, Text, Float, Enum, DateTime, JSON, Index
from sqlalchemy.orm import relationship

from miniflow.database.models import Base
from miniflow.database.models.mixins import TimestampMixin
from miniflow.models.enums import ExecutionStatuses


class ExecutionOutput(Base, TimestampMixin):
    """Execution output - Node çalıştırma sonuçları"""
    __prefix__ = "EXO"
    __tablename__ = "execution_outputs"
    
    # ---- Table Args ---- #
    __table_args__ = (
        Index('idx_execution_outputs_execution_node', 'execution_id', 'node_id'),
        Index('idx_execution_outputs_execution_status', 'execution_id', 'status'),
    )

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

    # ---- Execution Status ---- #
    status = Column(Enum(ExecutionStatuses), nullable=False, index=True,
    comment="Çalıştırma durumu")
    started_at = Column(DateTime(timezone=True), nullable=True, index=True,
    comment="Başlangıç zamanı")
    ended_at = Column(DateTime(timezone=True), nullable=True,
    comment="Bitiş zamanı")
    duration_seconds = Column(Float, nullable=True,
    comment="Çalışma süresi (saniye)")
    retry_count = Column(Integer, default=0, nullable=False,
    comment="Retry sayısı")

    # ---- Output Data ---- #
    output_data = Column(JSON, nullable=True, default=lambda: {},
    comment="Çıktı verileri (output_schema'ya uygun)")

    # ---- Error Data ---- #
    error_type = Column(String(100), nullable=True,
    comment="Hata tipi")
    error_message = Column(Text, nullable=True,
    comment="Hata mesajı")
    error_traceback = Column(Text, nullable=True,
    comment="Hata stack trace")

    # ---- Relationships ---- #
    execution = relationship("Execution", back_populates="execution_outputs")
    workspace = relationship("Workspace", back_populates="execution_outputs")
    workflow = relationship("Workflow", back_populates="execution_outputs")
    node = relationship("Node", back_populates="execution_outputs")
    global_script = relationship("Script", back_populates="execution_outputs")
    custom_script = relationship("CustomScript", back_populates="execution_outputs")

    # ---- Helper Methods ---- #
    @property
    def script(self):
        """Aktif script'i döndürür"""
        return self.global_script or self.custom_script
    
    @property
    def script_id(self):
        """Aktif script ID'sini döndürür"""
        return self.global_script_id or self.custom_script_id
    
    @property
    def is_success(self) -> bool:
        return self.status == ExecutionStatuses.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        return self.status == ExecutionStatuses.FAILED