"""
SQLAlchemy ORM için Temel Model Sınıfı

Bu modül, tüm ORM modelleri için declarative base sınıfını sağlar.
SQLAlchemy 2.0+ (DeclarativeBase) ve eski versiyonlar (declarative_base)
için uyumluluk sağlar.
"""

try:
    from sqlalchemy.orm import DeclarativeBase
    
    class Base(DeclarativeBase):
        """Tüm ORM modelleri için temel sınıf.
        
        SQLAlchemy 2.0+ için DeclarativeBase kullanır.
        Tüm model sınıfları bu sınıftan türetilmelidir.
        
        Örnek:
            >>> from miniflow.database.models import Base
            >>> from sqlalchemy import Column, Integer, String
            >>> 
            >>> class User(Base):
            ...     __tablename__ = 'users'
            ...     id = Column(Integer, primary_key=True)
            ...     name = Column(String(100))
        """
        __allow_unmapped__ = True  # Mixin'lerde declared_attr için gerekli
        
        def __init_subclass__(cls, **kwargs):
            """Alt sınıflara otomatik olarak __allow_unmapped__ ekler."""
            super().__init_subclass__(**kwargs)
            cls.__allow_unmapped__ = True
except ImportError:
    # SQLAlchemy 1.x uyumluluğu için
    from sqlalchemy.orm import declarative_base
    Base = declarative_base()
    # SQLAlchemy 1.x'te __allow_unmapped__ gerekmez