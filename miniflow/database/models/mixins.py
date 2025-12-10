"""
Ortak İşlevsellik için Model Mixin'leri

Bu modül, timestamp yönetimi, soft delete ve audit logging gibi
ortak model özellikleri için yeniden kullanılabilir mixin'ler sağlar.
"""

from datetime import datetime, timezone
from typing import Any
from sqlalchemy import Column, DateTime, Boolean, String
from sqlalchemy.orm import declared_attr


def _utc_now() -> datetime:
    """Mevcut UTC zamanını timezone-aware datetime olarak döndürür.
    
    Returns:
        timezone-aware datetime: UTC zamanı
    """
    return datetime.now(timezone.utc)


class TimestampMixin:
    """Otomatik timestamp yönetimi için mixin.
    
    Bu mixin, model sınıflarına `created_at` ve `updated_at` kolonlarını
    otomatik olarak ekler. `created_at` kayıt oluşturulduğunda,
    `updated_at` ise kayıt güncellendiğinde otomatik olarak ayarlanır.
    
    Örnek:
        >>> from miniflow.database.models import Base
        >>> from miniflow.database.models.mixins import TimestampMixin
        >>> from sqlalchemy import Column, Integer, String
        >>> 
        >>> class User(Base, TimestampMixin):
        ...     __tablename__ = 'users'
        ...     id = Column(Integer, primary_key=True)
        ...     name = Column(String(100))
        >>> # created_at ve updated_at otomatik olarak eklenir
    """
    __allow_unmapped__ = True  # SQLAlchemy 2.0 uyumluluğu için
    
    @declared_attr
    def created_at(cls):
        """Kayıt oluşturulma zamanı.
        
        Returns:
            Column: DateTime kolonu (timezone-aware, nullable=False)
        """
        return Column(
            DateTime(timezone=True),
            default=_utc_now,
            nullable=False,
            doc="Kayıt oluşturulma zamanı"
        )
    
    @declared_attr
    def updated_at(cls):
        """Kayıt son güncelleme zamanı.
        
        Returns:
            Column: DateTime kolonu (timezone-aware, nullable=False, onupdate=True)
        """
        return Column(
            DateTime(timezone=True),
            default=_utc_now,
            onupdate=_utc_now,
            nullable=False,
            doc="Kayıt son güncelleme zamanı"
        )


class SoftDeleteMixin:
    """Soft delete işlevselliği için mixin.
    
    Bu mixin, kayıtları fiziksel olarak silmek yerine işaretleyerek
    soft delete işlemi yapılmasını sağlar. `is_deleted` ve `deleted_at`
    kolonları otomatik olarak eklenir.
    
    Örnek:
        >>> from miniflow.database.models import Base
        >>> from miniflow.database.models.mixins import SoftDeleteMixin
        >>> 
        >>> class User(Base, SoftDeleteMixin):
        ...     __tablename__ = 'users'
        ...     id = Column(Integer, primary_key=True)
        >>> 
        >>> user = User()
        >>> user.soft_delete()  # Kayıt silindi olarak işaretlenir
        >>> user.restore()      # Kayıt geri yüklenir
    """
    __allow_unmapped__ = True  # SQLAlchemy 2.0 uyumluluğu için
    
    @declared_attr
    def is_deleted(cls):
        """Kayıt soft-delete edilmiş mi?
        
        Returns:
            Column: Boolean kolonu (default=False, nullable=False)
        """
        return Column(
            Boolean,
            default=False,
            nullable=False,
            doc="Kayıt soft-delete edilmiş mi?"
        )
    
    @declared_attr
    def deleted_at(cls):
        """Kayıt soft-delete edilme zamanı.
        
        Returns:
            Column: DateTime kolonu (timezone-aware, nullable=True)
        """
        return Column(
            DateTime(timezone=True),
            nullable=True,
            doc="Kayıt soft-delete edilme zamanı"
        )
    
    def soft_delete(self) -> None:
        """Kaydı soft-delete olarak işaretler.
        
        Kaydı fiziksel olarak silmez, sadece `is_deleted=True` ve
        `deleted_at` değerlerini ayarlar.
        """
        self.is_deleted = True
        self.deleted_at = datetime.now(timezone.utc)
    
    def restore(self) -> None:
        """Soft-delete edilmiş kaydı geri yükler.
        
        `is_deleted=False` ve `deleted_at=None` yapar.
        """
        self.is_deleted = False
        self.deleted_at = None


class AuditMixin:
    """Audit logging alanları için mixin.
    
    Bu mixin, kayıtların kim tarafından oluşturulduğunu ve
    güncellendiğini takip etmek için `created_by` ve `updated_by`
    kolonlarını ekler.
    
    Örnek:
        >>> from miniflow.database.models import Base
        >>> from miniflow.database.models.mixins import AuditMixin
        >>> 
        >>> class User(Base, AuditMixin):
        ...     __tablename__ = 'users'
        ...     id = Column(Integer, primary_key=True)
        >>> 
        >>> user = User()
        >>> user.created_by = "admin"
        >>> user.updated_by = "admin"
    """
    __allow_unmapped__ = True  # SQLAlchemy 2.0 uyumluluğu için
    
    @declared_attr
    def created_by(cls):
        """Kaydı oluşturan kullanıcı adı veya ID.
        
        Returns:
            Column: String kolonu (max 255 karakter, nullable=True)
        """
        return Column(
            String(255),
            nullable=True,
            doc="Kaydı oluşturan kullanıcı adı veya ID"
        )
    
    @declared_attr
    def updated_by(cls):
        """Kaydı son güncelleyen kullanıcı adı veya ID.
        
        Returns:
            Column: String kolonu (max 255 karakter, nullable=True)
        """
        return Column(
            String(255),
            nullable=True,
            doc="Kaydı son güncelleyen kullanıcı adı veya ID"
        )