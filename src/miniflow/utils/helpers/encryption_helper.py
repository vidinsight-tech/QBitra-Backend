import bcrypt
import hashlib
from typing import Optional
from cryptography.fernet import Fernet

from ..handlers import EnvironmentHandler
from src.miniflow.core.exceptions import InvalidInputError, InternalError


# Cache variables for lazy loading
_encryption_key: Optional[bytes] = None
_cipher: Optional[Fernet] = None


def _get_encryption_key() -> bytes:
    global _encryption_key
    
    if _encryption_key is None:
        key = EnvironmentHandler.get("ENCRYPTION_KEY")

        if key:
            _encryption_key = key.encode() if isinstance(key, str) else key
        else:
            print("\n[WARNING] ENCRYPTION_KEY ayarlanmamış. Geçici anahtar üretiliyor.")
            print("[WARNING] Production için ENCRYPTION_KEY ortam değişkenini ayarlayın.")
            new_key = Fernet.generate_key()
            print(f"[WARNING] Oluşturulan yeni encryption key {new_key}")
            _encryption_key = new_key
    
    return _encryption_key


def _get_cipher() -> Fernet:
    global _cipher
    
    if _cipher is None:
        _cipher = Fernet(_get_encryption_key())
    
    return _cipher


def encrypt_data(plain_text: str) -> str:
    if not plain_text:
        return ""
    
    try:
        encrypted_bytes = _get_cipher().encrypt(plain_text.encode('utf-8'))
        return encrypted_bytes.decode('utf-8')
    except Exception:
        raise InternalError(component_name="encryption_helper")
    
def decrypt_data(encrypted_text: str) -> str:
    if not encrypted_text:
        return ""
    
    try:
        decrypted_bytes = _get_cipher().decrypt(encrypted_text.encode('utf-8'))
        return decrypted_bytes.decode('utf-8')
    except Exception:
        raise InternalError(component_name="encryption_helper")
    
def hash_password(password: str, rounds: int = 12) -> str:
    if not password:
        raise InvalidInputError(field_name="password")
    
    try:
        salt = bcrypt.gensalt(rounds=rounds)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    except Exception:
        raise InternalError(component_name="encryption_helper")
    
def verify_password(password: str, hashed_password: str) -> bool:
    if not password or not hashed_password:
        return False
    
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False

def hash_data(data: str) -> str:
    if not data:
        return ""
    
    try:
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
    except Exception:
        raise InternalError(component_name="encryption_helper")