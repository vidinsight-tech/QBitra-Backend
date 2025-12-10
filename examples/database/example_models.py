import sys
from pathlib import Path

# Proje root'unu path'e ekle
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship

from miniflow.database.models import Base
from miniflow.database.models.mixins import TimestampMixin, SoftDeleteMixin, AuditMixin


class User(Base, TimestampMixin, SoftDeleteMixin, AuditMixin):
    """Kullanıcı modeli - Tüm mixin'lerle."""
    __tablename__ = 'users'
    __allow_unmapped__ = True
    
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    full_name = Column(String(200), nullable=True)
    
    # Relationship
    posts = relationship('Post', back_populates='author', cascade='all, delete-orphan')
    comments = relationship('Comment', back_populates='author', cascade='all, delete-orphan')


class Post(Base, TimestampMixin, SoftDeleteMixin, AuditMixin):
    """Blog yazısı modeli - Tüm mixin'lerle."""
    __tablename__ = 'posts'
    __allow_unmapped__ = True
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Relationship
    author = relationship('User', back_populates='posts')
    comments = relationship('Comment', back_populates='post', cascade='all, delete-orphan')


class Comment(Base, TimestampMixin, SoftDeleteMixin):
    """Yorum modeli - Timestamp ve SoftDelete mixin'leriyle."""
    __tablename__ = 'comments'
    __allow_unmapped__ = True
    
    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    post_id = Column(Integer, ForeignKey('posts.id'), nullable=False)
    
    # Relationship
    author = relationship('User', back_populates='comments')
    post = relationship('Post', back_populates='comments')