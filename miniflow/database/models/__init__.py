"""
Database Models Modülü

Bu modül, SQLAlchemy ORM modelleri için temel sınıflar, mixin'ler ve
serializasyon yardımcıları sağlar.

Modüller:
    - base: SQLAlchemy declarative base sınıfı
    - mixins: Timestamp, SoftDelete, Audit mixin'leri
    - serialization: Model-to-dict/JSON dönüşüm fonksiyonları

Örnek Kullanım:
    >>> from miniflow.database.models import Base
    >>> from miniflow.database.models.mixins import TimestampMixin, SoftDeleteMixin
    >>> from sqlalchemy import Column, Integer, String
    >>> 
    >>> class User(Base, TimestampMixin, SoftDeleteMixin):
    ...     __tablename__ = 'users'
    ...     id = Column(Integer, primary_key=True)
    ...     name = Column(String(100))
    ...     email = Column(String(255), unique=True)
"""

from miniflow.database.models.base import Base

from miniflow.database.models.mixins import (
    TimestampMixin,
    SoftDeleteMixin,
    AuditMixin,
)

from miniflow.database.models.serialization import (
    model_to_dict,
    models_to_list,
    model_to_json,
)

__all__ = [
    # Base
    "Base",
    # Mixins
    "TimestampMixin",
    "SoftDeleteMixin",
    "AuditMixin",
    # Serialization
    "model_to_dict",
    "models_to_list",
    "model_to_json",
]

