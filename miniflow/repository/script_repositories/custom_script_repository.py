"""
CustomScript Repository - Custom script işlemleri için repository.

Kullanım:
    >>> from miniflow.repository import CustomScriptRepository
    >>> script_repo = CustomScriptRepository()
    >>> script = script_repo.get_by_name(session, "WSP-123", "my_script")
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional, List

from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from miniflow.database.repository.advanced import AdvancedRepository
from miniflow.database.repository.base import handle_db_exceptions

from miniflow.models.enums import ScriptApprovalStatus, ScriptTestStatus


class CustomScriptRepository(AdvancedRepository):
    """Custom script işlemleri için repository."""
    
    def __init__(self):
        from miniflow.models import CustomScript
        super().__init__(CustomScript)
    
    # =========================================================================
    # LOOKUP METHODS
    # =========================================================================
    
    @handle_db_exceptions
    def get_by_name(
        self, 
        session: Session, 
        workspace_id: str, 
        name: str
    ) -> Optional[CustomScript]:
        """İsim ile custom script getirir."""
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
    ) -> List[CustomScript]:
        """Workspace'in custom script'lerini getirir."""
        return session.query(self.model).filter(
            self.model.workspace_id == workspace_id,
            self.model.is_deleted == False
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).all()
    
    @handle_db_exceptions
    def count_by_workspace_id(self, session: Session, workspace_id: str) -> int:
        """Custom script sayısını döndürür."""
        return session.query(func.count(self.model.id)).filter(
            self.model.workspace_id == workspace_id,
            self.model.is_deleted == False
        ).scalar()
    
    @handle_db_exceptions
    def get_all_by_approval_status(
        self, 
        session: Session, 
        workspace_id: str, 
        status: ScriptApprovalStatus, order_by: Optional[str] = "created_at", order_desc: bool = True
    ) -> List[CustomScript]:
        """Onay durumuna göre getirir (liste)."""
        return session.query(self.model).filter(
            self.model.workspace_id == workspace_id,
            self.model.approval_status == status,
            self.model.is_deleted == False
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).all()
    
    @handle_db_exceptions
    def get_all_by_category(
        self, 
        session: Session, 
        workspace_id: str, 
        category: str, order_by: Optional[str] = "created_at", order_desc: bool = True
    ) -> List[CustomScript]:
        """Kategoriye göre getirir (liste)."""
        return session.query(self.model).filter(
            self.model.workspace_id == workspace_id,
            self.model.category == category,
            self.model.is_deleted == False
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).all()
    
    # =========================================================================
    # STATUS METHODS
    # =========================================================================
    
    @handle_db_exceptions
    def update_approval_status(
        self, 
        session: Session, 
        script_id: str, 
        status: ScriptApprovalStatus
    ) -> Optional[CustomScript]:
        """Onay durumunu günceller."""
        script = self.get_by_id(session, script_id)
        if script:
            script.approval_status = status
            session.flush()
        return script
    
    @handle_db_exceptions
    def update_test_status(
        self, 
        session: Session, 
        script_id: str, 
        status: ScriptTestStatus,
        test_results: Optional[dict] = None,
        coverage: Optional[float] = None
    ) -> Optional[CustomScript]:
        """Test durumunu günceller."""
        script = self.get_by_id(session, script_id)
        if script:
            script.test_status = status
            if test_results:
                script.test_results = test_results
            if coverage is not None:
                script.test_coverage = coverage
            session.flush()
        return script
    
    @handle_db_exceptions
    def mark_as_dangerous(
        self, 
        session: Session, 
        script_id: str,
        is_dangerous: bool = True
    ) -> Optional[CustomScript]:
        """Script'i tehlikeli olarak işaretler."""
        script = self.get_by_id(session, script_id)
        if script:
            script.is_dangerous = is_dangerous
            session.flush()
        return script

