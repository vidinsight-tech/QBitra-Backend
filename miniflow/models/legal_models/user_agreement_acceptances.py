from sqlalchemy import Column, String, ForeignKey, DateTime, Boolean, Text, JSON, UniqueConstraint, Index
from sqlalchemy.orm import relationship

from miniflow.database.models import Base
from miniflow.database.models.mixins import TimestampMixin


class UserAgreementAcceptance(Base, TimestampMixin):
    """Kullanıcı sözleşme kabul kayıtları modeli."""
    __prefix__ = "UAA"
    __tablename__ = "user_agreement_acceptances"

    # ---- Table Args ---- #
    __table_args__ = (
        UniqueConstraint('user_id', 'agreement_id', 'agreement_version_id', name='uq_user_agreement_acceptance'),
        Index('idx_user_agreement_acceptances_user_agreement_active', 'user_id', 'agreement_id', 'is_active'),
        Index('idx_user_agreement_acceptances_agreement_date', 'agreement_id', 'accepted_at'),
    )

    # ---- User Relationship ---- #
    user_id = Column(String(20), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True,
    comment="Kullanıcı id'si")
    
    # ---- Agreement Relationships ---- #
    agreement_id = Column(String(20), ForeignKey("agreements.id", ondelete="CASCADE"), nullable=False, index=True,
    comment="Sözleşme id'si")
    agreement_version_id = Column(String(20), ForeignKey("agreement_versions.id", ondelete="CASCADE"), nullable=False, index=True,
    comment="Kabul edilen versiyon id'si")
    
    # ---- Acceptance Info ---- #
    accepted_at = Column(DateTime(timezone=True), nullable=False, index=True,
    comment="Kabul edilme tarihi")
    ip_address = Column(String(64), nullable=True,
    comment="Kabul edildiği IP adresi")
    user_agent = Column(String(512), nullable=True,
    comment="Kabul edildiği user agent")
    
    # ---- Status ---- #
    is_active = Column(Boolean, default=True, nullable=False, index=True,
    comment="Kabul aktif mi? (yeni versiyon geldiğinde false olabilir)")
    is_revoked = Column(Boolean, default=False, nullable=False, index=True,
    comment="Kabul iptal edildi mi?")
    revoked_at = Column(DateTime(timezone=True), nullable=True,
    comment="İptal edilme tarihi")
    revocation_reason = Column(Text, nullable=True,
    comment="İptal nedeni")
    
    # ---- Consent Details ---- #
    consent_method = Column(String(50), nullable=True,
    comment="Kabul yöntemi (checkbox, button, api vb.)")
    consent_location = Column(String(255), nullable=True,
    comment="Kabul edildiği sayfa/lokasyon")
    
    # ---- Legal Evidence ---- #
    evidence_data = Column(JSON, nullable=True,
    comment="Yasal kanıt verileri (timestamp, hash, signature vb.)")
    
    # ---- Relations ---- #
    user = relationship("User", back_populates="agreement_acceptances")
    agreement = relationship("Agreement", back_populates="acceptances")
    agreement_version = relationship("AgreementVersion", back_populates="acceptances")