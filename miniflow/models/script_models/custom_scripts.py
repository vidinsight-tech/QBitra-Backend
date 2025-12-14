from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Float, Text, ForeignKey, JSON, Enum, UniqueConstraint, Index
from sqlalchemy.orm import relationship

from miniflow.database.models import Base
from miniflow.database.models.mixins import SoftDeleteMixin, TimestampMixin
from miniflow.models.enums import ScriptApprovalStatus, ScriptTestStatus


class CustomScript(Base, SoftDeleteMixin, TimestampMixin):
    """Kullanıcı script'leri - workspace'lerde yüklenen onay workflow'u ile custom script'ler"""
    __prefix__ = "CSC"
    __tablename__ = 'custom_scripts'
    __allow_unmapped__ = True

    # Workspace ve sahiplik
    workspace_id = Column(String(20), ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=False, index=True,
    comment="Hangi workspace'de")
    uploaded_by = Column(String(20), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True,
    comment="Script'i yükleyen kullanıcı")
    
    # Temel bilgiler
    name = Column(String(100), nullable=False, index=True,
    comment="Script adı (workspace içinde benzersiz)")
    description = Column(Text, nullable=True,
    comment="Script açıklaması")
    content = Column(Text, nullable=False,
    comment="Script içeriği (zorunlu)")

    # Organizasyon - Gruplama için kategori ve alt kategori
    category = Column(String(50), nullable=True, index=True,
    comment="Kategori (opsiyonel)")
    subcategory = Column(String(50), nullable=True, index=True,
    comment="Alt kategori (opsiyonel)")
    
    # File helper uyumlu alanlar
    file_name = Column(String(255), nullable=True,
    comment="Dosya adı (file helper tarafından oluşturulan)")
    file_path = Column(String(512), nullable=True, unique=True, index=True,
    comment="Disk üzerindeki dosya yolu (file helper formatında)")
    file_extension = Column(String(20), nullable=True,
    comment="Dosya uzantısı (.py, .js, .sh)")
    file_size = Column(Integer, nullable=True,
    comment="Dosya boyutu (byte)")
    mime_type = Column(String(100), nullable=True,
    comment="Dosya MIME tipi (file helper tarafından tespit edilen)")
    
    # Ortam - Gerekli Python paketleri
    required_packages = Column(JSON, default=lambda: [], nullable=False,
    comment="Gerekli paketler (JSON array)")

    # Şema tanımları - Input/output doğrulama
    input_schema = Column(JSON, default=lambda: {}, nullable=False,
    comment="Input validation şeması (JSON)")
    output_schema = Column(JSON, default=lambda: {}, nullable=False,
    comment="Output validation şeması (JSON)")
    
    # Onay workflow'u (sadece mevcut durum - detaylar ScriptReviewHistory'de)
    approval_status = Column(Enum(ScriptApprovalStatus), default=ScriptApprovalStatus.PENDING, nullable=False, index=True,
    comment="Durum (PENDING, IN_REVIEW, APPROVED, REJECTED, CHANGES_REQUESTED, RESUBMITTED)")
    
    # Test ve kalite
    test_status = Column(Enum(ScriptTestStatus), default=ScriptTestStatus.UNTESTED, nullable=False, index=True,
    comment="Test durumu (UNTESTED, PASSED, FAILED, SKIPPED)")
    test_coverage = Column(Float, nullable=True,
    comment="Test coverage yüzdesi")
    test_results = Column(JSON, default=lambda: {}, nullable=False,
    comment="Test sonuçları (JSON)")
    is_dangerous = Column(Boolean, default=False, nullable=False,
    comment="Tehlikeli script işareti")
    
    # Üst veri
    tags = Column(JSON, default=lambda: [], nullable=True,
    comment="Etiketler (JSON array)")
    documentation_url = Column(String(500), nullable=True,
    comment="Dokümantasyon URL'i")
    
    # İlişkiler
    workspace = relationship("Workspace", back_populates="custom_scripts")
    uploader = relationship("User", foreign_keys=[uploaded_by], back_populates="uploaded_scripts")
    review_history = relationship("ScriptReviewHistory", back_populates="script", cascade="all, delete-orphan", order_by="desc(ScriptReviewHistory.created_at)")
    nodes = relationship("Node", foreign_keys="Node.custom_script_id", back_populates="custom_script")
    execution_inputs = relationship("ExecutionInput", back_populates="custom_script")
    execution_outputs = relationship("ExecutionOutput", back_populates="custom_script")
    
    # ---- Helper Methods ---- #
    @property
    def last_review(self):
        """Son review kaydını döndürür"""
        if self.review_history:
            return self.review_history[0] if self.review_history else None
        return None
    
    @property
    def review_count(self):
        """Toplam review sayısını döndürür"""
        return len(self.review_history) if self.review_history else 0
    
    @property
    def pending_review(self):
        """Bekleyen review kaydını döndürür"""
        if self.review_history:
            for review in self.review_history:
                if review.review_status == ScriptApprovalStatus.PENDING or review.review_status == ScriptApprovalStatus.IN_REVIEW:
                    return review
        return None
