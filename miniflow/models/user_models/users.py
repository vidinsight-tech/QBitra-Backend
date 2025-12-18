import re
import secrets
from datetime import datetime, timezone, timedelta
from typing import Dict
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, Index
from sqlalchemy.orm import relationship

from miniflow.database.models import Base
from miniflow.database.models.mixins import SoftDeleteMixin


class User(Base, SoftDeleteMixin):
    """Kullanıcı modeli"""
    __prefix__ = "USR"
    __tablename__ = "users"
    
    # ---- Table Args ---- #
    __table_args__ = (
        Index('idx_users_softdelete', 'is_deleted'),
    )

    # ---- User Authentication Information ---- #
    username = Column(String(100), nullable=False, unique=True, index=True, 
    comment="Kullanıcı adı")
    email = Column(String(100), nullable=False, unique=True, index=True, 
    comment="E-posta adresi")
    password = Column(String(100), nullable=False, 
    comment="Kullanıcı şifresi")
    is_admin = Column(Boolean, default=False, nullable=False, index=True,
    comment="Kullanıcı admin mi?")

    # ---- User Information ---- #
    name = Column(String(100), nullable=False, 
    comment="Kullanıcı adı")
    surname = Column(String(100), nullable=False, 
    comment="Kullanıcı soyadı")
    country_code = Column(String(2), nullable=True, 
    comment="ISO ülke kodu")
    phone_number = Column(String(20), nullable=True, unique=True, index=True,
    comment="E.164 formatı: +905551234567")

    # ---- User Information Verification Status ---- #
    email_verified_at = Column(DateTime(timezone=True), nullable=True, 
    comment="E-posta doğrulama tarihi")
    phone_verified_at = Column(DateTime(timezone=True), nullable=True, 
    comment="Telefon doğrulama tarihi")

    # ---- User Information Verification Tokens ---- #
    email_verification_token = Column(String(100), nullable=True, index=True,
    comment="E-posta doğrulama tokeni")
    email_verification_token_expires_at = Column(DateTime(timezone=True), nullable=True, 
    comment="E-posta doğrulama tokeni süresi")
    phone_verification_token = Column(String(100), nullable=True, 
    comment="Telefon doğrulama tokeni")
    phone_verification_token_expires_at = Column(DateTime(timezone=True), nullable=True, 
    comment="Telefon doğrulama tokeni süresi")
    password_reset_token = Column(String(100), nullable=True, index=True,
    comment="Şifre sıfırlama tokeni")
    password_reset_token_expires_at = Column(DateTime(timezone=True), nullable=True, 
    comment="Şifre sıfırlama tokeni süresi")

    # ---- User Information Audit ---- #
    password_last_changed_at = Column(DateTime(timezone=True), nullable=True, 
    comment="Şifre son değiştirilme tarihi")
    email_last_verified_at = Column(DateTime(timezone=True), nullable=True, 
    comment="E-posta son doğrulama tarihi")
    phone_last_verified_at = Column(DateTime(timezone=True), nullable=True, 
    comment="Telefon son doğrulama tarihi")
    username_last_verified_at = Column(DateTime(timezone=True), nullable=True, 
    comment="Kullanıcı adı son doğrulama tarihi")

    # ---- User Account Suspension Status ---- #
    is_suspended = Column(Boolean, default=False, nullable=False, index=True,
    comment="Kullanıcı hesabı askıya alındı mı?")
    suspended_at = Column(DateTime(timezone=True), nullable=True, 
    comment="Kullanıcı hesabı askıya alındığı tarih")
    suspended_reason = Column(Text, nullable=True, 
    comment="Kullanıcı hesabı askıya alındığı nedeni")
    suspension_expires_at = Column(DateTime(timezone=True), nullable=True, 
    comment="Kullanıcı hesabı askıya alındığı süre sonu")

    # ---- User Account Lock Status ---- #
    is_locked = Column(Boolean, default=False, nullable=False, index=True,
    comment="Kullanıcı hesabı kilitlendi mi?")
    locked_at = Column(DateTime(timezone=True), nullable=True, 
    comment="Kullanıcı hesabı kilitlendiği tarih")
    locked_reason = Column(Text, nullable=True, 
    comment="Kullanıcı hesabı kilitlendiği nedeni")
    lock_expires_at = Column(DateTime(timezone=True), nullable=True, 
    comment="Kullanıcı hesabı kilitlendiği süre sonu")

    # ---- User Account Workspace Information ---- #
    current_workspace_count = Column(Integer, default=0, nullable=False,
    comment="Kullanıcının mevcut çalışma alanı sayısı")
    current_free_workspace_count = Column(Integer, default=0, nullable=False,
    comment="Kullanıcının mevcut ücretsiz çalışma alanı sayısı")

    # ---- Relationships ---- #
    agreement_acceptances = relationship("UserAgreementAcceptance", back_populates="user")
    auth_sessions = relationship("AuthSession", foreign_keys="AuthSession.user_id", back_populates="user")
    login_history = relationship("LoginHistory", back_populates="user")
    uploaded_scripts = relationship("CustomScript", foreign_keys="CustomScript.uploaded_by", back_populates="uploader")
    script_reviews = relationship("ScriptReviewHistory", foreign_keys="ScriptReviewHistory.reviewed_by", back_populates="reviewer")
    api_keys = relationship("ApiKey", foreign_keys="ApiKey.owner_id", back_populates="owner")
    credentials = relationship("Credential", foreign_keys="Credential.owner_id", back_populates="owner")
    databases = relationship("Database", foreign_keys="Database.owner_id", back_populates="owner")
    uploaded_files = relationship("File", foreign_keys="File.owner_id", back_populates="owner")
    created_variables = relationship("Variable", foreign_keys="Variable.owner_id", back_populates="owner")
    
    # Workspace relationships
    owned_workspaces = relationship("Workspace", foreign_keys="Workspace.owner_id", back_populates="owner")
    workspace_memberships = relationship("WorkspaceMember", foreign_keys="WorkspaceMember.user_id", back_populates="user")
    sent_invitations = relationship("WorkspaceInvitation", foreign_keys="WorkspaceInvitation.invited_by", back_populates="inviter")
    received_invitations = relationship("WorkspaceInvitation", foreign_keys="WorkspaceInvitation.invitee_id", back_populates="invitee")
    
    # Communication relationships
    tickets = relationship("Ticket", back_populates="user")
    
    # Information relationships
    audit_logs = relationship("AuditLog", back_populates="user")
    notifications = relationship("Notification", back_populates="user")

    # ---- Helper Methods ---- #
    @property
    def full_name(self) -> str:
        return f"{self.name} {self.surname}"

    @staticmethod
    def validate_email_format(email: str) -> bool:
        """E-posta formatını doğrula"""
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_regex, email))
    
    @staticmethod
    def validate_password_strength(password: str) -> Dict[str, any]:
        """Şifre gücünü politika karşısında doğrula"""
        errors = []
        
        if len(password) < 8:
            errors.append("Şifre en az 8 karakter olmalıdır")
        if not re.search(r'[A-Z]', password):
            errors.append("Şifre en az bir büyük harf içermelidir")
        if not re.search(r'[a-z]', password):
            errors.append("Şifre en az bir küçük harf içermelidir")
        if not re.search(r'\d', password):
            errors.append("Şifre en az bir rakam içermelidir")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\\/~`]', password):
            errors.append("Şifre en az bir özel karakter içermelidir")
        
        return {"valid": len(errors) == 0, "errors": errors}
    
    @staticmethod
    def validate_username(username: str) -> Dict[str, any]:
        """Kullanıcı adı formatını doğrula"""
        errors = []
        
        if len(username) < 3:
            errors.append("Kullanıcı adı en az 3 karakter olmalıdır")
        if len(username) > 50:
            errors.append("Kullanıcı adı en fazla 50 karakter olabilir")
        if not re.match(r'^[a-zA-Z0-9][a-zA-Z0-9_-]*[a-zA-Z0-9]$', username):
            errors.append("Kullanıcı adı sadece harf, rakam, alt çizgi ve tire içerebilir")
        
        return {"valid": len(errors) == 0, "errors": errors}
    
    def generate_email_verification_token(self) -> str:
        """E-posta doğrulama tokeni oluştur"""
        self.email_verification_token = secrets.token_urlsafe(32)
        self.email_verification_token_expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
        return self.email_verification_token
    
    def verify_email_verification_token(self, token: str) -> bool:
        """E-posta doğrulama tokeni doğrula"""
        if not self.email_verification_token or not self.email_verification_token_expires_at:
            return False
        if self.email_verification_token != token:
            return False
        if self.email_verification_token_expires_at < datetime.now(timezone.utc):
            return False
        return True
    
    def generate_phone_verification_token(self) -> str:
        """Telefon doğrulama tokeni oluştur"""
        # TODO: Implement phone verification token generation
    
    def verify_phone_verification_token(self, token: str) -> bool:
        """Telefon doğrulama tokeni doğrula"""
        # TODO: Implement phone verification token verification

    def generate_password_reset_token(self) -> str:
        """Şifre sıfırlama tokeni oluştur"""
        self.password_reset_token = secrets.token_urlsafe(32)
        self.password_reset_token_expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
        return self.password_reset_token

    def verify_password_reset_token(self, token: str) -> bool:
        """Şifre sıfırlama tokeni doğrula"""
        if not self.password_reset_token or not self.password_reset_token_expires_at:
            return False
        if self.password_reset_token != token:
            return False
        if self.password_reset_token_expires_at < datetime.now(timezone.utc):
            return False
        return True