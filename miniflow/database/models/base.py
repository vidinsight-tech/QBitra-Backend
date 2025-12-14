"""
SQLAlchemy ORM için Temel Model Sınıfı

Bu modül, tüm ORM modelleri için declarative base sınıfını sağlar.
SQLAlchemy 2.0+ (DeclarativeBase) için uyumluluk sağlar.
"""

import uuid
from sqlalchemy import Column, String
from sqlalchemy.orm import DeclarativeBase, declared_attr


class Base(DeclarativeBase):
    """Tüm ORM modelleri için temel sınıf.
    
    SQLAlchemy 2.0+ için DeclarativeBase kullanır.
    Tüm model sınıfları bu sınıftan türetilmelidir.
    
    ID Format: PREFIX-UUID16 (örn: USR-A1B2C3D4E5F6G7H8)
    
    Örnek:
        >>> from miniflow.database.models import Base
        >>> from sqlalchemy import Column, String
        >>> 
        >>> class User(Base):
        ...     __tablename__ = 'users'
        ...     __prefix__ = 'USR'
        ...     name = Column(String(100))
    """
    __allow_unmapped__ = True  
    __abstract__ = True
    __prefix__ = 'GEN'
    
    @declared_attr
    def id(cls):
        """Primary key - PREFIX-UUID16 formatında benzersiz ID.
        
        Returns:
            Column: String(20) primary key kolonu
        """
        return Column(
            String(20),
            primary_key=True,
            default=cls._generate_id,
            nullable=False,
            doc="Benzersiz ID (PREFIX-UUID16 formatında)"
        )
        
    def __init_subclass__(cls, **kwargs):
        """Alt sınıflara otomatik olarak __allow_unmapped__ ekler."""
        super().__init_subclass__(**kwargs)
        cls.__allow_unmapped__ = True

    @classmethod
    def _generate_id(cls):
        """Benzersiz ID üretir (PREFIX-UUID formatında)."""
        prefix = getattr(cls, '__prefix__', 'GEN')
        if len(prefix) != 3:
            raise ValueError(f"Model prefix must be exactly 3 characters. Got: {prefix}")
        
        uuid_suffix = str(uuid.uuid4()).replace('-', '')[:16].upper()
        return f"{prefix}-{uuid_suffix}"