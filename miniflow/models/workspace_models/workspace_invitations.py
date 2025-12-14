from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship

from miniflow.database.models import Base
from miniflow.database.models.mixins import SoftDeleteMixin, TimestampMixin
from miniflow.models.enums import InvitationStatus


class WorkspaceInvitation(Base, SoftDeleteMixin, TimestampMixin):
    """Workspace davetleri - Workspace'e kullanıcı davet yönetimi"""
    __prefix__ = "WIN"
    __tablename__ = 'workspace_invitations'
    __allow_unmapped__ = True

    # ---- Relationships ---- #
    workspace_id = Column(String(20), ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=False, index=True,
    comment="Hangi workspace'e davet")
    invited_by = Column(String(20), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True,
    comment="Daveti gönderen kullanıcı")
    invitee_id = Column(String(20), ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True,
    comment="Davet edilen kullanıcı ID'si (kayıtlı ise)")
    role_id = Column(String(20), ForeignKey('workspace_roles.id', ondelete='RESTRICT'), nullable=False,
    comment="Verilecek rol")
    
    # ---- Invitation Details ---- #
    email = Column(String(255), nullable=False, index=True,
    comment="Davet edilen email adresi")
    message = Column(Text, nullable=True,
    comment="Davet mesajı (opsiyonel)")
    
    # ---- Status ---- #
    status = Column(Enum(InvitationStatus), default=InvitationStatus.PENDING, nullable=False, index=True,
    comment="Davet durumu (PENDING, ACCEPTED, DECLINED, EXPIRED, CANCELLED)")
    expires_at = Column(DateTime(timezone=True), nullable=True,
    comment="Davet son geçerlilik tarihi")
    responded_at = Column(DateTime(timezone=True), nullable=True,
    comment="Yanıt zamanı (kabul/red)")

    # ---- Relationships ---- #
    workspace = relationship("Workspace", back_populates="invitations")
    inviter = relationship("User", foreign_keys=[invited_by])
    invitee = relationship("User", foreign_keys=[invitee_id])
    role = relationship("WorkspaceRole")

    # ---- Helper Methods ---- #
    @property
    def is_pending(self) -> bool:
        return self.status == InvitationStatus.PENDING
    
    @property
    def is_expired(self) -> bool:
        if self.expires_at and self.status == InvitationStatus.PENDING:
            return datetime.now(timezone.utc) > self.expires_at
        return self.status == InvitationStatus.EXPIRED