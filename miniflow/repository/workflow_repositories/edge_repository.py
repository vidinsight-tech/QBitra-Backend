"""
Edge Repository - Edge işlemleri için repository.

Kullanım:
    >>> from miniflow.repository import EdgeRepository
    >>> edge_repo = EdgeRepository()
    >>> edges = edge_repo.get_all_by_workflow_id(session, "WF-123")
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional, List
from datetime import datetime, timezone

from sqlalchemy import func, or_, desc
from sqlalchemy.orm import Session

from miniflow.database.repository.advanced import AdvancedRepository
from miniflow.database.repository.base import handle_db_exceptions

if TYPE_CHECKING:
    from miniflow.models import Edge


class EdgeRepository(AdvancedRepository):
    """Edge işlemleri için repository."""
    
    def __init__(self):
        from miniflow.models import Edge
        super().__init__(Edge)
    
    # =========================================================================
    # LOOKUP METHODS
    # =========================================================================
    
    @handle_db_exceptions
    def get_by_from_and_to_node(
        self, 
        session: Session, 
        source_node_id: str, 
        target_node_id: str
    ) -> Optional[Edge]:
        """Başlangıç ve bitiş node'larıyla edge getirir (tek kayıt)."""
        return session.query(self.model).filter(
            self.model.source_node_id == source_node_id,
            self.model.target_node_id == target_node_id,
            self.model.is_deleted == False
        ).first()
    
    @handle_db_exceptions
    def get_all_by_source_node_id(
        self, 
        session: Session, 
        source_node_id: str, order_by: Optional[str] = "created_at", order_desc: bool = True
    ) -> List[Edge]:
        """Kaynak node'a göre edge'leri getirir (liste)."""
        return session.query(self.model).filter(
            self.model.source_node_id == source_node_id,
            self.model.is_deleted == False
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).all()
    
    @handle_db_exceptions
    def get_all_by_target_node_id(
        self, 
        session: Session, 
        target_node_id: str, order_by: Optional[str] = "created_at", order_desc: bool = True
    ) -> List[Edge]:
        """Hedef node'a göre edge'leri getirir (liste)."""
        return session.query(self.model).filter(
            self.model.target_node_id == target_node_id,
            self.model.is_deleted == False
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).all()
    
    @handle_db_exceptions
    def get_all_by_workflow_id(
        self, 
        session: Session, 
        workflow_id: str, order_by: Optional[str] = "created_at", order_desc: bool = True
    ) -> List[Edge]:
        """Workflow'un tüm edge'lerini getirir."""
        return session.query(self.model).filter(
            self.model.workflow_id == workflow_id,
            self.model.is_deleted == False
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).all()
    
    @handle_db_exceptions
    def count_by_workflow_id(self, session: Session, workflow_id: str) -> int:
        """Edge sayısını döndürür."""
        return session.query(func.count(self.model.id)).filter(
            self.model.workflow_id == workflow_id,
            self.model.is_deleted == False
        ).scalar()
    
    @handle_db_exceptions
    def get_all_by_from_node_id(
        self, 
        session: Session, 
        source_node_id: str, order_by: Optional[str] = "created_at", order_desc: bool = True
    ) -> List[Edge]:
        """Çıkış node'una göre edge'leri getirir (liste)."""
        return self.get_all_by_source_node_id(session, source_node_id, order_by, order_desc)
    
    @handle_db_exceptions
    def get_all_by_to_node_id(
        self, 
        session: Session, 
        target_node_id: str, order_by: Optional[str] = "created_at", order_desc: bool = True
    ) -> List[Edge]:
        """Hedef node'una göre edge'leri getirir (liste)."""
        return self.get_all_by_target_node_id(session, target_node_id, order_by, order_desc)
    
    @handle_db_exceptions
    def get_outgoing_edges(
        self, 
        session: Session, 
        node_id: str
    ) -> List[Edge]:
        """Node'dan çıkan edge'leri getirir."""
        return self.get_all_by_source_node_id(session, node_id)
    
    # =========================================================================
    # DELETE METHODS
    # =========================================================================
    
    @handle_db_exceptions
    def delete_all_by_workflow_id(self, session: Session, workflow_id: str) -> int:
        """Workflow'un tüm edge'lerini siler (soft delete)."""
        now = datetime.now(timezone.utc)
        result = session.query(self.model).filter(
            self.model.workflow_id == workflow_id,
            self.model.is_deleted == False
        ).update({
            self.model.is_deleted: True,
            self.model.deleted_at: now
        }, synchronize_session=False)
        session.flush()
        return result
    
    @handle_db_exceptions
    def delete_edges_by_node_id(self, session: Session, node_id: str) -> int:
        """Node'a bağlı tüm edge'leri siler (soft delete)."""
        now = datetime.now(timezone.utc)
        result = session.query(self.model).filter(
            or_(
                self.model.source_node_id == node_id,
                self.model.target_node_id == node_id
            ),
            self.model.is_deleted == False
        ).update({
            self.model.is_deleted: True,
            self.model.deleted_at: now
        }, synchronize_session=False)
        session.flush()
        return result

