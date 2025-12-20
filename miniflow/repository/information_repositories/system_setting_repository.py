"""
SystemSetting Repository - Sistem ayarları için repository.

Kullanım:
    >>> from miniflow.repository import SystemSettingRepository
    >>> setting_repo = SystemSettingRepository()
    >>> setting = setting_repo.get_by_key(session, "email.smtp_host")
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional, List
from datetime import datetime, timezone

from sqlalchemy import desc
from sqlalchemy.orm import Session

from miniflow.database.repository.base import BaseRepository, handle_db_exceptions


class SystemSettingRepository(BaseRepository):
    """Sistem ayarları için repository."""
    
    def __init__(self):
        from miniflow.models import SystemSetting
        super().__init__(SystemSetting)
    
    # =========================================================================
    # LOOKUP METHODS
    # =========================================================================
    
    @handle_db_exceptions
    def get_by_key(
        self, 
        session: Session, 
        key: str
    ) -> Optional[SystemSetting]:
        """Anahtar ile ayar getirir."""
        return session.query(self.model).filter(
            self.model.key == key
        ).first()
    
    @handle_db_exceptions
    def get_all_by_category(
        self, 
        session: Session, 
        category: str, order_by: Optional[str] = "created_at", order_desc: bool = True
    ) -> List[SystemSetting]:
        """Kategoriye göre ayarları getirir (liste)."""
        return session.query(self.model).filter(
            self.model.category == category
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).all()
    
    @handle_db_exceptions
    def get_value(
        self, 
        session: Session, 
        key: str,
        default: Optional[str] = None
    ) -> Optional[str]:
        """Ayar değerini döndürür."""
        setting = self.get_by_key(session, key)
        return setting.value if setting else default
    
    @handle_db_exceptions
    def get_all_categories(self, session: Session) -> List[str]:
        """Tüm kategorileri listeler."""
        from sqlalchemy import distinct
        result = session.query(distinct(self.model.category)).filter(
            self.model.category.isnot(None)
        ).all()
        return [row[0] for row in result]
    
    # =========================================================================
    # UPDATE METHODS
    # =========================================================================
    
    @handle_db_exceptions
    def set_value(
        self, 
        session: Session, 
        key: str,
        value: str,
        updated_by: Optional[str] = None
    ) -> Optional[SystemSetting]:
        """Ayar değerini günceller."""
        setting = self.get_by_key(session, key)
        if setting:
            setting.value = value
            setting.updated_by = updated_by
            setting.change_at = datetime.now(timezone.utc)
            session.flush()
        return setting
    
    @handle_db_exceptions
    def upsert_setting(
        self, 
        session: Session, 
        key: str,
        value: str,
        value_type: str = "string",
        category: Optional[str] = None,
        description: Optional[str] = None,
        updated_by: Optional[str] = None
    ) -> SystemSetting:
        """Ayar oluşturur veya günceller."""
        setting = self.get_by_key(session, key)
        now = datetime.now(timezone.utc)
        
        if setting:
            setting.value = value
            setting.updated_by = updated_by
            setting.change_at = now
            if category:
                setting.category = category
            if description:
                setting.description = description
        else:
            from miniflow.models import SystemSetting
            setting = SystemSetting(
                key=key,
                value=value,
                value_type=value_type,
                category=category,
                description=description,
                updated_by=updated_by,
                change_at=now
            )
            session.add(setting)
        
        session.flush()
        return setting
    
    # =========================================================================
    # DELETE METHODS
    # =========================================================================
    
    @handle_db_exceptions
    def delete_by_key(self, session: Session, key: str) -> bool:
        """Anahtara göre ayar siler."""
        result = session.query(self.model).filter(
            self.model.key == key
        ).delete(synchronize_session=False)
        session.flush()
        return result > 0
    
    @handle_db_exceptions
    def delete_all_by_category(self, session: Session, category: str) -> int:
        """Kategorideki tüm ayarları siler."""
        result = session.query(self.model).filter(
            self.model.category == category
        ).delete(synchronize_session=False)
        session.flush()
        return result

