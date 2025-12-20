"""
ExecutionInput Repository - Execution input işlemleri için repository.

Kullanım:
    >>> from miniflow.repository import ExecutionInputRepository
    >>> input_repo = ExecutionInputRepository()
    >>> inputs = input_repo.get_all_by_execution_id(session, "EXE-123")
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional, List

from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from miniflow.database.repository.bulk import BulkRepository
from miniflow.database.repository.base import handle_db_exceptions

if TYPE_CHECKING:
    from miniflow.models import ExecutionInput


class ExecutionInputRepository(BulkRepository):
    """Execution input işlemleri için repository."""
    
    def __init__(self):
        from miniflow.models import ExecutionInput
        super().__init__(ExecutionInput)
    
    # =========================================================================
    # LOOKUP METHODS
    # =========================================================================
    
    @handle_db_exceptions
    def get_all_by_execution_id(
        self, 
        session: Session, 
        execution_id: str, order_by: Optional[str] = "created_at", order_desc: bool = True
    ) -> List[ExecutionInput]:
        """Execution'ın input'larını getirir (liste)."""
        return session.query(self.model).filter(
            self.model.execution_id == execution_id
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).all()
    
    @handle_db_exceptions
    def get_by_execution_and_node(
        self, 
        session: Session, 
        execution_id: str, 
        node_id: str
    ) -> Optional[ExecutionInput]:
        """Execution ve node ile input getirir."""
        return session.query(self.model).filter(
            self.model.execution_id == execution_id,
            self.model.node_id == node_id
        ).first()
    
    @handle_db_exceptions
    def get_all_by_execution_and_node_ids(
        self, 
        session: Session, 
        execution_id: str, 
        node_ids: List[str], order_by: Optional[str] = "created_at", order_desc: bool = True
    ) -> List[ExecutionInput]:
        """Toplu node ID'leri ile input'ları getirir (liste)."""
        return session.query(self.model).filter(
            self.model.execution_id == execution_id,
            self.model.node_id.in_(node_ids)
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).all()
    
    @handle_db_exceptions
    def get_ready_execution_inputs(
        self, 
        session: Session, 
        execution_id: str
    ) -> List[ExecutionInput]:
        """Çalıştırılmaya hazır input'ları getirir (dependency_count=0)."""
        return session.query(self.model).filter(
            self.model.execution_id == execution_id,
            self.model.dependency_count == 0
        ).all()
    
    # =========================================================================
    # UPDATE METHODS
    # =========================================================================
    
    @handle_db_exceptions
    def increment_waiting_for_by_ids(
        self, 
        session: Session, 
        input_ids: List[str],
        increment: int = 1
    ) -> int:
        """waiting_for değerini toplu artırır."""
        result = session.query(self.model).filter(
            self.model.id.in_(input_ids)
        ).update({
            self.model.waiting_for: self.model.waiting_for + increment
        }, synchronize_session=False)
        session.flush()
        return result
    
    @handle_db_exceptions
    def decrement_dependency_count_by_node_ids(
        self, 
        session: Session, 
        execution_id: str,
        node_ids: List[str],
        decrement: int = 1
    ) -> int:
        """Dependency count'u toplu azaltır."""
        result = session.query(self.model).filter(
            self.model.execution_id == execution_id,
            self.model.node_id.in_(node_ids)
        ).update({
            self.model.dependency_count: self.model.dependency_count - decrement
        }, synchronize_session=False)
        session.flush()
        return result
    
    # =========================================================================
    # DELETE METHODS
    # =========================================================================
    
    @handle_db_exceptions
    def delete_by_execution_id(self, session: Session, execution_id: str) -> int:
        """Execution'ın tüm input'larını siler (hard delete)."""
        result = session.query(self.model).filter(
            self.model.execution_id == execution_id
        ).delete(synchronize_session=False)
        session.flush()
        return result
    
    @handle_db_exceptions
    def delete_by_ids(self, session: Session, input_ids: List[str]) -> int:
        """Belirli ID'lerdeki input'ları siler (hard delete)."""
        result = session.query(self.model).filter(
            self.model.id.in_(input_ids)
        ).delete(synchronize_session=False)
        session.flush()
        return result

