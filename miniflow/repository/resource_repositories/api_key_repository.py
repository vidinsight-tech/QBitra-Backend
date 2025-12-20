"""
ApiKey Repository - API key işlemleri için repository.

Kullanım:
    >>> from miniflow.repository import ApiKeyRepository
    >>> api_key_repo = ApiKeyRepository()
    >>> api_key = api_key_repo.get_by_name(session, "WSP-123", "my_api_key")
"""

from __future__ import annotations

from typing import Optional, List
from datetime import datetime, timezone

from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from miniflow.database.repository.advanced import AdvancedRepository
from miniflow.models import ApiKey
from miniflow.database.repository.base import handle_db_exceptions



class ApiKeyRepository(AdvancedRepository):
    """API key işlemleri için repository."""
    
    def __init__(self):
        super().__init__(ApiKey)
    
    # =========================================================================
    # LOOKUP METHODS
    # =========================================================================
    
    @handle_db_exceptions
    def get_by_name(
        self, 
        session: Session, 
        workspace_id: str, 
        name: str
    ) -> Optional[ApiKey]:
        """İsim ile API key getirir."""
        return session.query(self.model).filter(
            self.model.workspace_id == workspace_id,
            self.model.name == name,
            self.model.is_deleted == False
        ).first()
    
    @handle_db_exceptions
    def get_by_key_hash(
        self, 
        session: Session, 
        key_hash: str
    ) -> Optional[ApiKey]:
        """Key hash ile API key getirir."""
        return session.query(self.model).filter(
            self.model.key_hash == key_hash,
            self.model.is_deleted == False
        ).first()
    
    @handle_db_exceptions
    def get_by_api_key(
        self, 
        session: Session, 
        api_key: str
    ) -> Optional[ApiKey]:
        """Tam API key string ile getirir (hash karşılaştırma gerekir)."""
        # Note: Bu metod hash karşılaştırması yapmak için service layer'da implement edilmeli
        # Burada sadece key_hash ile arama yapılır
        import hashlib
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        return self.get_by_key_hash(session, key_hash)
    
    @handle_db_exceptions
    def get_all_by_workspace_id(
        self, 
        session: Session, 
        workspace_id: str, order_by: Optional[str] = "created_at", order_desc: bool = True
    ) -> List[ApiKey]:
        """Workspace'in tüm API key'lerini getirir."""
        return session.query(self.model).filter(
            self.model.workspace_id == workspace_id,
            self.model.is_deleted == False
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).all()
    
    @handle_db_exceptions
    def count_by_workspace_id(self, session: Session, workspace_id: str) -> int:
        """API key sayısını döndürür."""
        return session.query(func.count(self.model.id)).filter(
            self.model.workspace_id == workspace_id,
            self.model.is_deleted == False
        ).scalar()
    
    # =========================================================================
    # STATUS METHODS
    # =========================================================================
    
    @handle_db_exceptions
    def update_last_used(
        self, 
        session: Session, 
        api_key_id: str
    ) -> Optional[ApiKey]:
        """Son kullanım zamanını ve sayacı günceller."""
        api_key = self.get_by_id(session, api_key_id)
        if api_key:
            api_key.last_used_at = datetime.now(timezone.utc)
            api_key.usage_count = (api_key.usage_count or 0) + 1
            session.flush()
        return api_key
    
    @handle_db_exceptions
    def deactivate(self, session: Session, api_key_id: str) -> Optional[ApiKey]:
        """API key'i deaktif eder."""
        api_key = self.get_by_id(session, api_key_id)
        if api_key:
            api_key.is_active = False
            session.flush()
        return api_key
    
    @handle_db_exceptions
    def activate(self, session: Session, api_key_id: str) -> Optional[ApiKey]:
        """API key'i aktif eder."""
        api_key = self.get_by_id(session, api_key_id)
        if api_key:
            api_key.is_active = True
            session.flush()
        return api_key

