from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, ForeignKey, Enum, Boolean, Integer
from sqlalchemy.orm import relationship

from miniflow.database.models import Base
from miniflow.database.models.mixins import SoftDeleteMixin, TimestampMixin
from miniflow.models.enums import ScriptApprovalStatus


class ScriptReviewHistory(Base, SoftDeleteMixin, TimestampMixin):
    """Script review mesajlaşma zinciri - detaylı review mesajlaşma sistemi"""
    __prefix__ = "SRH"
    __tablename__ = 'script_review_history'
    __allow_unmapped__ = True

    # ---- Script Relationship ---- #
    script_id = Column(String(20), ForeignKey('custom_scripts.id', ondelete='CASCADE'), nullable=False, index=True,
    comment="Review edilen script id'si")
    
    # ---- Reviewer Information ---- #
    reviewed_by = Column(String(20), ForeignKey('users.id', ondelete='SET NULL'), nullable=False, index=True,
    comment="Script'i review eden kullanıcı")
    
    # ---- Review Status ---- #
    review_status = Column(Enum(ScriptApprovalStatus), nullable=False, index=True,
    comment="Review durumu (PENDING, IN_REVIEW, APPROVED, REJECTED, CHANGES_REQUESTED, RESUBMITTED)")
    
    # ---- Review Message ---- #
    review_notes = Column(Text, nullable=True,
    comment="Review mesajı/notları")
    review_title = Column(String(255), nullable=True,
    comment="Review başlığı (opsiyonel)")
    
    # ---- Review Priority & Flags ---- #
    is_urgent = Column(Boolean, default=False, nullable=False, index=True,
    comment="Acil review mu?")
    is_auto_reviewed = Column(Boolean, default=False, nullable=False,
    comment="Otomatik review mu? (test sonuçlarına göre)")
    requires_changes = Column(Boolean, default=False, nullable=False,
    comment="Değişiklik gerekiyor mu?")
    
    # ---- Review Scores (Basit) ---- #
    overall_score = Column(Integer, nullable=True,
    comment="Genel skor (0-100, opsiyonel)")
    
    # ---- Review Chain ---- #
    previous_review_id = Column(String(20), ForeignKey('script_review_history.id', ondelete='SET NULL'), nullable=True,
    comment="Önceki review id'si (mesajlaşma zinciri için)")
    
    # ---- Review Context ---- #
    review_reason = Column(String(255), nullable=True,
    comment="Review nedeni (kısa açıklama)")
    
    # ---- Relations ---- #
    script = relationship("CustomScript", back_populates="review_history")
    reviewer = relationship("User", foreign_keys=[reviewed_by], back_populates="script_reviews")
    previous_review = relationship("ScriptReviewHistory", remote_side="ScriptReviewHistory.id", back_populates="next_reviews")
    next_reviews = relationship("ScriptReviewHistory", back_populates="previous_review", foreign_keys=[previous_review_id])
