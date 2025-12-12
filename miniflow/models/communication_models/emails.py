from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer, JSON
from sqlalchemy.orm import relationship
from miniflow.database.models import Base


class Email(Base):
    """Kullanıcı modeli - Tüm mixin'lerle."""
    __prefix__ = "EML"
    __tablename__ = 'emails'

    # ---- Email Content ---- #
    from_email = Column(String(255), nullable=False,
    comment="Gönderen e-posta adresi")
    to_email = Column(String(255), nullable=False, index=True,
    comment="Alıcı e-posta adresi")
    subject = Column(String(512), nullable=False,
    comment="E-posta başlığı")

    text_body = Column(String(255), nullable=False,
    comment="E-posta içeriği (Metin olarak gönderilecek ise burası doldurulur)")
    html_body = Column(Text, nullable=True,
    comment="E-posta içeriği (HTML olarka gönderilecek ise)")
    

    # ---- Provider Info ---- #
    provider = Column(String(50), nullable=False,
    comment="E-posta göndermek için kullanılan sağlayıcı (mailtrap, ses, sendgrid)")  
    provider_message_id = Column(String(255), nullable=True, index=True,
    comment="Sağlayıcında dönen id")

    # ---- Delivery State ---- #
    status = Column(String(50), nullable=False, default="pending",
    comment="E-posta gönderim durumu")
    is_test = Column(Boolean, default=False,
    comment="Test E-postası olup olmadığına dair flag")
    retry_count = Column(Integer, default=0,
    comment="Gönderimin tekrar denenme sayısı")
    last_error_code = Column(String(100), nullable=True,
    comment="Son gönderim denemesinde alınan hata kodu")
    last_error_message = Column(Text, nullable=True,
    comment="Son gönderim denemesinde alınan hata mesajı")
    provider_response = Column(JSON, nullable=True,
    comment="Provider tarafında dönülen responseun tamamı")

    # ---- Timestamps ---- #
    sent_at = Column(DateTime(timezone=True), nullable=True,
    comment="Sistemnde gönderilme zamanı")
    delivered_at = Column(DateTime(timezone=True), nullable=True,
    comment="Kaşrı tarafı teslim zamanı")
    failed_at = Column(DateTime(timezone=True), nullable=True,
    comment="Hata (alınırsa) zamanı")

    # ---- Relations ---- #
    attachments = relationship("EmailAttachment", back_populates="email", cascade="all, delete-orphan")