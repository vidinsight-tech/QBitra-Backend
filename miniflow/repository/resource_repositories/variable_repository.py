"""
Variable Repository - Değişken işlemleri için repository.

Kullanım:
    >>> from miniflow.repository import VariableRepository
    >>> variable_repo = VariableRepository()
    >>> variable = variable_repo.get_by_key(session, "WSP-123", "my_variable")
"""

from __future__ import annotations

from typing import Optional, List

from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from miniflow.database.repository.advanced import AdvancedRepository
from miniflow.models import Variable
from miniflow.database.repository.base import handle_db_exceptions



class VariableRepository(AdvancedRepository):
    """Değişken işlemleri için repository."""
    
    def __init__(self):
        super().__init__(Variable)
    
    # =========================================================================
    # LOOKUP METHODS
    # =========================================================================
    
    @handle_db_exceptions
    def get_by_key(
        self, 
        session: Session, 
        workspace_id: str, 
        key: str
    ) -> Optional[Variable]:
        """Key ile değişken getirir."""
        return session.query(self.model).filter(
            self.model.workspace_id == workspace_id,
            self.model.key == key,
            self.model.is_deleted == False
        ).first()
    
    @handle_db_exceptions
    def get_all_by_workspace_id(
        self, 
        session: Session, 
        workspace_id: str, order_by: Optional[str] = "created_at", order_desc: bool = True
    ) -> List[Variable]:
        """Workspace'in tüm değişkenlerini getirir."""
        return session.query(self.model).filter(
            self.model.workspace_id == workspace_id,
            self.model.is_deleted == False
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).all()
    
    @handle_db_exceptions
    def count_by_workspace_id(self, session: Session, workspace_id: str) -> int:
        """Değişken sayısını döndürür."""
        return session.query(func.count(self.model.id)).filter(
            self.model.workspace_id == workspace_id,
            self.model.is_deleted == False
        ).scalar()
    
    @handle_db_exceptions
    def get_secrets_by_workspace_id(
        self, 
        session: Session, 
        workspace_id: str, order_by: Optional[str] = "created_at", order_desc: bool = True
    ) -> List[Variable]:
        """Gizli değişkenleri getirir."""
        return session.query(self.model).filter(
            self.model.workspace_id == workspace_id,
            self.model.is_secret == True,
            self.model.is_deleted == False
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).all()

