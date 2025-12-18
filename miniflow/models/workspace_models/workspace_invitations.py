from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum, UniqueConstraint, Index
from sqlalchemy.orm import relationship

from miniflow.database.models import Base
from miniflow.database.models.mixins import SoftDeleteMixin, TimestampMixin
from miniflow.models.enums import InvitationStatus


class WorkspaceInvitation(Base, SoftDeleteMixin, TimestampMixin):
    """Workspace davetleri - Workspace'e kullanıcı davet yönetimi"""
    __prefix__ = "WIN"
    __tablename__ = 'workspace_invitations'
    
    # ---- Table Args ---- #
    __table_args__ = (
        # Basit unique constraint - aynı workspace'de aynı email'e sadece bir pending invitation
        # PostgreSQL'de partial unique index için: Index('idx_workspace_invitations_pending', 'workspace_id', 'email', 'status', unique=True, postgresql_where=(status == 'PENDING')),
        UniqueConstraint('workspace_id', 'email', name='uq_workspace_invitation_workspace_email'),
        Index('idx_workspace_invitations_workspace_status', 'workspace_id', 'status'),
        Index('idx_workspace_invitations_email_status', 'email', 'status'),
        Index('idx_workspace_invitations_softdelete', 'is_deleted', 'created_at'),
    )

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
    expires_at = Column(DateTime(timezone=True), nullable=True, index=True,
    comment="Davet son geçerlilik tarihi")
    responded_at = Column(DateTime(timezone=True), nullable=True,
    comment="Yanıt zamanı (kabul/red)")

    # ---- Relationships ---- #
    workspace = relationship("Workspace", back_populates="invitations")
    inviter = relationship("User", foreign_keys=[invited_by], back_populates="sent_invitations")
    invitee = relationship("User", foreign_keys=[invitee_id], back_populates="received_invitations")
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