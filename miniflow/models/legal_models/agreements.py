from sqlalchemy import Column, String, Text, ForeignKey, Boolean, DateTime, Integer, Enum, JSON
from sqlalchemy.orm import relationship

from miniflow.database.models import Base
from miniflow.database.models.mixins import TimestampMixin
from miniflow.models.enums import AgreementType, AgreementStatus


class Agreement(Base, TimestampMixin):
    __prefix__ = "AGR"
    __tablename__ = "agreements"
    __allow_unmapped__ = True

    # ---- Agreement Information ---- #
    agreement_type = Column(Enum(AgreementType), nullable=False, index=True,
    comment="Sözleşme tipi (terms_of_service, privacy_policy vb.)")
    title = Column(String(255), nullable=False,
    comment="Sözleşme başlığı")
    description = Column(Text, nullable=True,
    comment="Sözleşme açıklaması")
    
    # ---- Status ---- #
    status = Column(Enum(AgreementStatus), nullable=False, default=AgreementStatus.DRAFT, index=True,
    comment="Sözleşme durumu (draft, active, archived, deprecated)")
    
    # ---- Current Version ---- #
    current_version_id = Column(String(20), ForeignKey("agreement_versions.id", ondelete="SET NULL"), nullable=True,
    comment="Aktif versiyon id'si")
    
    # ---- Requirements ---- #
    is_required = Column(Boolean, default=True, nullable=False, index=True,
    comment="Kullanıcılar için zorunlu mu?")
    
    # ---- Display Settings ---- #
    display_order = Column(Integer, default=0, nullable=False, index=True,
    comment="Görüntüleme sırası")
    show_on_signup = Column(Boolean, default=True, nullable=False,
    comment="Kayıt sırasında gösterilsin mi?")

    
    # ---- Legal Info ---- #
    effective_date = Column(DateTime(timezone=True), nullable=True,
    comment="Yürürlük tarihi")
    expiration_date = Column(DateTime(timezone=True), nullable=True,
    comment="Son geçerlilik tarihi (opsiyonel)")
    jurisdiction = Column(String(100), nullable=True,
    comment="Yargı yetkisi (ülke/bölge)")
    language = Column(String(10), nullable=False, default="tr",
    comment="Sözleşme dili (tr, en vb.)")
    
    # ---- Metadata ---- #
    metadata = Column(JSON, nullable=True,
    comment="Ek metadata bilgileri")
    
    # ---- Relations ---- #
    current_version = relationship("AgreementVersion", foreign_keys=[current_version_id], post_update=True)
    versions = relationship("AgreementVersion", back_populates="agreement", cascade="all, delete-orphan", order_by="desc(AgreementVersion.version_number)")
    acceptances = relationship("UserAgreementAcceptance", back_populates="agreement")

