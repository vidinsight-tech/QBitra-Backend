from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Boolean, Text, JSON, Integer
from sqlalchemy.orm import relationship, ForeignKey

from miniflow.database.models import Base
from miniflow.database.models.mixins import SoftDeleteMixin

class Node(Base, SoftDeleteMixin):
    """Workflow node modeli"""
    __prefix__ = "ND"
    __tablename__ = "nodes"
    __allow_unmapped__ = True

    # ---- Node ---- #
    workflow_id = Column(String(20), ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False, index=True,
    comment="Node'in ait olduğu workflow id'si")
    global_script_id = Column(String(20), ForeignKey("scripts.id", ondelete="CASCADE"), nullable=False, index=True,
    comment="Node'in ait olduğu global script id'si (global script'in workflow'a bağlı olmadan çalıştırılması için)")
    custom_script_id = Column(String(20), ForeignKey("custom_scripts.id", ondelete="CASCADE"), nullable=True, index=True,
    comment="Node'in ait olduğu custom script id'si (custom script'in workflow'a bağlı olarak çalıştırılması için)")

    # ---- Node Content ---- #
    name = Column(String(255), nullable=False,
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
    metadata = Column(JSON, nullable=True, default=lambda: {},
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
        if self.global_script:
            return self.global_script
        if self.custom_script:
            return self.custom_script
        return None