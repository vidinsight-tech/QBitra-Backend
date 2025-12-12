from sqlalchemy import Column, String, Text, JSON, ForeignKey, DateTime, Integer, Enum, Boolean
from sqlalchemy.orm import relationship

from miniflow.database.models import Base
from miniflow.database.models.mixins import TimestampMixin
from miniflow.models.enums import CrashSeverity, CrashStatus


class CrashLog(Base, TimestampMixin):
    """Sistemde önemli hataları tutan crash log modeli."""
    __prefix__ = "CRL"
    __tablename__ = "crash_logs"
    __allow_unmapped__ = True

    # ---- User Context (Optional) ---- #
    user_id = Column(String(20), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True,
    comment="Hata yaşayan kullanıcının id'si")
    user_email = Column(String(255), nullable=True,
    comment="Hata yaşayan kullanıcının e-posta adresi")

    # ---- Crash Information ---- #
    error_type = Column(String(255), nullable=False, index=True,
    comment="Hata tipi (örn: TypeError, ValueError, ConnectionError)")
    error_message = Column(Text, nullable=False,
    comment="Hata mesajı")
    stack_trace = Column(Text, nullable=True,
    comment="Detaylı stack trace bilgisi")
    
    # ---- Severity & Status ---- #
    severity = Column(Enum(CrashSeverity), nullable=False, default=CrashSeverity.MEDIUM, index=True,
    comment="Hatanın önem seviyesi (low, medium, high, critical)")
    status = Column(Enum(CrashStatus), nullable=False, default=CrashStatus.NEW, index=True,
    comment="Hatanın durumu (new, investigating, resolved, ignored, duplicate)")
    
    # ---- Context Information (Workflow/Execution) ---- #
    workflow_id = Column(String(20), nullable=True, index=True,
    comment="İlgili workflow id'si (varsa)")
    execution_id = Column(String(20), nullable=True, index=True,
    comment="İlgili execution id'si (varsa)")
    node_id = Column(String(20), nullable=True, index=True,
    omment="İlgili node id'si (varsa)")
    trace_id = Column(String(255), nullable=True, index=True,
    comment="Trace id (distributed tracing için)")
    
    # ---- Page/Route Context ---- #
    page_url = Column(String(512), nullable=True,
    comment="Hata yaşanan sayfa URL'i")
    route_path = Column(String(255), nullable=True,
    comment="Hata yaşanan route path'i")
    http_method = Column(String(10), nullable=True,
    omment="HTTP method (GET, POST, PUT, DELETE vb.)")
    
    # ---- Environment Info ---- #
    app_version = Column(String(50), nullable=True, index=True,
    comment="Uygulama versiyonu")
    environment = Column(String(50), nullable=True, index=True,
    comment="Ortam (production, staging, beta, development)")
    browser = Column(String(100), nullable=True,
    comment="Tarayıcı bilgisi")
    browser_version = Column(String(50), nullable=True,
    comment="Tarayıcı versiyonu")
    os = Column(String(100), nullable=True,
    comment="İşletim sistemi bilgisi")
    os_version = Column(String(50), nullable=True,
    comment="İşletim sistemi versiyonu")
    
    # ---- Additional Context ---- #
    context = Column(JSON, nullable=True,
    comment="Ek context bilgileri (anonymous_id, custom fields vb.)")
    request_data = Column(JSON, nullable=True,
    comment="Request body/query params (hassas bilgiler hariç)")
    response_data = Column(JSON, nullable=True,
    comment="Response data (hata durumunda)")
    
    # ---- Resolution Tracking ---- #
    is_resolved = Column(Boolean, default=False, nullable=False, index=True,
    comment="Hata çözüldü mü?")
    resolved_at = Column(DateTime(timezone=True), nullable=True,
    comment="Hatanın çözüldüğü zaman")
    resolved_by = Column(String(20), ForeignKey("users.id", ondelete="SET NULL"), nullable=True,
    omment="Çözmeyi yapan kullanıcının id'si")
    resolution_notes = Column(Text, nullable=True,
    comment="Çözüm notları")
    fix_version = Column(String(50), nullable=True,
    comment="Düzeltmenin yapıldığı versiyon")
    
    # ---- Related Ticket ---- #
    related_ticket_id = Column(String(20), ForeignKey("tickets.id", ondelete="SET NULL"), nullable=True, index=True,
    comment="Bu hatayla ilgili açılan ticket id'si")
    
    # ---- Occurrence Tracking ---- #
    occurrence_count = Column(Integer, default=1, nullable=False,
    comment="Aynı hatanın kaç kez tekrarlandığı")
    first_occurred_at = Column(DateTime(timezone=True), nullable=True,
    comment="Hatanın ilk oluştuğu zaman (occurrence_count > 1 ise)")
    last_occurred_at = Column(DateTime(timezone=True), nullable=True,
    comment="Hatanın son oluştuğu zaman")
    
    # ---- Relations ---- #
    user = relationship("User", foreign_keys=[user_id])
    resolver = relationship("User", foreign_keys=[resolved_by])
    related_ticket = relationship("Ticket", foreign_keys=[related_ticket_id])