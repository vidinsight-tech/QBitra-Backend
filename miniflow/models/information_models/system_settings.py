from sqlalchemy import Column, String, Text, JSON, ForeignKey, Boolean, DateTime, Index
from miniflow.database.models import Base
from miniflow.database.models.mixins import TimestampMixin


class SystemSetting(Base, TimestampMixin):
    __prefix__ = "SYS"
    __tablename__ = "system_settings"

    # ---- Table Args ---- #
    __table_args__ = (
        Index('idx_system_settings_category_key', 'category', 'key'),
    )

    # ---- Setting Information ---- #
    key = Column(String(255), nullable=False, unique=True, index=True,
    comment="Ayar anahtarı (unique)")
    value = Column(Text, nullable=True,
    comment="Ayar değeri (string, number, boolean, JSON string olarak)")
    value_type = Column(String(50), nullable=False, default="string",
    comment="Değer tipi (string, number, boolean, json)")
    
    # ---- Setting Metadata ---- #
    category = Column(String(100), nullable=True, index=True,
    comment="Ayar kategorisi (email, security, features vb.)")
    description = Column(Text, nullable=True,
    comment="Ayar açıklaması")
    is_encrypted = Column(Boolean, default=False, nullable=False,
    comment="Değer şifrelenmiş mi?")
    
    # ---- Change Tracking ---- #
    updated_by = Column(String(20), ForeignKey("users.id", ondelete="SET NULL"), nullable=True,
    comment="Ayarı son güncelleyen kullanıcının id'si")
    change_at = Column(DateTime(timezone=True), nullable=True,
    comment="Ayarı son güncelleme zamanı")