from sqlalchemy import Column, String, Integer, Boolean, Text, Index
from sqlalchemy.orm import relationship

from miniflow.database.models import Base
from miniflow.database.models.mixins import SoftDeleteMixin, TimestampMixin


class WorkspaceRole(Base, SoftDeleteMixin, TimestampMixin):
    """Workspace rolleri ve yetkileri - Workspace içinde kullanıcı rollerini ve izinlerini yönetir"""
    __prefix__ = "WRL"
    __tablename__ = 'workspace_roles'
    
    # ---- Table Args ---- #
    __table_args__ = (
        Index('idx_workspace_roles_softdelete', 'is_deleted', 'created_at'),
    )

    # ---- Basic Information ---- #
    name = Column(String(50), nullable=False, unique=True, index=True,
    comment="Rol adı (Owner, Admin, Editor, Viewer)")
    description = Column(Text, nullable=True,
    comment="Rol açıklaması")
    
    # ---- Workspace Permissions ---- #
    can_view_workspace = Column(Boolean, default=True, nullable=False,
    comment="Workspace görüntüleme")
    can_edit_workspace = Column(Boolean, default=False, nullable=False,
    comment="Workspace düzenleme")
    can_delete_workspace = Column(Boolean, default=False, nullable=False,
    comment="Workspace silme")
    can_invite_members = Column(Boolean, default=False, nullable=False,
    comment="Üye davet etme")
    can_remove_members = Column(Boolean, default=False, nullable=False,
    comment="Üye çıkarma")
    can_change_plan = Column(Boolean, default=False, nullable=False,
    comment="Plan değiştirme")
    
    # ---- Workflow Permissions ---- #
    can_view_workflows = Column(Boolean, default=True, nullable=False,
    comment="Workflow görüntüleme")
    can_create_workflows = Column(Boolean, default=False, nullable=False,
    comment="Workflow oluşturma")
    can_edit_workflows = Column(Boolean, default=False, nullable=False,
    comment="Workflow düzenleme")
    can_delete_workflows = Column(Boolean, default=False, nullable=False,
    comment="Workflow silme")
    can_execute_workflows = Column(Boolean, default=True, nullable=False,
    comment="Workflow çalıştırma")
    
    # ---- Credential Permissions ---- #
    can_view_credentials = Column(Boolean, default=True, nullable=False,
    comment="Credential görüntüleme")
    can_create_credentials = Column(Boolean, default=False, nullable=False,
    comment="Credential oluşturma")
    can_edit_credentials = Column(Boolean, default=False, nullable=False,
    comment="Credential düzenleme")
    can_delete_credentials = Column(Boolean, default=False, nullable=False,
    comment="Credential silme")
    can_view_credential_values = Column(Boolean, default=False, nullable=False,
    comment="Credential değerlerini görme")
    
    # ---- File Permissions ---- #
    can_view_files = Column(Boolean, default=True, nullable=False,
        comment="Dosya görüntüleme")
    can_upload_files = Column(Boolean, default=False, nullable=False,
        comment="Dosya yükleme")
    can_download_files = Column(Boolean, default=True, nullable=False,
        comment="Dosya indirme")
    can_delete_files = Column(Boolean, default=False, nullable=False,
        comment="Dosya silme")
    
    # ---- Database Permissions ---- #
    can_view_databases = Column(Boolean, default=True, nullable=False,
    comment="Database görüntüleme")
    can_create_databases = Column(Boolean, default=False, nullable=False,
    comment="Database oluşturma")
    can_edit_databases = Column(Boolean, default=False, nullable=False,
    comment="Database düzenleme")
    can_delete_databases = Column(Boolean, default=False, nullable=False,
    comment="Database silme")
    can_view_connection_details = Column(Boolean, default=False, nullable=False,
    comment="Bağlantı detaylarını görme")
    
    # ---- Variable Permissions ---- #
    can_view_variables = Column(Boolean, default=True, nullable=False,
    comment="Variable görüntüleme")
    can_create_variables = Column(Boolean, default=False, nullable=False,
    comment="Variable oluşturma")
    can_edit_variables = Column(Boolean, default=False, nullable=False,
    comment="Variable düzenleme")
    can_delete_variables = Column(Boolean, default=False, nullable=False,
    comment="Variable silme")
    can_view_variable_values = Column(Boolean, default=False, nullable=False,
    comment="Variable değerlerini görme")
    
    # ---- API Key Permissions ---- #
    can_view_api_keys = Column(Boolean, default=True, nullable=False,
    comment="API Key görüntüleme")
    can_create_api_keys = Column(Boolean, default=False, nullable=False,
    comment="API Key oluşturma")
    can_edit_api_keys = Column(Boolean, default=False, nullable=False,
    comment="API Key düzenleme")
    can_delete_api_keys = Column(Boolean, default=False, nullable=False,
    comment="API Key silme")
    can_view_api_key_values = Column(Boolean, default=False, nullable=False,
    comment="API Key değerlerini görme")
    
    # ---- System Flags ---- #
    is_system_role = Column(Boolean, default=False, nullable=False,
    comment="Sistem rolü mü? (silinemez)")
    display_order = Column(Integer, default=0, nullable=False,
    comment="Sıralama")

    # ---- Relationships ---- #
    workspace_members = relationship("WorkspaceMember", back_populates="role")
