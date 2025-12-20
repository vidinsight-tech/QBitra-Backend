"""
Database Repository - Veritabanı bağlantı işlemleri için repository.

Kullanım:
    >>> from miniflow.repository import DatabaseRepository
    >>> db_repo = DatabaseRepository()
    >>> database = db_repo.get_by_name(session, "WSP-123", "my_database")
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional, List
from datetime import datetime, timezone

from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from miniflow.database.repository.advanced import AdvancedRepository
from miniflow.database.repository.base import handle_db_exceptions

if TYPE_CHECKING:
    from miniflow.models import Database


class DatabaseRepository(AdvancedRepository):
    """Veritabanı bağlantı işlemleri için repository."""
    
    def __init__(self):
        from miniflow.models import Database
        super().__init__(Database)
    
    # =========================================================================
    # LOOKUP METHODS
    # =========================================================================
    
    @handle_db_exceptions
    def get_by_name(
        self, 
        session: Session, 
        workspace_id: str, 
        name: str
    ) -> Optional[Database]:
        """İsim ile veritabanı getirir."""
        return session.query(self.model).filter(
            self.model.workspace_id == workspace_id,
            self.model.name == name,
            self.model.is_deleted == False
        ).first()
    
    @handle_db_exceptions
    def get_all_by_workspace_id(
        self, 
        session: Session, 
        workspace_id: str, order_by: Optional[str] = "created_at", order_desc: bool = True
    ) -> List[Database]:
        """Workspace'in tüm veritabanlarını getirir."""
        return session.query(self.model).filter(
            self.model.workspace_id == workspace_id,
            self.model.is_deleted == False
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).all()
    
    @handle_db_exceptions
    def count_by_workspace_id(self, session: Session, workspace_id: str) -> int:
        """Veritabanı sayısını döndürür."""
        return session.query(func.count(self.model.id)).filter(
            self.model.workspace_id == workspace_id,
            self.model.is_deleted == False
        ).scalar()
    
    @handle_db_exceptions
    def get_all_by_type(
        self, 
        session: Session, 
        workspace_id: str, 
        db_type: str, order_by: Optional[str] = "created_at", order_desc: bool = True
    ) -> List[Database]:
        """Tipe göre veritabanlarını getirir (liste)."""
        return session.query(self.model).filter(
            self.model.workspace_id == workspace_id,
            self.model.database_type == db_type,
            self.model.is_deleted == False
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).all()
    
    # =========================================================================
    # STATUS METHODS
    # =========================================================================
    
    @handle_db_exceptions
    def update_test_status(
        self, 
        session: Session, 
        database_id: str, 
        is_tested: bool,
        test_result: Optional[str] = None
    ) -> Optional[Database]:
        """Test durumunu günceller."""
        database = self.get_by_id(session, database_id)
        if database:
            database.is_tested = is_tested
            database.last_test_at = datetime.now(timezone.utc)
            if test_result:
                database.last_test_result = test_result
            session.flush()
        return database
    
    @handle_db_exceptions
    def deactivate(self, session: Session, database_id: str) -> Optional[Database]:
        """Veritabanını deaktif eder."""
        database = self.get_by_id(session, database_id)
        if database:
            database.is_active = False
            session.flush()
        return database
    
    @handle_db_exceptions
    def activate(self, session: Session, database_id: str) -> Optional[Database]:
        """Veritabanını aktif eder."""
        database = self.get_by_id(session, database_id)
        if database:
            database.is_active = True
            session.flush()
        return database

