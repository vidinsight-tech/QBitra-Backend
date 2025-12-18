from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Float, Text, ForeignKey, JSON, Enum, Index
from sqlalchemy.orm import relationship

from miniflow.database.models import Base
from miniflow.database.models.mixins import SoftDeleteMixin, TimestampMixin


class Script(Base, SoftDeleteMixin, TimestampMixin):
    """Global script kütüphanesi - versiyonlama, test ve performans takibi ile çalıştırılabilir script'ler"""
    __prefix__ = "SCR"
    __tablename__ = 'scripts'
    
    # ---- Table Args ---- #
    __table_args__ = (
        Index('idx_scripts_category_subcategory', 'category', 'subcategory'),
        Index('idx_scripts_softdelete', 'is_deleted', 'created_at'),
    )

    # Temel bilgiler
    name = Column(String(100), nullable=False, unique=True, index=True,
        comment="Script adı (global olarak benzersiz)")
    description = Column(Text, nullable=True,
        comment="Script açıklaması")
    content = Column(Text, nullable=False,
        comment="Script içeriği")

    # Organizasyon - Gruplama için kategori ve alt kategori
    category = Column(String(50), nullable=False, index=True,
        comment="Kategori (zorunlu)")
    subcategory = Column(String(50), nullable=True, index=True,
        comment="Alt kategori (opsiyonel)")

    # Dosya bilgileri - Script depolama ve üst veri (file helper uyumlu)
    file_name = Column(String(255), nullable=True,
        comment="Dosya adı (file helper tarafından oluşturulan)")
    file_path = Column(String(512), nullable=True, unique=True, index=True,
        comment="Dosya yolu (file helper formatında)")
    file_extension = Column(String(20), nullable=True,
        comment="Dosya uzantısı (.py, .js, .sh)")
    file_size = Column(Integer, nullable=True,
        comment="Dosya boyutu (byte)")
    mime_type = Column(String(100), nullable=True,
        comment="Dosya MIME tipi (file helper tarafından tespit edilen)")
    script_metadata = Column(JSON, nullable=True,
        comment="Meta veriler (JSON)")

    # Ortam - Gerekli Python paketleri
    required_packages = Column(JSON, default=lambda: [], nullable=False,
        comment="Gerekli paketler (JSON array)")

    # Şema tanımları - Input/output doğrulama
    input_schema = Column(JSON, default=lambda: {}, nullable=False,
        comment="Input validation şeması (JSON)")
    output_schema = Column(JSON, default=lambda: {}, nullable=False,
        comment="Output validation şeması (JSON)")

    # Üst veri ve dokümantasyon
    tags = Column(JSON, default=lambda: [], nullable=True,
        comment="Etiketler (JSON array)")
    documentation_url = Column(String(500), nullable=True,
        comment="Dokümantasyon URL'i")

    # İlişkiler
    nodes_as_global = relationship("Node", foreign_keys="Node.global_script_id", back_populates="global_script")
    execution_inputs = relationship("ExecutionInput", foreign_keys="ExecutionInput.global_script_id", back_populates="global_script")
    execution_outputs = relationship("ExecutionOutput", foreign_keys="ExecutionOutput.global_script_id", back_populates="global_script")
