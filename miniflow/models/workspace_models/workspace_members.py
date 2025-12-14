from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship

from miniflow.database.models import Base
from miniflow.database.models.mixins import SoftDeleteMixin, TimestampMixin


class WorkspaceMember(Base, SoftDeleteMixin, TimestampMixin):
    """Workspace üyeleri - User ve Workspace arasında many-to-many ilişki"""
    __prefix__ = "WMB"
    __tablename__ = 'workspace_members'
    __allow_unmapped__ = True

    # ---- Relationships ---- #
    workspace_id = Column(String(20), ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=False, index=True,
    comment="Workspace ID'si")
    user_id = Column(String(20), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True,
    comment="Kullanıcı ID'si")
    role_id = Column(String(20), ForeignKey('workspace_roles.id', ondelete='RESTRICT'), nullable=False, index=True,
    comment="Kullanıcı rolü ID'si")
    invited_by = Column(String(20), ForeignKey('users.id', ondelete='SET NULL'), nullable=True,
    comment="Daveti gönderen kullanıcı (null = owner)")
    
    # ---- Membership Details ---- #
    joined_at = Column(DateTime(timezone=True), nullable=True,
    comment="Katılma zamanı")
    custom_permissions = Column(JSON, default=lambda: {}, nullable=True,
    comment="Rol izinlerini override etmek için JSON")

    # ---- Relationships ---- #
    workspace = relationship("Workspace", back_populates="members")
    user = relationship("User", foreign_keys=[user_id], back_populates="workspace_memberships")
    role = relationship("WorkspaceRole", back_populates="workspace_members")
    inviter = relationship("User", foreign_keys=[invited_by])

    # ---- Helper Methods ---- #
    def update_last_accessed(self):
        self.last_accessed_at = datetime.now(timezone.utc)
    
    def has_permission(self, permission: str) -> bool:
        """Belirtilen izni kontrol et (custom_permissions > role permissions)"""
        # Önce custom_permissions kontrol et
        if self.custom_permissions and permission in self.custom_permissions:
            return self.custom_permissions[permission]
        # Sonra role permissions kontrol et
        return getattr(self.role, permission, False)
