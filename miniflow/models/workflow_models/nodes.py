from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Boolean, Text, JSON, Integer, Index
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from miniflow.database.models import Base
from miniflow.database.models.mixins import SoftDeleteMixin, TimestampMixin

class Node(Base, SoftDeleteMixin, TimestampMixin):
    """Workflow node modeli"""
    __prefix__ = "NOD"
    __tablename__ = "nodes"
    
    # ---- Table Args ---- #
    __table_args__ = (
        Index('idx_nodes_workflow_name', 'workflow_id', 'name'),
        Index('idx_nodes_softdelete', 'is_deleted', 'created_at'),
    )

    # ---- Relationships ---- #
    workflow_id = Column(String(20), ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False, index=True,
    comment="Node'in ait olduğu workflow id'si")
    global_script_id = Column(String(20), ForeignKey("scripts.id", ondelete="SET NULL"), nullable=True, index=True,
    comment="Global script id'si (global_script veya custom_script'den biri zorunlu)")
    custom_script_id = Column(String(20), ForeignKey("custom_scripts.id", ondelete="SET NULL"), nullable=True, index=True,
    comment="Custom script id'si (global_script veya custom_script'den biri zorunlu)")

    # ---- Node Content ---- #
    name = Column(String(255), nullable=False, index=True,
    comment="Node'un adı")
    description = Column(Text, nullable=True,
    comment="Node'un açıklaması")
    max_retries = Column(Integer, nullable=False, default=3,
    comment="Node'un maksimum retry sayısı")
    timeout_seconds = Column(Integer, nullable=False, default=300,
    comment="Node'un timeout süresi (saniye)")

    input_schema = Column(JSON, nullable=True, default=lambda: {},
    comment="Node'un giriş şeması")
    output_schema = Column(JSON, nullable=True, default=lambda: {},
    comment="Node'un çıktı şeması")
    node_metadata = Column(JSON, nullable=True, default=lambda: {},
    comment="Node'un meta verileri")
    
    # ---- Relations ---- # 
    workflow = relationship("Workflow", back_populates="nodes")
    global_script = relationship("Script", foreign_keys=[global_script_id], back_populates="nodes_as_global")
    custom_script = relationship("CustomScript", foreign_keys=[custom_script_id], back_populates="nodes")
    edges_as_source = relationship("Edge", foreign_keys="Edge.source_node_id", back_populates="source_node")
    edges_as_target = relationship("Edge", foreign_keys="Edge.target_node_id", back_populates="target_node")
    execution_inputs = relationship("ExecutionInput", back_populates="node")
    execution_outputs = relationship("ExecutionOutput", back_populates="node")

    # ---- Helper Methods ---- #
    @property
    def script(self):
        """Aktif script'i döndürür (global veya custom)"""
        return self.global_script or self.custom_script
    
    @property
    def script_id(self):
        """Aktif script ID'sini döndürür"""
        return self.global_script_id or self.custom_script_id
    
    @property
    def is_global_script(self) -> bool:
        """Global script mi?"""
        return self.global_script_id is not None
    
    @property
    def is_custom_script(self) -> bool:
        """Custom script mi?"""
        return self.custom_script_id is not None