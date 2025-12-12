from sqlalchemy import Column, String, Text, ForeignKey, Integer, DateTime, Boolean
from sqlalchemy.orm import relationship

from miniflow.database.models import Base
from miniflow.database.models.mixins import TimestampMixin


class AgreementVersion(Base, TimestampMixin):
    """Sözleşme versiyonları modeli - Her sözleşmenin versiyon geçmişi."""
    __prefix__ = "AGV"
    __tablename__ = "agreement_versions"
    __allow_unmapped__ = True

    # ---- Agreement Relationship ---- #
    agreement_id = Column(String(20), ForeignKey("agreements.id", ondelete="CASCADE"), nullable=False, index=True,
    comment="Sözleşme id'si")
    
    # ---- Version Information ---- #
    version_number = Column(Integer, nullable=False, index=True,
    comment="Versiyon numarası (1, 2, 3 vb.)")
    version_name = Column(String(100), nullable=True,
    comment="Versiyon adı (örn: 'v2.1', '2024 Update')")
    
    # ---- Content ---- #
    content = Column(Text, nullable=False,
    comment="Sözleşme içeriği (HTML veya Markdown)")
    content_hash = Column(String(64), nullable=True, index=True,
    comment="İçerik hash'i (değişiklik tespiti için)")
    
    # ---- Change Information ---- #
    change_summary = Column(Text, nullable=True,
    comment="Değişiklik özeti (kullanıcılara gösterilecek)")
    change_details = Column(Text, nullable=True,
    comment="Detaylı değişiklik notları (iç kullanım)")
    
    # ---- Status ---- #
    is_active = Column(Boolean, default=False, nullable=False, index=True,
    comment="Bu versiyon aktif mi?")
    
    # ---- Dates ---- #
    published_at = Column(DateTime(timezone=True), nullable=True,
    comment="Yayınlanma tarihi")
    effective_from = Column(DateTime(timezone=True), nullable=True,
    comment="Bu versiyonun geçerli olmaya başladığı tarih")
    effective_until = Column(DateTime(timezone=True), nullable=True,
    comment="Bu versiyonun geçerliliğinin bittiği tarih")
    
    # ---- Author Info ---- #
    created_by = Column(String(20), ForeignKey("users.id", ondelete="SET NULL"), nullable=True,
    comment="Versiyonu oluşturan kullanıcının id'si")
    approved_by = Column(String(20), ForeignKey("users.id", ondelete="SET NULL"), nullable=True,
    comment="Versiyonu onaylayan kullanıcının id'si")
    approved_at = Column(DateTime(timezone=True), nullable=True,
    comment="Onaylanma tarihi")
    
    # ---- Relations ---- #
    agreement = relationship("Agreement", back_populates="versions", foreign_keys=[agreement_id])
    acceptances = relationship("UserAgreementAcceptance", back_populates="agreement_version")
    creator = relationship("User", foreign_keys=[created_by])
    approver = relationship("User", foreign_keys=[approved_by])

