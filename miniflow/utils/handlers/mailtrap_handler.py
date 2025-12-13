import mailtrap as mt
import threading
from typing import List, Optional, Dict, Any, Union

from miniflow.utils.handlers.environment_handler import EnvironmentHandler
from miniflow.utils.handlers.configuration_handler import ConfigurationHandler
from miniflow.core.exceptions import (
    ExternalServiceError,
    ExternalServiceTimeoutError,
    ExternalServiceAuthenticationError,
    ExternalServiceRateLimitError,
    ExternalServiceUnavailableError,
    InternalServiceValidationError,
)


class MailtrapHandler:
    """
    Mailtrap email handler - Singleton pattern (class-based)
    """
    
    # Class variables for singleton pattern
    _initialized: bool = False
    _lock: threading.Lock = threading.Lock()  # Thread safety için
    _client: Optional[mt.MailtrapClient] = None
    _api_key: Optional[str] = None
    _from_email: Optional[str] = None
    _from_name: Optional[str] = None
    _use_sandbox: bool = False
    
    # Template IDs (loaded from configuration)
    _email_verification_template_id: Optional[str] = None
    _first_login_template_id: Optional[str] = None
    _password_reset_template_id: Optional[str] = None
    _email_change_template_id: Optional[str] = None
    _password_change_template_id: Optional[str] = None
    _account_deletion_template_id: Optional[str] = None
    _new_device_login_template_id: Optional[str] = None
    
    @classmethod
    def initialize(cls, environment_name: str = "dev") -> None:
        """
        Handler'ı başlatır - ConfigurationHandler ve EnvironmentHandler'dan config yükler
        Thread-safe initialization
        """
        # Double-check locking pattern
        if cls._initialized:
            return
        
        with cls._lock:
            # Tekrar kontrol et (race condition önleme)
            if cls._initialized:
                return
        
        # ConfigurationHandler'ı yükle
        ConfigurationHandler.load_config(environment_name)
        
        # Default sender (ConfigurationHandler'dan)
        cls._from_email = ConfigurationHandler.get_value_as_str("MAILTRAP", "default_from_email")
        cls._from_name = ConfigurationHandler.get_value_as_str("MAILTRAP", "default_from_name")
        
        # Sandbox mode (ConfigurationHandler'dan, fallback EnvironmentHandler)
        sandbox_mode = ConfigurationHandler.get_value_as_bool("MAILTRAP", "sandbox_mode")
        if sandbox_mode is None:
            cls._use_sandbox = EnvironmentHandler.get_env("MAILTRAP_USE_SANDBOX", "true").lower() == "true"
        else:
            cls._use_sandbox = sandbox_mode
        
        # API Key (EnvironmentHandler'dan)
        # Önce MAILTRAP_API_KEY'i kontrol et, yoksa sandbox/transactional key'leri kullan
        cls._api_key = EnvironmentHandler.get_env("MAILTRAP_API_KEY")
        if not cls._api_key:
            # Sandbox mode için sandbox key, değilse transactional key kullan
            if cls._use_sandbox:
                cls._api_key = EnvironmentHandler.get_env("MAILTRAP_SANDBOX_API_KEY")
            else:
                cls._api_key = EnvironmentHandler.get_env("MAILTRAP_TRANSACTIONAL_TRANS_API_KEY")
        
        if not cls._api_key:
            raise InternalServiceValidationError(
                service_name="mailtrap_handler",
                validation_field="MAILTRAP_API_KEY",
                expected_value="non-empty string",
                actual_value=None,
                message="MAILTRAP_API_KEY, MAILTRAP_SANDBOX_API_KEY, or MAILTRAP_TRANSACTIONAL_TRANS_API_KEY environment variable is required"
            )
        
        # Sandbox ID (ConfigurationHandler'dan, fallback EnvironmentHandler)
        inbox_id = None
        sandbox_id = ConfigurationHandler.get_value_as_int("MAILTRAP", "sandbox_id")
        if sandbox_id is not None:
            inbox_id = sandbox_id
        elif cls._use_sandbox:
            # Fallback: EnvironmentHandler'dan oku
            inbox_id_str = EnvironmentHandler.get_env("MAILTRAP_INBOX_ID")
            if inbox_id_str:
                try:
                    inbox_id = int(inbox_id_str)
                except ValueError:
                    pass
        
        # Template IDs (ConfigurationHandler'dan dinamik olarak yükle)
        cls._email_verification_template_id = ConfigurationHandler.get_value_as_str("MAILTRAP", "email_verification_template_id")
        cls._first_login_template_id = ConfigurationHandler.get_value_as_str("MAILTRAP", "first_login_template_id")
        cls._password_reset_template_id = ConfigurationHandler.get_value_as_str("MAILTRAP", "password_reset_template_id")
        cls._email_change_template_id = ConfigurationHandler.get_value_as_str("MAILTRAP", "email_change_template_id")
        cls._password_change_template_id = ConfigurationHandler.get_value_as_str("MAILTRAP", "password_change_template_id")
        cls._account_deletion_template_id = ConfigurationHandler.get_value_as_str("MAILTRAP", "account_deletion_template_id")
        cls._new_device_login_template_id = ConfigurationHandler.get_value_as_str("MAILTRAP", "new_device_login_template_id")
        
        # Initialize client
        # inbox_id sadece sandbox mode'da kullanılır
        client_kwargs = {
            "token": cls._api_key,
            "sandbox": cls._use_sandbox
        }
        if cls._use_sandbox and inbox_id is not None:
            client_kwargs["inbox_id"] = inbox_id
        
        cls._client = mt.MailtrapClient(**client_kwargs)
        
        cls._initialized = True
    
    @classmethod
    def _ensure_initialized(cls) -> None:
        """Handler'ın başlatıldığından emin olur"""
        if not cls._initialized:
            cls.initialize()
    
    @classmethod
    def _validate_sender_email(cls, from_email: Optional[str] = None) -> str:
        """Gönderen email'i doğrular ve döndürür"""
        sender_email = from_email or cls._from_email
        if not sender_email:
            raise InternalServiceValidationError(
                service_name="mailtrap_handler",
                validation_field="from_email",
                expected_value="non-empty string",
                actual_value=None,
                message="Sender email is required. Set MAILTRAP_FROM_EMAIL in configuration or provide from_email parameter."
            )
        return sender_email
    
    @classmethod
    def _validate_template_id(cls, template_id: Optional[str], template_name: str) -> None:
        """Template ID'nin yapılandırıldığını doğrular"""
        if not template_id:
            raise InternalServiceValidationError(
                service_name="mailtrap_handler",
                validation_field=f"{template_name}_template_id",
                expected_value="non-empty string",
                actual_value=None,
                message=f"{template_name.replace('_', ' ').title()} template ID is not configured in MAILTRAP section of configuration file."
            )
    
    @classmethod
    def _handle_error(cls, e: Exception) -> None:
        """Mailtrap hatalarını Miniflow exception'larına çevirir"""
        error_str = str(e).lower()
        
        if "timeout" in error_str or "timed out" in error_str:
            raise ExternalServiceTimeoutError(
                service_name="mailtrap",
                service_type="email_provider"
            )
        
        if "rate limit" in error_str or "429" in error_str:
            raise ExternalServiceRateLimitError(
                service_name="mailtrap",
                service_type="email_provider"
            )
        
        if "401" in error_str or "unauthorized" in error_str:
            raise ExternalServiceAuthenticationError(
                service_name="mailtrap",
                service_type="email_provider"
            )
        
        if "connection" in error_str or "unreachable" in error_str:
            raise ExternalServiceUnavailableError(
                service_name="mailtrap",
                service_type="email_provider"
            )
        
        raise ExternalServiceError(
            service_name="mailtrap",
            service_type="email_provider",
            error_details={"original_error": str(e)}
        )
    
    @classmethod
    def send_email(
        cls,
        to_email: Union[str, List[str]],
        subject: str,
        text_content: Optional[str] = None,
        html_content: Optional[str] = None,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Basit email gönderir
        
        Args:
            to_email: Alıcı email adresi veya liste
            subject: Email konusu
            text_content: Metin içerik (opsiyonel)
            html_content: HTML içerik (opsiyonel)
            from_email: Gönderen email (opsiyonel, default kullanılır)
            from_name: Gönderen ismi (opsiyonel, default kullanılır)
            
        Returns:
            Mailtrap response dict
        """
        cls._ensure_initialized()
        
        # Göndereni hazırla ve doğrula
        sender_email = cls._validate_sender_email(from_email)
        sender = mt.Address(email=sender_email, name=from_name or cls._from_name)
        
        # Alıcıları hazırla
        email_list = [to_email] if isinstance(to_email, str) else to_email
        
        # Toplu email gönderiminde BCC kullan (gizlilik için)
        if len(email_list) > 1:
            # Çoklu alıcı: Tüm alıcılar BCC'de
            # Sandbox mode'da TO gereksinimi için ilk alıcı TO'da, production'da gönderen TO'da
            if cls._use_sandbox:
                # Sandbox: İlk alıcı TO'da (Mailtrap sandbox gereksinimi)
                to_list = [mt.Address(email=email_list[0])]
                bcc_list = [mt.Address(email=email) for email in email_list[1:]]
            else:
                # Production: Gönderen TO'da, tüm alıcılar BCC'de (maksimum gizlilik)
                to_list = [sender]
                bcc_list = [mt.Address(email=email) for email in email_list]
        else:
            # Tek alıcı: TO kullan
            to_list = [mt.Address(email=email_list[0])]
            bcc_list = None
        
        # Email headers (spam önleme ve güvenilirlik için)
        # Not: X-Priority: 1 spam filtreleri tarafından şüpheli görülebilir, kullanılmıyor
        # X-Auto-Response-Suppress: Otomatik yanıtları (out-of-office, auto-reply) bastırır
        headers = {
            "X-Mailer": "VidInsight Miniflow",
            "X-Auto-Response-Suppress": "OOF, AutoReply",
        }
        
        # Reply-To header (gönderen email ile aynı)
        reply_to = mt.Address(email=sender_email, name=from_name or cls._from_name)
        
        # Email oluştur
        mail = mt.Mail(
            sender=sender,
            to=to_list,
            bcc=bcc_list,
            subject=subject,
            text=text_content,
            html=html_content,
            headers=headers,
            reply_to=reply_to
        )
        
        # Gönder
        try:
            response = cls._client.send(mail)
            return response
        except Exception as e:
            cls._handle_error(e)  # Exception fırlatır, return'e ulaşılmaz
            raise  # Type safety için (unreachable)
    
    @classmethod
    def send_template_email(
        cls,
        to_email: Union[str, List[str]],
        template_uuid: str,
        template_variables: Dict[str, Any],
        from_email: Optional[str] = None,
        from_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Template kullanarak email gönderir
        
        Args:
            to_email: Alıcı email adresi veya liste
            template_uuid: Mailtrap template UUID
            template_variables: Template değişkenleri
            from_email: Gönderen email (opsiyonel)
            from_name: Gönderen ismi (opsiyonel)
            
        Returns:
            Mailtrap response dict
        """
        cls._ensure_initialized()
        
        # Göndereni hazırla ve doğrula
        sender_email = cls._validate_sender_email(from_email)
        sender_name = from_name or cls._from_name
        sender = mt.Address(email=sender_email, name=sender_name)
        
        # Alıcıları hazırla
        email_list = [to_email] if isinstance(to_email, str) else to_email
        
        # Toplu email gönderiminde BCC kullan (gizlilik için)
        if len(email_list) > 1:
            # Çoklu alıcı: Tüm alıcılar BCC'de
            # Sandbox mode'da TO gereksinimi için ilk alıcı TO'da, production'da gönderen TO'da
            if cls._use_sandbox:
                # Sandbox: İlk alıcı TO'da (Mailtrap sandbox gereksinimi)
                to_list = [mt.Address(email=email_list[0])]
                bcc_list = [mt.Address(email=email) for email in email_list[1:]]
            else:
                # Production: Gönderen TO'da, tüm alıcılar BCC'de (maksimum gizlilik)
                to_list = [sender]
                bcc_list = [mt.Address(email=email) for email in email_list]
        else:
            # Tek alıcı: TO kullan
            to_list = [mt.Address(email=email_list[0])]
            bcc_list = None
        
        # Email headers (spam önleme ve güvenilirlik için)
        # Not: X-Priority: 1 spam filtreleri tarafından şüpheli görülebilir, kullanılmıyor
        # X-Auto-Response-Suppress: Otomatik yanıtları (out-of-office, auto-reply) bastırır
        headers = {
            "X-Mailer": "VidInsight Miniflow",
            "X-Priority": "3",
            "X-Auto-Response-Suppress": "OOF, AutoReply",
        }
        
        # Reply-To header (gönderen email ile aynı)
        reply_to = mt.Address(email=sender_email, name=sender_name)
        
        # Template email oluştur
        mail = mt.MailFromTemplate(
            sender=sender,
            to=to_list,
            bcc=bcc_list,
            template_uuid=template_uuid,
            template_variables=template_variables,
            headers=headers,
            reply_to=reply_to
        )
        
        # Gönder
        try:
            response = cls._client.send(mail)
            return response
        except Exception as e:
            cls._handle_error(e)  # Exception fırlatır, return'e ulaşılmaz
            raise  # Type safety için (unreachable)
    
    @classmethod
    def send_email_verification(
        cls,
        to_email: str,
        *,
        name: str,
        surname: str,
        verification_url: str
    ) -> Dict[str, Any]:
        """
        Email doğrulama e-postası gönderir
        
        Args:
            to_email: Alıcı email
            name: Kullanıcı adı (USER_FIRST_NAME olarak template'e gönderilir)
            surname: Kullanıcı soyadı (USER_LAST_NAME olarak template'e gönderilir)
            verification_url: Doğrulama linki (VERIFICATION_URL olarak template'e gönderilir)
            
        Returns:
            Mailtrap response dict
        """
        cls._ensure_initialized()
        cls._validate_template_id(cls._email_verification_template_id, "email_verification")
        
        return cls.send_template_email(
            to_email=to_email,
            template_uuid=cls._email_verification_template_id,
            template_variables={
                "USER_FIRST_NAME": name,
                "USER_LAST_NAME": surname,
                "VERIFICATION_URL": verification_url
            }
        )
    
    @classmethod
    def send_welcome_email(
        cls,
        to_email: str,
        *,
        first_name: str,
        last_name: str,
        video_1_url: str,
        video_1_title: str,
        video_1_description: str,
        video_2_url: str,
        video_2_title: str,
        video_2_description: str,
        video_3_url: str,
        video_3_title: str,
        video_3_description: str,
        dashboard_url: str
    ) -> Dict[str, Any]:
        """
        Hoş geldin e-postası gönderir (Welcome Email)
        
        Args:
            to_email: Alıcı email
            first_name: Kullanıcı adı (USER_FIRST_NAME)
            last_name: Kullanıcı soyadı (USER_LAST_NAME)
            video_1_url: İlk video URL'i (VIDEO_1_URL)
            video_1_title: İlk video başlığı (VIDEO_1_TITLE)
            video_1_description: İlk video açıklaması (VIDEO_1_DESCRIPTION)
            video_2_url: İkinci video URL'i (VIDEO_2_URL)
            video_2_title: İkinci video başlığı (VIDEO_2_TITLE)
            video_2_description: İkinci video açıklaması (VIDEO_2_DESCRIPTION)
            video_3_url: Üçüncü video URL'i (VIDEO_3_URL)
            video_3_title: Üçüncü video başlığı (VIDEO_3_TITLE)
            video_3_description: Üçüncü video açıklaması (VIDEO_3_DESCRIPTION)
            dashboard_url: Dashboard URL'i (DASHBOARD_URL)
            
        Returns:
            Mailtrap response dict
        """
        cls._ensure_initialized()
        cls._validate_template_id(cls._first_login_template_id, "first_login")
        
        return cls.send_template_email(
            to_email=to_email,
            template_uuid=cls._first_login_template_id,
            template_variables={
                "USER_FIRST_NAME": first_name,
                "USER_LAST_NAME": last_name,
                "VIDEO_1_URL": video_1_url,
                "VIDEO_1_TITLE": video_1_title,
                "VIDEO_1_DESCRIPTION": video_1_description,
                "VIDEO_2_URL": video_2_url,
                "VIDEO_2_TITLE": video_2_title,
                "VIDEO_2_DESCRIPTION": video_2_description,
                "VIDEO_3_URL": video_3_url,
                "VIDEO_3_TITLE": video_3_title,
                "VIDEO_3_DESCRIPTION": video_3_description,
                "DASHBOARD_URL": dashboard_url
            }
        )
    
    @classmethod
    def send_password_reset_email(
        cls,
        to_email: str,
        *,
        first_name: str,
        last_name: str,
        password_reset_url: str
    ) -> Dict[str, Any]:
        """
        Şifre sıfırlama e-postası gönderir
        
        Args:
            to_email: Alıcı email
            first_name: Kullanıcı adı (USER_FIRST_NAME olarak template'e gönderilir)
            last_name: Kullanıcı soyadı (USER_LAST_NAME olarak template'e gönderilir)
            password_reset_url: Şifre sıfırlama linki (PASSWORD_RESET_URL olarak template'e gönderilir)
            
        Returns:
            Mailtrap response dict
        """
        cls._ensure_initialized()
        cls._validate_template_id(cls._password_reset_template_id, "password_reset")
        
        return cls.send_template_email(
            to_email=to_email,
            template_uuid=cls._password_reset_template_id,
            template_variables={
                "USER_FIRST_NAME": first_name,
                "USER_LAST_NAME": last_name,
                "PASSWORD_RESET_URL": password_reset_url
            }
        )
    
    @classmethod
    def send_email_change_email(
        cls,
        to_email: str,
        *,
        first_name: str,
        last_name: str,
        old_email: str,
        new_email: str,
        email_change_url: str
    ) -> Dict[str, Any]:
        """
        Email değişikliği e-postası gönderir
        
        Args:
            to_email: Alıcı email (eski email)
            first_name: Kullanıcı adı (USER_FIRST_NAME olarak template'e gönderilir)
            last_name: Kullanıcı soyadı (USER_LAST_NAME olarak template'e gönderilir)
            old_email: Eski email adresi (OLD_EMAIL olarak template'e gönderilir)
            new_email: Yeni email adresi (NEW_EMAIL olarak template'e gönderilir)
            email_change_url: Email değişikliği onay linki (EMAIL_CHANGE_URL olarak template'e gönderilir)
            
        Returns:
            Mailtrap response dict
        """
        cls._ensure_initialized()
        cls._validate_template_id(cls._email_change_template_id, "email_change")
        
        return cls.send_template_email(
            to_email=to_email,
            template_uuid=cls._email_change_template_id,
            template_variables={
                "USER_FIRST_NAME": first_name,
                "USER_LAST_NAME": last_name,
                "OLD_EMAIL": old_email,
                "NEW_EMAIL": new_email,
                "EMAIL_CHANGE_URL": email_change_url
            }
        )
    
    @classmethod
    def send_password_change_email(
        cls,
        to_email: str,
        *,
        first_name: str,
        last_name: str,
        change_date: str,
        change_time: str,
        ip_address: str,
        device_info: str,
        password_reset_url: str
    ) -> Dict[str, Any]:
        """
        Şifre değişikliği e-postası gönderir
        
        Args:
            to_email: Alıcı email
            first_name: Kullanıcı adı (USER_FIRST_NAME olarak template'e gönderilir)
            last_name: Kullanıcı soyadı (USER_LAST_NAME olarak template'e gönderilir)
            change_date: Değişiklik tarihi (CHANGE_DATE olarak template'e gönderilir)
            change_time: Değişiklik saati (CHANGE_TIME olarak template'e gönderilir)
            ip_address: IP adresi (IP_ADDRESS olarak template'e gönderilir)
            device_info: Cihaz bilgisi (DEVICE_INFO olarak template'e gönderilir)
            password_reset_url: Şifre sıfırlama URL'i (PASSWORD_RESET_URL olarak template'e gönderilir)
            
        Returns:
            Mailtrap response dict
        """
        cls._ensure_initialized()
        cls._validate_template_id(cls._password_change_template_id, "password_change")
        
        return cls.send_template_email(
            to_email=to_email,
            template_uuid=cls._password_change_template_id,
            template_variables={
                "USER_FIRST_NAME": first_name,
                "USER_LAST_NAME": last_name,
                "CHANGE_DATE": change_date,
                "CHANGE_TIME": change_time,
                "IP_ADDRESS": ip_address,
                "DEVICE_INFO": device_info,
                "PASSWORD_RESET_URL": password_reset_url
            }
        )
    
    @classmethod
    def send_account_deletion_email(
        cls,
        to_email: str,
        *,
        first_name: str,
        last_name: str,
        deletion_date: str
    ) -> Dict[str, Any]:
        """
        Hesap silme e-postası gönderir
        
        Args:
            to_email: Alıcı email
            first_name: Kullanıcı adı (USER_FIRST_NAME olarak template'e gönderilir)
            last_name: Kullanıcı soyadı (USER_LAST_NAME olarak template'e gönderilir)
            deletion_date: Hesap silme tarihi (DELETION_DATE olarak template'e gönderilir)
            
        Returns:
            Mailtrap response dict
        """
        cls._ensure_initialized()
        cls._validate_template_id(cls._account_deletion_template_id, "account_deletion")
        
        return cls.send_template_email(
            to_email=to_email,
            template_uuid=cls._account_deletion_template_id,
            template_variables={
                "USER_FIRST_NAME": first_name,
                "USER_LAST_NAME": last_name,
                "DELETION_DATE": deletion_date
            }
        )
    
    @classmethod
    def send_new_device_login_email(
        cls,
        to_email: str,
        *,
        first_name: str,
        last_name: str,
        login_date: str,
        login_time: str,
        device_info: str,
        browser_info: str,
        location: str,
        ip_address: str,
        password_reset_url: str,
        sessions_url: str
    ) -> Dict[str, Any]:
        """
        Yeni cihazdan giriş e-postası gönderir
        
        Args:
            to_email: Alıcı email
            first_name: Kullanıcı adı (USER_FIRST_NAME olarak template'e gönderilir)
            last_name: Kullanıcı soyadı (USER_LAST_NAME olarak template'e gönderilir)
            login_date: Giriş tarihi (LOGIN_DATE olarak template'e gönderilir)
            login_time: Giriş saati (LOGIN_TIME olarak template'e gönderilir)
            device_info: Cihaz bilgisi (DEVICE_INFO olarak template'e gönderilir)
            browser_info: Tarayıcı bilgisi (BROWSER_INFO olarak template'e gönderilir)
            location: Konum bilgisi (LOCATION olarak template'e gönderilir)
            ip_address: IP adresi (IP_ADDRESS olarak template'e gönderilir)
            password_reset_url: Şifre sıfırlama URL'i (PASSWORD_RESET_URL olarak template'e gönderilir)
            sessions_url: Oturumlar URL'i (SESSIONS_URL olarak template'e gönderilir)
            
        Returns:
            Mailtrap response dict
        """
        cls._ensure_initialized()
        cls._validate_template_id(cls._new_device_login_template_id, "new_device_login")
        
        return cls.send_template_email(
            to_email=to_email,
            template_uuid=cls._new_device_login_template_id,
            template_variables={
                "USER_FIRST_NAME": first_name,
                "USER_LAST_NAME": last_name,
                "LOGIN_DATE": login_date,
                "LOGIN_TIME": login_time,
                "DEVICE_INFO": device_info,
                "BROWSER_INFO": browser_info,
                "LOCATION": location,
                "IP_ADDRESS": ip_address,
                "PASSWORD_RESET_URL": password_reset_url,
                "SESSIONS_URL": sessions_url
            }
        )
