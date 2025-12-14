from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Boolean, Text
from sqlalchemy.orm import relationship, ForeignKey

from miniflow.database.models import Base
from miniflow.database.models.mixins import SoftDeleteMixin

class Edge(Base, SoftDeleteMixin):
    """Workflow edge modeli"""
    __prefix__ = "ED"
    __tablename__ = "edges"
    __allow_unmapped__ = True

    # ---- Edge ---- #
    workflow_id = Column(String(20), ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False, index=True,
    comment="Edge'in ait olduğu workflow id'si")

    # ---- Edge Content ---- #
    source_node_id = Column(String(20), ForeignKey("nodes.id", ondelete="CASCADE"), nullable=False, index=True,
    comment="Edge'in kaynak node id'si")
    target_node_id = Column(String(20), ForeignKey("nodes.id", ondelete="CASCADE"), nullable=False, index=True,
    comment="Edge'in hedef node id'si")

    # ---- Relations ---- #
    workflow = relationship("Workflow", back_populates="edges")
    source_node = relationship("Node", foreign_keys=[source_node_id], back_populates="edges_as_source")
    target_node = relationship("Node", foreign_keys=[target_node_id], back_populates="edges_as_target")