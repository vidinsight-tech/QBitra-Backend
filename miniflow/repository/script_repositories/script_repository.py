"""
Script Repository - Global script işlemleri için repository.

Kullanım:
    >>> from miniflow.repository import ScriptRepository
    >>> script_repo = ScriptRepository()
    >>> script = script_repo.get_by_name(session, "http_request")
"""

from __future__ import annotations

from typing import Optional, List

from sqlalchemy import func, distinct, desc
from sqlalchemy.orm import Session

from miniflow.database.repository.advanced import AdvancedRepository
from miniflow.models import Script
from miniflow.database.repository.base import handle_db_exceptions



class ScriptRepository(AdvancedRepository):
    """Global script işlemleri için repository."""
    
    def __init__(self):
        super().__init__(Script)
    
    # =========================================================================
    # LOOKUP METHODS
    # =========================================================================
    
    @handle_db_exceptions
    def get_by_name(self, session: Session, name: str) -> Optional[Script]:
        """İsim ile script getirir."""
        return session.query(self.model).filter(
            self.model.name == name,
            self.model.is_deleted == False
        ).first()
    
    @handle_db_exceptions
    def get_all(self, session: Session) -> List[Script]:
        """Tüm script'leri getirir."""
        return session.query(self.model).filter(
            self.model.is_deleted == False
        ).all()
    
    @handle_db_exceptions
    def get_all_by_category(
        self, 
        session: Session, 
        category: str, order_by: Optional[str] = "created_at", order_desc: bool = True
    ) -> List[Script]:
        """Kategoriye göre script'leri getirir (liste)."""
        return session.query(self.model).filter(
            self.model.category == category,
            self.model.is_deleted == False
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).all()
    
    @handle_db_exceptions
    def get_all_by_category_and_subcategory(
        self, 
        session: Session, 
        category: str, 
        subcategory: str, order_by: Optional[str] = "created_at", order_desc: bool = True
    ) -> List[Script]:
        """Kategori ve alt kategoriye göre getirir (liste)."""
        return session.query(self.model).filter(
            self.model.category == category,
            self.model.subcategory == subcategory,
            self.model.is_deleted == False
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).all()
    
    @handle_db_exceptions
    def count_all(self, session: Session) -> int:
        """Toplam script sayısını döndürür."""
        return session.query(func.count(self.model.id)).filter(
            self.model.is_deleted == False
        ).scalar()
    
    @handle_db_exceptions
    def get_categories(self, session: Session) -> List[str]:
        """Tüm kategorileri listeler."""
        result = session.query(distinct(self.model.category)).filter(
            self.model.is_deleted == False,
            self.model.category.isnot(None)
        ).all()
        return [row[0] for row in result]

