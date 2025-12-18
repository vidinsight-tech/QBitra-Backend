from sqlalchemy import Column, String, Integer, Boolean, Float, Text, JSON, Index
from sqlalchemy.orm import relationship

from miniflow.database.models import Base
from miniflow.database.models.mixins import TimestampMixin


class WorkspacePlan(Base, TimestampMixin):
    """Workspace planları - Plan limitleri ve özellik tanımları"""
    __prefix__ = "WPL"
    __tablename__ = 'workspace_plans'
    
    # ---- Table Args ---- #
    __table_args__ = (
        Index('idx_workspace_plans_display_order', 'display_order'),
        Index('idx_workspace_plans_created', 'created_at'),
    )

    # ---- Basic Information ---- #
    name = Column(String(50), nullable=False, unique=True, index=True,
    comment="Plan adı (freemium, starter, pro, business, enterprise)")
    display_name = Column(String(100), nullable=False,
    comment="Görünen ad (Freemium, Starter, Pro, Business, Enterprise)")
    description = Column(Text, nullable=True,
    comment="Plan açıklaması")
    is_popular = Column(Boolean, default=False, nullable=False,
    comment="Popüler plan mı? (UI'da vurgulama)")
    display_order = Column(Integer, default=0, nullable=False,
    comment="Sıralama")
    
    # ---- Workspace Limits ---- #
    max_members = Column(Integer, nullable=False,
    comment="Maksimum üye sayısı (-1 = sınırsız)")
    max_workflows = Column(Integer, nullable=False,
    comment="Maksimum workflow sayısı (-1 = sınırsız)")
    max_custom_scripts = Column(Integer, nullable=False,
    comment="Maksimum custom script sayısı (-1 = sınırsız)")
    
    # ---- Storage Limits ---- #
    storage_limit_mb = Column(Integer, nullable=False,
    comment="Depolama limiti MB (-1 = sınırsız)")
    max_file_size_mb = Column(Integer, nullable=False,
    comment="Maksimum dosya boyutu MB (-1 = sınırsız)")
    
    # ---- Execution Limits ---- #
    monthly_execution_limit = Column(Integer, nullable=False,
    comment="Aylık execution limiti (-1 = sınırsız)")
    max_concurrent_executions = Column(Integer, nullable=False,
    comment="Eşzamanlı execution limiti (-1 = sınırsız)")
    
    # ---- API Limits ---- #
    max_api_keys = Column(Integer, nullable=False,
    comment="Maksimum API key sayısı (-1 = sınırsız)")
    api_rate_limit_per_minute = Column(Integer, nullable=True,
    comment="Dakikalık API istek limiti")
    api_rate_limit_per_hour = Column(Integer, nullable=True,
    comment="Saatlik API istek limiti")
    api_rate_limit_per_day = Column(Integer, nullable=True,
    comment="Günlük API istek limiti")
    
    # ---- Pricing ---- #
    monthly_price_usd = Column(Float, default=0.0, nullable=False,
    comment="Aylık fiyat (USD)")
    yearly_price_usd = Column(Float, nullable=True,
    comment="Yıllık fiyat (USD)")
    price_per_extra_member_usd = Column(Float, default=0.0, nullable=False,
    comment="Ekstra üye başına fiyat (USD)")
    
    # ---- Features List ---- #
    features = Column(JSON, default=lambda: [], nullable=False,
    comment="Özellik listesi (UI için)")

    # ---- Relationships ---- #
    workspaces = relationship("Workspace", back_populates="plan")
