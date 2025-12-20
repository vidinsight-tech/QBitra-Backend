"""
File Repository - Dosya işlemleri için repository.

Kullanım:
    >>> from miniflow.repository import FileRepository
    >>> file_repo = FileRepository()
    >>> file = file_repo.get_by_name(session, "WSP-123", "my_file.pdf")
"""

from __future__ import annotations

from typing import Optional, List

from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from miniflow.database.repository.advanced import AdvancedRepository
from miniflow.models import File
from miniflow.database.repository.base import handle_db_exceptions



class FileRepository(AdvancedRepository):
    """Dosya işlemleri için repository."""
    
    def __init__(self):
        super().__init__(File)
    
    # =========================================================================
    # LOOKUP METHODS
    # =========================================================================
    
    @handle_db_exceptions
    def get_by_name(
        self, 
        session: Session, 
        workspace_id: str, 
        name: str
    ) -> Optional[File]:
        """İsim ile dosya getirir."""
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
    ) -> List[File]:
        """Workspace'in tüm dosyalarını getirir."""
        return session.query(self.model).filter(
            self.model.workspace_id == workspace_id,
            self.model.is_deleted == False
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).all()
    
    @handle_db_exceptions
    def count_by_workspace_id(self, session: Session, workspace_id: str) -> int:
        """Dosya sayısını döndürür."""
        return session.query(func.count(self.model.id)).filter(
            self.model.workspace_id == workspace_id,
            self.model.is_deleted == False
        ).scalar()
    
    @handle_db_exceptions
    def get_total_size_by_workspace_id(self, session: Session, workspace_id: str) -> int:
        """Toplam dosya boyutunu döndürür (bytes)."""
        result = session.query(func.sum(self.model.file_size)).filter(
            self.model.workspace_id == workspace_id,
            self.model.is_deleted == False
        ).scalar()
        return result or 0
    
    @handle_db_exceptions
    def get_all_by_extension(
        self, 
        session: Session, 
        workspace_id: str, 
        extension: str, order_by: Optional[str] = "created_at", order_desc: bool = True
    ) -> List[File]:
        """Uzantıya göre dosyaları getirir (liste)."""
        return session.query(self.model).filter(
            self.model.workspace_id == workspace_id,
            self.model.file_extension == extension,
            self.model.is_deleted == False
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).all()

