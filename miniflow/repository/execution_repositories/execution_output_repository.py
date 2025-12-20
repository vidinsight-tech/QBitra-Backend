"""
ExecutionOutput Repository - Execution output işlemleri için repository.

Kullanım:
    >>> from miniflow.repository import ExecutionOutputRepository
    >>> output_repo = ExecutionOutputRepository()
    >>> outputs = output_repo.get_all_by_execution_id(session, "EXE-123")
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional, List

from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from miniflow.database.repository.bulk import BulkRepository
from miniflow.database.repository.base import handle_db_exceptions

if TYPE_CHECKING:
    from miniflow.models import ExecutionOutput


class ExecutionOutputRepository(BulkRepository):
    """Execution output işlemleri için repository."""
    
    def __init__(self):
        from miniflow.models import ExecutionOutput
        super().__init__(ExecutionOutput)
    
    # =========================================================================
    # LOOKUP METHODS
    # =========================================================================
    
    @handle_db_exceptions
    def get_all_by_execution_id(
        self, 
        session: Session, 
        execution_id: str, order_by: Optional[str] = "created_at", order_desc: bool = True
    ) -> List[ExecutionOutput]:
        """Execution'ın output'larını getirir (liste)."""
        return session.query(self.model).filter(
            self.model.execution_id == execution_id
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).all()
    
    @handle_db_exceptions
    def get_by_execution_and_node(
        self, 
        session: Session, 
        execution_id: str, 
        node_id: str
    ) -> Optional[ExecutionOutput]:
        """Execution ve node ile output getirir."""
        return session.query(self.model).filter(
            self.model.execution_id == execution_id,
            self.model.node_id == node_id
        ).first()
    
    @handle_db_exceptions
    def count_by_execution_id(self, session: Session, execution_id: str) -> int:
        """Output sayısını döndürür."""
        return session.query(func.count(self.model.id)).filter(
            self.model.execution_id == execution_id
        ).scalar()
    
    @handle_db_exceptions
    def count_by_status(
        self, 
        session: Session, 
        execution_id: str, 
        status: str
    ) -> int:
        """Duruma göre output sayısını döndürür."""
        return session.query(func.count(self.model.id)).filter(
            self.model.execution_id == execution_id,
            self.model.status == status
        ).scalar()
    
    @handle_db_exceptions
    def get_all_by_status(
        self, 
        session: Session, 
        execution_id: str, 
        status: str, order_by: Optional[str] = "created_at", order_desc: bool = True
    ) -> List[ExecutionOutput]:
        """Duruma göre output'ları getirir (liste)."""
        return session.query(self.model).filter(
            self.model.execution_id == execution_id,
            self.model.status == status
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).all()
    
    # =========================================================================
    # UPDATE METHODS
    # =========================================================================
    
    @handle_db_exceptions
    def update_status(
        self, 
        session: Session, 
        output_id: str, 
        status: str
    ) -> Optional[ExecutionOutput]:
        """Output durumunu günceller."""
        output = self.get_by_id(session, output_id)
        if output:
            output.status = status
            session.flush()
        return output
    
    # =========================================================================
    # DELETE METHODS
    # =========================================================================
    
    @handle_db_exceptions
    def delete_by_execution_id(self, session: Session, execution_id: str) -> int:
        """Execution'ın tüm output'larını siler (hard delete)."""
        result = session.query(self.model).filter(
            self.model.execution_id == execution_id
        ).delete(synchronize_session=False)
        session.flush()
        return result

