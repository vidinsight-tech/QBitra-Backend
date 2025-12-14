from sqlalchemy import Column, String, Integer, Boolean, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from miniflow.database.models import Base
from miniflow.database.models.mixins import SoftDeleteMixin, TimestampMixin


class Workspace(Base, SoftDeleteMixin, TimestampMixin):
    """Workspace - Çalışma alanları, workflow'ları organize etmek ve takım işbirliği için"""
    __prefix__ = "WSP"
    __tablename__ = 'workspaces'
    __allow_unmapped__ = True

    # ---- Basic Information ---- #
    name = Column(String(100), nullable=False, index=True,
    comment="Workspace adı")
    slug = Column(String(100), nullable=False, unique=True, index=True,
    comment="URL-friendly benzersiz slug")
    description = Column(Text, nullable=True,
    comment="Workspace açıklaması")
    
    # ---- Ownership ---- #
    owner_id = Column(String(20), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True,
    comment="Workspace sahibi")
    
    # ---- Plan ---- #
    plan_id = Column(String(20), ForeignKey('workspace_plans.id', ondelete='RESTRICT'), nullable=False, index=True,
    comment="Mevcut plan")
    plan_name = Column(String(50), nullable=False,
    comment="Plan adı")
    
    # ---- Current Limits (from plan) ---- #
    member_limit = Column(Integer, nullable=False,
    comment="Üye limiti")
    workflow_limit = Column(Integer, nullable=False,
    comment="Workflow limiti")
    custom_script_limit = Column(Integer, nullable=False,
    comment="Custom script limiti")
    storage_limit_mb = Column(Integer, nullable=False,
    comment="Depolama limiti (MB)")
    max_file_size_mb = Column(Integer, nullable=False,
    comment="Maksimum dosya boyutu (MB)")
    api_key_limit = Column(Integer, nullable=False,
    comment="API key limiti")
    monthly_execution_limit = Column(Integer, nullable=False,
    comment="Aylık execution limiti")
    max_concurrent_executions = Column(Integer, nullable=False,
    comment="Eşzamanlı execution limiti")
    
    # ---- Current Usage ---- #
    current_member_count = Column(Integer, default=1, nullable=False,
    comment="Mevcut üye sayısı")
    current_workflow_count = Column(Integer, default=0, nullable=False,
    comment="Mevcut workflow sayısı")
    current_custom_script_count = Column(Integer, default=0, nullable=False,
    comment="Mevcut custom script sayısı")
    current_storage_mb = Column(Float, default=0.0, nullable=False,
    comment="Mevcut depolama kullanımı (MB)")
    current_api_key_count = Column(Integer, default=0, nullable=False,
    comment="Mevcut API key sayısı")
    current_month_executions = Column(Integer, default=0, nullable=False,
    comment="Bu ay execution sayısı")
    
    # ---- Suspension Status ---- #
    is_suspended = Column(Boolean, default=False, nullable=False, index=True,
    comment="Askıya alınmış mı?")
    suspension_reason = Column(Text, nullable=True,
    comment="Askıya alma nedeni")
    suspended_at = Column(DateTime(timezone=True), nullable=True,
    comment="Askıya alma zamanı")

    # ---- Relationships ---- #
    owner = relationship("User", foreign_keys=[owner_id], back_populates="owned_workspaces")
    plan = relationship("WorkspacePlan", back_populates="workspaces")
    members = relationship("WorkspaceMember", back_populates="workspace", cascade="all, delete-orphan")
    invitations = relationship("WorkspaceInvitation", back_populates="workspace", cascade="all, delete-orphan")
    
    # Resource relationships
    workflows = relationship("Workflow", back_populates="workspace", cascade="all, delete-orphan")
    custom_scripts = relationship("CustomScript", back_populates="workspace", cascade="all, delete-orphan")
    api_keys = relationship("ApiKey", back_populates="workspace", cascade="all, delete-orphan")
    credentials = relationship("Credential", back_populates="workspace", cascade="all, delete-orphan")
    databases = relationship("Database", back_populates="workspace", cascade="all, delete-orphan")
    files = relationship("File", back_populates="workspace", cascade="all, delete-orphan")
    variables = relationship("Variable", back_populates="workspace", cascade="all, delete-orphan")
    
    # Execution relationships
    executions = relationship("Execution", back_populates="workspace", cascade="all, delete-orphan")
    execution_inputs = relationship("ExecutionInput", back_populates="workspace", cascade="all, delete-orphan")
    execution_outputs = relationship("ExecutionOutput", back_populates="workspace", cascade="all, delete-orphan")