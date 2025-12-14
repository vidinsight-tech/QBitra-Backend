import bcrypt
import hashlib
from typing import Optional
from cryptography.fernet import Fernet

from miniflow.utils.handlers.environment_handler import EnvironmentHandler
from miniflow.utils.handlers.configuration_handler import ConfigurationHandler
from miniflow.core.exceptions import (
    InvalidInputError,
    InternalServiceError,
    InternalServiceValidationError
)

# Cache değişkenleri (lazy loading)
_encryption_key: Optional[bytes] = None
_bcrypt_rounds: Optional[int] = 12
_cipher: Optional[Fernet] = None


def _ensure_config_loaded() -> None:
    """Config'in yüklendiğinden emin olur."""
    global _config_loaded, _cipher, _bcrypt_rounds
    
    if _config_loaded:
        return
    
    _bcrypt_rounds = ConfigurationHandler.get_value_as_int("SECURITY", "bcrypt_rounds", 12)
    key = EnvironmentHandler.get_env("ENCRYPTION_KEY")
    
    if not key:
        raise InternalServiceValidationError(
            service_name="encryption_helper",
            validation_field="ENCRYPTION_KEY",
            expected_value="base64 encoded 32-byte key",
            actual_value=None,
            message="ENCRYPTION_KEY environment variable is required. "
        )
    
    try:
        key_bytes = key.encode() if isinstance(key, str) else key
        _cipher = Fernet(key_bytes)
    except Exception:
        raise InternalServiceValidationError(
            service_name="encryption_helper",
            validation_field="ENCRYPTION_KEY",
            expected_value="valid Fernet key (base64 encoded 32-byte)",
            actual_value="invalid format",
            message="ENCRYPTION_KEY format is invalid"
        )
    
    _config_loaded = True

def encrypt_data(plain_text: str) -> str:
    """Metni Fernet ile şifreler."""
    if not plain_text:
        return ""
    
    _ensure_config_loaded()
    
    try:
        encrypted_bytes = _cipher.encrypt(plain_text.encode('utf-8'))
        return encrypted_bytes.decode('utf-8')
    except Exception:
        raise InternalServiceError(
            service_name="encryption_helper",
            message="Encryption failed"
        )


def decrypt_data(encrypted_text: str) -> str:
    """Şifreli metni çözer."""
    if not encrypted_text:
        return ""
    
    _ensure_config_loaded()
    
    try:
        decrypted_bytes = _cipher.decrypt(encrypted_text.encode('utf-8'))
        return decrypted_bytes.decode('utf-8')
    except Exception:
        raise InternalServiceError(
            service_name="encryption_helper",
            message="Decryption failed"
        )


def hash_password(password: str, rounds: Optional[int] = None) -> str:
    """Şifreyi bcrypt ile hashler."""
    if not password:
        raise InvalidInputError(
            field_name="password",
            message="Password cannot be empty"
        )
    
    _ensure_config_loaded()
    
    actual_rounds = rounds if rounds is not None else _bcrypt_rounds
    
    try:
        salt = bcrypt.gensalt(rounds=actual_rounds)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    except Exception:
        raise InternalServiceError(
            service_name="encryption_helper",
            message="Password hashing failed"
        )


def verify_password(password: str, hashed_password: str) -> bool:
    """Şifreyi hash ile doğrular."""
    if not password or not hashed_password:
        return False
    
    try:
        return bcrypt.checkpw(
            password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except Exception:
        return False


def hash_data(data: str) -> str:
    """Veriyi SHA-256 ile hashler."""
    if not data:
        return ""
    
    try:
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
    except Exception:
        raise InternalServiceError(
            service_name="encryption_helper",
            message="Data hashing failed"
        )