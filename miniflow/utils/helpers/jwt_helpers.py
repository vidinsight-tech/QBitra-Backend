import jwt
from typing import Dict, Any, Tuple, Optional
from datetime import datetime, timezone, timedelta

from miniflow.utils.handlers.environment_handler import EnvironmentHandler
from miniflow.utils.handlers.configuration_handler import ConfigurationHandler
from miniflow.core.exceptions import (
    TokenExpiredError,
    TokenInvalidError,
    InternalServiceValidationError
)


# Cache değişkenleri (lazy loading)
_config_loaded: bool = False
_secret_key: Optional[str] = None
_algorithm: Optional[str] = "HS256"
_access_expire_minutes: Optional[int] = 30
_refresh_expire_days: Optional[int] = 7
_access_token_type: Optional[str] = "access"
_refresh_token_type: Optional[str] = "refresh"


def _ensure_config_loaded() -> None:
    """Konfigürasyonun yüklendiğinden emin olur."""
    global _config_loaded, _secret_key, _algorithm
    global _access_expire_minutes, _refresh_expire_days
    global _access_token_type, _refresh_token_type
    
    if _config_loaded:
        return

    # Secret key (.env'den - zorunlu)
    _secret_key = EnvironmentHandler.get_env("JWT_SECRET_KEY")
    if not _secret_key:
        raise InternalServiceValidationError(
            service_name="jwt_helper",
            validation_field="JWT_SECRET_KEY",
            expected_value="non-empty string",
            actual_value=None,
            message="JWT_SECRET_KEY environment variable is required for token operations."
        )
    
    # Diğer ayarlar (dev.ini'den - varsayılan değerlerle)
    _algorithm = ConfigurationHandler.get_value_as_str("JWT", "algorithm")
    _access_expire_minutes = ConfigurationHandler.get_value_as_int("JWT", "access_token_expire_minutes", 30)
    _refresh_expire_days = ConfigurationHandler.get_value_as_int("JWT", "refresh_token_expire_days", 7)
    _access_token_type = ConfigurationHandler.get_value_as_str("JWT", "access_token_type", "access")
    _refresh_token_type = ConfigurationHandler.get_value_as_str("JWT", "refresh_token_type", "refresh")
    
    _config_loaded = True

def create_access_token(
    user_id: str,
    jti: str,
    additional_claims: Optional[Dict[str, Any]] = None
) -> Tuple[str, datetime]:
    """Access token oluşturur."""
    _ensure_config_loaded()

    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(minutes=_access_expire_minutes)
    
    payload = {
        "sub": user_id,
        "jti": jti,
        "token_type": _access_token_type,
        "exp": int(expires_at.timestamp()),
        "iat": int(now.timestamp()),
        "nbf": int(now.timestamp())
    }
    
    if additional_claims:
        payload.update(additional_claims)

    token = jwt.encode(payload, _secret_key, _algorithm)
    return token, expires_at

def create_refresh_token(
    user_id: str,
    jti: str,
    additional_claims: Optional[Dict[str, Any]] = None
) -> Tuple[str, datetime]:
    """Refresh token oluşturur."""
    _ensure_config_loaded()

    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(days=_refresh_expire_days)
    
    payload = {
        "sub": user_id,
        "jti": jti,
        "token_type": _refresh_token_type,
        "exp": int(expires_at.timestamp()),
        "iat": int(now.timestamp()),
        "nbf": int(now.timestamp())
    }
    
    if additional_claims:
        payload.update(additional_claims)
    
    token = jwt.encode(payload, _secret_key, _algorithm)
    return token, expires_at

def validate_access_token(token: str) -> Tuple[bool, Dict[str, Any]]:
    """Access token doğrular."""
    _ensure_config_loaded()

    try:
        payload = jwt.decode(token, _secret_key, algorithms=[_algorithm])

        if payload.get("token_type") != _access_token_type:
            raise TokenInvalidError(token_type="access", reason="token_type_mismatch")
        
        return True, payload

    except jwt.ExpiredSignatureError:
        raise TokenExpiredError(token_type="access")
    except jwt.InvalidTokenError:
        raise TokenInvalidError(token_type="access")

def validate_refresh_token(token: str) -> Tuple[bool, Dict[str, Any]]:
    """Refresh token doğrular."""
    _ensure_config_loaded()

    try:
        payload = jwt.decode(token, _secret_key, algorithms=[_algorithm])
        
        if payload.get("token_type") != _refresh_token_type:
            raise TokenInvalidError(token_type="refresh", reason="token_type_mismatch")
        
        return True, payload
        
    except jwt.ExpiredSignatureError:
        raise TokenExpiredError(token_type="refresh")
    except jwt.InvalidTokenError:
        raise TokenInvalidError(token_type="refresh")

def decode_token_without_validation(token: str) -> Optional[Dict[str, Any]]:
    """Token'ı imza doğrulaması yapmadan decode eder."""
    try:
        return jwt.decode(token, options={"verify_signature": False})
    except Exception:
        return None

def get_token_remaining_time(payload: Dict[str, Any]) -> Optional[int]:
    """Token'ın kalan süresini saniye cinsinden döndürür."""
    if not payload or "exp" not in payload:
        return None

    remaining = payload["exp"] - int(datetime.now(timezone.utc).timestamp())
    return max(remaining, 0)

def is_token_valid(payload: Dict[str, Any]) -> bool:
    """Token'ın süresinin dolup dolmadığını kontrol eder."""
    remaining = get_token_remaining_time(payload)
    return remaining is not None and remaining > 0

def refresh_access_token(refresh_token: str, new_jti: str) -> Tuple[str, datetime]:
    """Refresh token ile yeni access token üretir."""
    _ensure_config_loaded()

    is_valid, payload = validate_refresh_token(refresh_token)
    if not is_valid:
        raise TokenInvalidError(token_type="refresh", reason="validation_failed")

    # Yeni access token oluştur
    access_token, expires_at = create_access_token(
        user_id=payload["user_id"],
        jti=new_jti,
        additional_claims={
            "refresh_jti": payload.get("jti"),  # Hangi refresh token'dan geldiği
            "refreshed_at": int(datetime.now(timezone.utc).timestamp())
        }
    )
    
    return access_token, expires_at
