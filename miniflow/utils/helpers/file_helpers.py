import os
import io
import uuid
import shutil
import zipfile
import mimetypes
import unicodedata
import threading
from weakref import WeakValueDictionary
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Tuple, Set, BinaryIO, TextIO, Union, TypedDict

from miniflow.core.exceptions import (
    ResourceNotFoundError,
    InvalidInputError,
    InternalServiceError
)
from miniflow.utils.handlers.configuration_handler import ConfigurationHandler

# Constants
MAX_FILENAME_LENGTH: int = 255  # Düzeltildi: Tip annotasyonu ayrı, değer ayrı

# Thread-safe globals
_base_storage_path: Optional[str] = None
_base_storage_path_lock = threading.Lock()
_directory_locks: WeakValueDictionary[str, threading.Lock] = WeakValueDictionary()
_directory_locks_lock = threading.Lock()


class UploadResult(TypedDict):
    """Dosya yükleme sonuç yapısı"""
    file_name: str
    file_path: str
    file_size: int
    mime_type: str
    extension: str


# Script MIME type mapping (fallback - mimetypes.guess_type() tanımazsa kullanılır)
_SCRIPT_MIME_TYPE_MAP = {
    '.py': 'text/x-python',
    '.js': 'application/javascript',
    '.ts': 'application/typescript',
    '.sh': 'application/x-sh',
    '.bash': 'application/x-sh',
    '.zsh': 'application/x-sh',
    '.ps1': 'application/x-powershell',
    '.rb': 'text/x-ruby',
    '.php': 'text/x-php',
    '.go': 'text/x-go',
    '.java': 'text/x-java-source',
    '.cpp': 'text/x-c++src',
    '.c': 'text/x-csrc',
}


# ============================================
# THREAD-SAFE HELPERS
# ============================================

def ensure_directory(path: str) -> None:
    """Thread-safe directory creation."""
    with _directory_locks_lock:
        if path not in _directory_locks:
            _directory_locks[path] = threading.Lock()
        dir_lock = _directory_locks[path]
    
    with dir_lock:
        Path(path).mkdir(parents=True, exist_ok=True)


def _get_base_storage_path() -> str:
    """Thread-safe base storage path getter with lazy initialization."""
    global _base_storage_path

    if _base_storage_path is None:
        with _base_storage_path_lock:
            if _base_storage_path is None:
                project_root = Path(__file__).resolve().parents[3]
                storage_path = project_root / 'resources'
                _base_storage_path = str(storage_path)
    
    return _base_storage_path


# ============================================
# SECURITY HELPERS
# ============================================

def sanitize_filename(name: str) -> str:
    """Dosya adını güvenli hale getirir (path traversal koruması)."""
    if not name:
        return "file"

    name = unicodedata.normalize('NFC', name)

    # Path traversal koruması
    while ".." in name:
        name = name.replace("..", "")
    name = name.replace("/", "")
    name = name.replace("\\", "")
    name = name.replace("\x00", "")
    name = name.replace(" ", "_")

    # Tehlikeli karakterleri kaldır
    name = "".join(c for c in name if c.isalnum() or c in "._-")

    # Son kontrol
    if not name or name in (".", "..") or name.startswith("..") or ".." in name:
        name = "file"

    if len(name) > MAX_FILENAME_LENGTH:
        name_part, ext = os.path.splitext(name)
        max_name_length = MAX_FILENAME_LENGTH - len(ext)
        if max_name_length > 0:
            name = name_part[:max_name_length] + ext
        else:
            name = name[:MAX_FILENAME_LENGTH]

    return name


def _check_symlink(path: Path) -> None:
    """Path veya parent'larında symlink kontrolü."""
    current = path
    while current != current.parent:
        if current.is_symlink():
            raise InvalidInputError(
                field_name="path",
                message="Symlink detected in path - security risk"
            )
        current = current.parent


def _validate_path_traversal(file_path: Path, base_path: Path) -> None:
    """Path traversal kontrolü yapar."""
    _check_symlink(file_path)
    
    resolved_path = file_path.resolve()
    base_resolved = base_path.resolve()
    
    try:
        resolved_path.relative_to(base_resolved)
    except ValueError:
        raise InvalidInputError(
            field_name="path",
            message="Path traversal attempt detected"
        )


def _validate_workspace_id(workspace_id: str) -> str:
    """Workspace ID'yi doğrular ve sanitize eder."""
    safe_workspace_id = sanitize_filename(workspace_id)
    if not safe_workspace_id or safe_workspace_id in (".", ".."):
        raise InvalidInputError(
            field_name="workspace_id",
            message="Invalid workspace ID"
        )
    return safe_workspace_id


def _get_safe_workspace_path(workspace_id: str, subfolder: str) -> str:
    """Workspace path oluşturur ve doğrular (DRY helper)."""
    base_path = _get_base_storage_path()
    safe_workspace_id = _validate_workspace_id(workspace_id)
    
    file_path = Path(base_path) / subfolder / safe_workspace_id
    _validate_path_traversal(file_path, Path(base_path))
    return str(file_path.resolve())


# ============================================
# ATOMIC FILE OPERATIONS
# ============================================

def _atomic_file_write(content: Union[str, bytes], file_path: str, is_binary: bool = False) -> None:
    """Atomic file write (TOCTOU koruması)."""
    directory = os.path.dirname(file_path)
    if directory:
        ensure_directory(directory)
    
    temp_file_path = file_path + '.tmp'
    
    try:
        mode = 'wb' if is_binary else 'w'
        encoding = None if is_binary else 'utf-8'
        
        with open(temp_file_path, mode, encoding=encoding) as f:
            f.write(content)
        
        # Güvenli dosya izinleri
        try:
            os.chmod(temp_file_path, 0o600)
        except (OSError, PermissionError):
            pass
        
        # Atomic rename
        try:
            os.rename(temp_file_path, file_path)
        except (OSError, PermissionError):
            # Network filesystem fallback
            shutil.copy2(temp_file_path, file_path)
            os.remove(temp_file_path)
    
    except OSError as e:
        _cleanup_temp_file(temp_file_path)
        
        error_code = getattr(e, 'errno', None)
        if error_code == 28:  # ENOSPC
            raise InvalidInputError(
                field_name="file_path",
                message="Disk quota exceeded or no space left on device"
            )
        elif error_code == 122:  # EDQUOT
            raise InvalidInputError(
                field_name="file_path",
                message="Disk quota exceeded"
            )
        else:
            raise InvalidInputError(
                field_name="file_path",
                message="File system error occurred"
            )
    except Exception:
        _cleanup_temp_file(temp_file_path)
        raise InvalidInputError(
            field_name="file_path",
            message="File could not be saved"
        )


def _cleanup_temp_file(temp_file_path: str) -> None:
    """Temp dosyayı güvenli şekilde temizler."""
    try:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
    except Exception:
        pass


# ============================================
# FILE PATH GENERATION/ACCESS HELPERS
# ============================================

def create_resources_folder() -> None:
    """Resources klasör yapısını oluşturur."""
    base_path = _get_base_storage_path()
    ensure_directory(base_path)
    
    for folder_name in ["files", "temp", "global_scripts", "custom_scripts"]:
        folder_path = os.path.join(base_path, folder_name)
        ensure_directory(folder_path)


def get_global_script_path() -> str:
    """Global script path döndürür."""
    base_path = _get_base_storage_path()
    file_path = Path(base_path) / "global_scripts"
    _validate_path_traversal(file_path, Path(base_path))
    return str(file_path.resolve())


def get_workspace_global_script_path(workspace_id: str) -> str:
    """Workspace global script path döndürür."""
    return _get_safe_workspace_path(workspace_id, "global_scripts")


def get_workspace_custom_script_path(workspace_id: str) -> str:
    """Workspace custom script path döndürür."""
    return _get_safe_workspace_path(workspace_id, "custom_scripts")


def get_workspace_file_path(workspace_id: str) -> str:
    """Workspace file path döndürür."""
    return _get_safe_workspace_path(workspace_id, "files")


def get_workspace_temp_path(workspace_id: str) -> str:
    """Workspace temp path döndürür."""
    return _get_safe_workspace_path(workspace_id, "temp")


# ============================================
# FILE SIZE/EXISTS HELPERS
# ============================================

def get_folder_size(folder_path: str) -> int:
    """Klasör boyutunu byte cinsinden döndürür."""
    if not os.path.exists(folder_path):
        raise ResourceNotFoundError(
            resource_type="folder",
            resource_path=folder_path
        )

    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder_path, followlinks=False):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.isfile(fp) and not os.path.islink(fp):
                total_size += os.path.getsize(fp)
    
    return total_size


def file_exists(file_path: str) -> bool:
    """Dosyanın var olup olmadığını kontrol eder."""
    return os.path.exists(file_path) and os.path.isfile(file_path)


def get_file_size(file_path: str) -> int:
    """Dosya boyutunu byte cinsinden döndürür."""
    if not file_exists(file_path):
        raise ResourceNotFoundError(
            resource_type="file",
            resource_path=file_path
        )
    
    return os.path.getsize(file_path)


# ============================================
# WORKSPACE QUOTA CHECK HELPERS
# ============================================

def get_max_workspace_quota() -> Optional[int]:
    """Sistem maksimum workspace quota limitini byte cinsinden döndürür."""
    max_quota_mb = ConfigurationHandler.get_value_as_int(
        "FILE OPERATIONS", "max_workspace_quota_mb", None
    )
   
    if max_quota_mb:
        return max_quota_mb * 1024 * 1024
    
    # Düzeltildi: Yorum ve değer uyumlu hale getirildi (25 GB default)
    return 25 * 1024 * 1024 * 1024  # 25 GB


def check_workspace_quota(
    workspace_id: str,
    required_bytes: int,
    quota_limit_mb: Optional[int] = None
) -> Tuple[bool, Optional[int]]:
    """
    Workspace quota kontrolü yapar.
    
    Args:
        workspace_id: Workspace ID
        required_bytes: Gereken byte miktarı
        quota_limit_mb: Workspace quota limiti (MB) - Veritabanından gelecek. None ise sınırsız.
    
    Returns:
        Tuple[bool, Optional[int]]: (yeterli_mu, kalan_byte)
    """
    max_quota = get_max_workspace_quota()
    
    if quota_limit_mb is not None:
        quota_limit_bytes = quota_limit_mb * 1024 * 1024
        
        if max_quota is not None and quota_limit_bytes > max_quota:
            quota_limit_bytes = max_quota
    else:
        quota_limit_bytes = max_quota
    
    if quota_limit_bytes is None:
        return True, None  # Sınırsız
    
    try:
        current_usage = get_folder_size(get_workspace_file_path(workspace_id))
    except ResourceNotFoundError:
        current_usage = 0
    
    remaining = quota_limit_bytes - current_usage
    has_space = remaining >= required_bytes
    
    return has_space, max(remaining, 0)


# ============================================
# FOLDER OPERATIONS
# ============================================

def delete_folder(folder_path: str) -> None:
    """Klasörü siler."""
    if not os.path.isdir(folder_path):
        raise ResourceNotFoundError(
            resource_type="folder",
            resource_path=folder_path
        )
    
    try:
        shutil.rmtree(folder_path)
    except FileNotFoundError:
        raise ResourceNotFoundError(
            resource_type="folder",
            resource_path=folder_path
        )
    except Exception:
        raise InternalServiceError(
            service_name="file_helper",
            message="Folder deletion failed"
        )


# ============================================
# FILE CRUD OPERATIONS
# ============================================

def create_file(uploaded_file: Union[BinaryIO, TextIO], file_path: str) -> Tuple[int, float]:
    """Dosya oluşturur (streaming, memory-safe)."""
    directory = os.path.dirname(file_path)
    if directory:
        ensure_directory(directory)

    file_size = 0
    temp_file_path = file_path + '.tmp'
    
    try:
        with open(temp_file_path, 'wb') as f:
            chunk_size = 8192
            while True:
                chunk = uploaded_file.read(chunk_size)
                if not chunk:
                    break
                if isinstance(chunk, str):
                    chunk = chunk.encode('utf-8')
                
                file_size += len(chunk)
                f.write(chunk)
        
        try:
            os.chmod(temp_file_path, 0o600)
        except (OSError, PermissionError):
            pass
        
        try:
            os.rename(temp_file_path, file_path)
        except (OSError, PermissionError):
            shutil.copy2(temp_file_path, file_path)
            os.remove(temp_file_path)
    
    except Exception:
        _cleanup_temp_file(temp_file_path)
        raise InvalidInputError(
            field_name="file_path",
            message="File could not be created"
        )
    
    size_kb = file_size / 1024
    return file_size, size_kb


def create_file_with_content(content: str, file_path: str) -> Tuple[int, float]:
    """String içerik ile dosya oluşturur."""
    if not content:
        raise InvalidInputError(
            field_name="content",
            message="Content cannot be empty"
        )
    
    content_bytes = content.encode('utf-8')
    file_size = len(content_bytes)
    _atomic_file_write(content_bytes, file_path, is_binary=True)
    
    size_kb = file_size / 1024
    return file_size, size_kb


def read_file(file_path: str, max_size: Optional[int] = None) -> bytes:
    """Dosya içeriğini okur (opsiyonel boyut limiti ile)."""
    if not os.path.exists(file_path):
        raise ResourceNotFoundError(
            resource_type="file",
            resource_path=file_path
        )
    
    file_size = os.path.getsize(file_path)
    
    if max_size is None and file_size > 100 * 1024 * 1024:  # 100MB
        raise InvalidInputError(
            field_name="file_path",
            message=f"File too large ({file_size / 1024 / 1024:.2f} MB). Use max_size parameter or streaming."
        )
    
    if max_size is not None and file_size > max_size:
        raise InvalidInputError(
            field_name="file_path",
            message=f"File size ({file_size} bytes) exceeds max_size ({max_size} bytes)"
        )
    
    with open(file_path, 'rb') as f:
        return f.read()


def delete_file(file_path: str) -> None:
    """Dosyayı siler."""
    if not os.path.isfile(file_path):
        raise ResourceNotFoundError(
            resource_type="file",
            resource_path=file_path
        )
    
    try:
        os.remove(file_path)
    except FileNotFoundError:
        raise ResourceNotFoundError(
            resource_type="file",
            resource_path=file_path
        )
    except Exception:
        raise InternalServiceError(
            service_name="file_helper",
            message="File deletion failed"
        )


def generate_unique_filename(original_filename: str, workspace_id: str) -> str:
    """Benzersiz dosya adı üretir."""
    name, ext = os.path.splitext(original_filename)
    unique_id = str(uuid.uuid4().hex[:16])
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    name = sanitize_filename(name)
    
    safe_workspace_id = sanitize_filename(workspace_id)
    if not safe_workspace_id or safe_workspace_id in (".", ".."):
        safe_workspace_id = "workspace"

    fixed_length = len(timestamp) + 1 + len(safe_workspace_id) + 1 + len(unique_id) + 1
    available_length = MAX_FILENAME_LENGTH - fixed_length - len(ext)

    if available_length > 0 and len(name) > available_length:
        name = name[:available_length]

    new_name = f"{timestamp}_{safe_workspace_id}_{unique_id}_{name}{ext}"
    new_name = sanitize_filename(new_name)

    if ext and not new_name.endswith(ext):
        if len(new_name) + len(ext) <= MAX_FILENAME_LENGTH:
            new_name = new_name + ext
        else:
            truncate_length = MAX_FILENAME_LENGTH - len(ext)
            new_name = new_name[:truncate_length] + ext
    
    return new_name


# ============================================
# MIME TYPE DETECTION
# ============================================

def _detect_zip_mime_type(content: bytes) -> str:
    """ZIP dosyasından MIME type tespit eder."""
    try:
        zip_buffer = io.BytesIO(content)
        with zipfile.ZipFile(zip_buffer, 'r') as zip_file:
            namelist = zip_file.namelist()
            
            # Word document check
            if any('word/' in name.lower() for name in namelist) or \
               any('[Content_Types].xml' in name for name in namelist):
                if any(name.endswith('.xml') and 'word' in name.lower() for name in namelist):
                    return 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            
            # Excel check
            if any('xl/' in name.lower() for name in namelist) or \
               any('worksheets/' in name.lower() for name in namelist):
                return 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            
            # PowerPoint check
            if any('ppt/' in name.lower() for name in namelist):
                return 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
            
            return 'application/zip'
    except (zipfile.BadZipFile, Exception):
        return 'application/zip'


def _detect_mime_type_from_content(content: bytes) -> Optional[str]:
    """Magic bytes ile MIME type tespit eder."""
    if not content or len(content) < 4:
        return None
    
    signatures = {
        b'\xFF\xD8\xFF': 'image/jpeg',
        b'\x89PNG\r\n\x1a\n': 'image/png',
        b'GIF87a': 'image/gif',
        b'GIF89a': 'image/gif',
        b'BM': 'image/bmp',
        b'<svg': 'image/svg+xml',
        b'%PDF': 'application/pdf',
        b'PK\x03\x04': 'application/zip',
        b'\xd0\xcf\x11\xe0': 'application/msword',
        b'\x1f\x8b': 'application/gzip',
        b'ID3': 'audio/mpeg',
        b'\x00\x00\x00\x18ftyp': 'video/mp4',
        b'\x1a\x45\xdf\xa3': 'video/x-matroska',
    }
    
    header = content[:512]
    
    for signature, mime_type in signatures.items():
        if header.startswith(signature):
            if signature == b'PK\x03\x04':
                return _detect_zip_mime_type(content)
            return mime_type
    
    return None


# ============================================
# FILE UPLOAD
# ============================================

def upload_file(
    uploaded_file: Union[BinaryIO, TextIO],
    workspace_id: str,
    max_file_size_mb: Optional[int] = None,
    allowed_extensions: Optional[Set[str]] = None,
    blocked_extensions: Optional[Set[str]] = None,
    allowed_mime_types: Optional[Set[str]] = None,
    quota_limit_mb: Optional[int] = None
) -> UploadResult:
    """
    Dosya yükler ve doğrular.
    
    Args:
        uploaded_file: Dosya objesi
        workspace_id: Workspace ID
        max_file_size_mb: Maksimum dosya boyutu (MB)
        allowed_extensions: İzin verilen uzantılar
        blocked_extensions: Engellenen uzantılar
        allowed_mime_types: İzin verilen MIME tipleri
        quota_limit_mb: Workspace quota limiti (MB)
    
    Returns:
        UploadResult: Dosya bilgileri
    """
    try:
        ConfigurationHandler.load_config()
    except Exception:
        pass
    
    original_filename = getattr(uploaded_file, 'filename', None) or "unknown"
    if original_filename == "unknown":
        raise InvalidInputError(
            field_name="file",
            message="File name not found"
        )

    if max_file_size_mb is None:
        max_file_size_mb = ConfigurationHandler.get_value_as_int(
            "FILE OPERATIONS", "max_file_size_mb", None
        )
    max_file_size_bytes = (max_file_size_mb * 1024 * 1024) if max_file_size_mb and max_file_size_mb > 0 else None

    file_size = 0
    magic_bytes: Optional[bytes] = None
    temp_file_path: Optional[str] = None

    try:
        # Seek to beginning if possible
        if hasattr(uploaded_file, 'seek'):
            try:
                uploaded_file.seek(0)
            except (AttributeError, OSError):
                pass

        # Read first chunk for magic bytes
        first_chunk = uploaded_file.read(512)
        if not first_chunk:
            raise InvalidInputError(
                field_name="file",
                message="File is empty"
            )

        if isinstance(first_chunk, bytes):
            magic_bytes = first_chunk
            file_size = len(first_chunk)
        else:
            magic_bytes = first_chunk.encode('utf-8')
            file_size = len(magic_bytes)
        
        # Streaming write to temp file
        chunk_size = 8192
        workspace_file_path = get_workspace_file_path(workspace_id)
        ensure_directory(workspace_file_path)
        temp_file_path = os.path.join(workspace_file_path, f".tmp_{uuid.uuid4().hex}")
        
        with open(temp_file_path, 'wb') as temp_file:
            if isinstance(first_chunk, bytes):
                temp_file.write(first_chunk)
            else:
                temp_file.write(first_chunk.encode('utf-8'))
            
            while True:
                chunk = uploaded_file.read(chunk_size)
                if not chunk:
                    break
                
                if isinstance(chunk, str):
                    chunk = chunk.encode('utf-8')
                
                file_size += len(chunk)
                
                if max_file_size_bytes and file_size > max_file_size_bytes:
                    _cleanup_temp_file(temp_file_path)
                    raise InvalidInputError(
                        field_name="file",
                        message=f"File size limit exceeded. Maximum: {max_file_size_mb} MB"
                    )
                
                temp_file.write(chunk)
        
    except InvalidInputError:
        _cleanup_temp_file(temp_file_path)
        raise
    except Exception:
        _cleanup_temp_file(temp_file_path)
        raise InvalidInputError(
            field_name="file",
            message="File could not be read"
        )

    if file_size == 0:
        _cleanup_temp_file(temp_file_path)
        raise InvalidInputError(
            field_name="file",
            message="Empty files cannot be uploaded"
        )
    
    # Quota check
    has_space, remaining = check_workspace_quota(workspace_id, file_size, quota_limit_mb)
    if not has_space:
        _cleanup_temp_file(temp_file_path)
        raise InvalidInputError(
            field_name="file",
            message=f"Workspace quota exceeded. Remaining space: {remaining / 1024 / 1024:.2f} MB, Required: {file_size / 1024 / 1024:.2f} MB"
        )
    
    # Filename sanitization
    sanitized_name = sanitize_filename(original_filename)
    original_ext = os.path.splitext(original_filename)[1]
    if original_ext and not sanitized_name.endswith(original_ext.lower()):
        sanitized_name = sanitized_name + original_ext.lower()
    
    extension_with_case = os.path.splitext(sanitized_name)[1]
    extension = extension_with_case.lower()
    if not extension:
        _cleanup_temp_file(temp_file_path)
        raise InvalidInputError(
            field_name="filename",
            message="File extension not found"
        )
    
    # MIME type detection
    mime_type_from_content: Optional[str] = None
    if magic_bytes and len(magic_bytes) >= 4:
        mime_type_from_content = _detect_mime_type_from_content(magic_bytes)
    
    mime_type_from_extension, _ = mimetypes.guess_type(sanitized_name)
    if not mime_type_from_extension:
        mime_type_from_extension = mimetypes.types_map.get(extension, "application/octet-stream")
    
    # MIME type mismatch check
    if mime_type_from_content and mime_type_from_extension:
        content_mime = mime_type_from_content.lower().split(';')[0].strip()
        extension_mime = mime_type_from_extension.lower().split(';')[0].strip()
        
        if content_mime != extension_mime:
            _cleanup_temp_file(temp_file_path)
            raise InvalidInputError(
                field_name="file",
                message=f"MIME type mismatch detected. Content type: {mime_type_from_content}, Extension type: {mime_type_from_extension}. File rejected for security."
            )
        mime_type = mime_type_from_content
    else:
        mime_type = mime_type_from_content or mime_type_from_extension
    
    # Load default configurations
    if allowed_extensions is None:
        allowed_extensions_list = ConfigurationHandler.get_value_as_list(
            "FILE OPERATIONS", "allowed_extensions", []
        )
        allowed_extensions = {ext.strip().lower() for ext in allowed_extensions_list}
    
    if blocked_extensions is None:
        blocked_extensions_list = ConfigurationHandler.get_value_as_list(
            "FILE OPERATIONS", "blocked_extensions", []
        )
        blocked_extensions = {ext.strip().lower() for ext in blocked_extensions_list}
    
    if allowed_mime_types is None:
        allowed_mime_types_list = ConfigurationHandler.get_value_as_list(
            "FILE OPERATIONS", "allowed_mime_types", []
        )
        allowed_mime_types = {mime.strip().lower() for mime in allowed_mime_types_list}
    
    # Extension validation
    if allowed_extensions and extension not in allowed_extensions:
        _cleanup_temp_file(temp_file_path)
        raise InvalidInputError(
            field_name="file",
            message=f"File extension not allowed: {extension}"
        )
    
    if blocked_extensions and extension in blocked_extensions:
        _cleanup_temp_file(temp_file_path)
        raise InvalidInputError(
            field_name="file",
            message=f"File type blocked: {extension}"
        )
    
    # Multi-level extension check
    if blocked_extensions:
        parts = sanitized_name.split('.')
        if len(parts) > 1:
            for part in parts[:-1]:
                if part.lower() in blocked_extensions:
                    _cleanup_temp_file(temp_file_path)
                    raise InvalidInputError(
                        field_name="file",
                        message=f"Suspicious file extension detected at multiple levels: {part}"
                    )
    
    # MIME type validation
    if allowed_mime_types and mime_type.lower() not in allowed_mime_types:
        _cleanup_temp_file(temp_file_path)
        raise InvalidInputError(
            field_name="file",
            message=f"File type not allowed: {mime_type}"
        )
    
    # Generate unique filename
    unique_filename = generate_unique_filename(sanitized_name, workspace_id)
    
    # Final file path
    file_path_obj = Path(workspace_file_path) / unique_filename
    _validate_path_traversal(file_path_obj, Path(workspace_file_path))
    file_path = str(file_path_obj.resolve())
    
    # Atomic rename from temp to final
    try:
        try:
            os.chmod(temp_file_path, 0o600)
        except (OSError, PermissionError):
            pass
        
        try:
            os.rename(temp_file_path, file_path)
        except (OSError, PermissionError):
            shutil.copy2(temp_file_path, file_path)
            os.remove(temp_file_path)
        
    except OSError as e:
        _cleanup_temp_file(temp_file_path)
        error_code = getattr(e, 'errno', None)
        if error_code == 28:
            raise InvalidInputError(
                field_name="file",
                message="Disk quota exceeded or no space left on device"
            )
        elif error_code == 122:
            raise InvalidInputError(
                field_name="file",
                message="Disk quota exceeded"
            )
        else:
            raise InvalidInputError(
                field_name="file",
                message="File system error occurred"
            )
    except Exception:
        _cleanup_temp_file(temp_file_path)
        raise InvalidInputError(
            field_name="file",
            message="File could not be saved"
        )
    
    return {
        "file_path": file_path,
        "file_size": file_size,
        "mime_type": mime_type,
        "extension": extension,
        "file_name": unique_filename
    }


# ============================================
# SCRIPT UPLOAD
# ============================================

def upload_custom_script(
    content: str,
    script_name: str,
    extension: str,
    workspace_id: str,
    category: Optional[str] = None,
    subcategory: Optional[str] = None,
    quota_limit_mb: Optional[int] = None
) -> UploadResult:
    """Custom script yükler."""
    try:
        ConfigurationHandler.load_config()
    except Exception:
        pass
    
    if not content:
        raise InvalidInputError(
            field_name="content",
            message="Content cannot be empty"
        )
    
    if not script_name:
        raise InvalidInputError(
            field_name="script_name",
            message="Script name cannot be empty"
        )
    
    if not extension:
        raise InvalidInputError(
            field_name="extension",
            message="Extension cannot be empty"
        )
    
    if not extension.startswith('.'):
        extension = '.' + extension
    
    extension_lower = extension.lower()
    
    # Extension validation
    allowed_script_extensions_list = ConfigurationHandler.get_value_as_list(
        "CUSTOM SCRIPTS", "allowed_script_extensions", [".py"]
    )
    allowed_script_extensions = {ext.strip().lower() for ext in allowed_script_extensions_list}
    
    if extension_lower not in allowed_script_extensions:
        raise InvalidInputError(
            field_name="extension",
            message=f"Script extension not allowed: {extension}. Allowed extensions: {', '.join(allowed_script_extensions)}"
        )
    
    # Size validation
    max_script_size_mb = ConfigurationHandler.get_value_as_int(
        "CUSTOM SCRIPTS", "max_script_size_mb", 1
    )
    max_script_size_bytes = max_script_size_mb * 1024 * 1024
    
    content_bytes = content.encode('utf-8')
    content_size = len(content_bytes)
    if content_size > max_script_size_bytes:
        raise InvalidInputError(
            field_name="content",
            message=f"Script size ({content_size / 1024 / 1024:.2f} MB) exceeds maximum allowed size ({max_script_size_mb} MB)"
        )
    
    # Quota check
    has_space, remaining = check_workspace_quota(workspace_id, content_size, quota_limit_mb)
    if not has_space:
        raise InvalidInputError(
            field_name="content",
            message=f"Workspace quota exceeded. Remaining space: {remaining / 1024 / 1024:.2f} MB, Required: {content_size / 1024 / 1024:.2f} MB"
        )
    
    # MIME type detection
    mime_type_from_extension, _ = mimetypes.guess_type(f"file{extension}")
    if not mime_type_from_extension:
        mime_type_from_extension = _SCRIPT_MIME_TYPE_MAP.get(extension_lower, 'text/plain')
    mime_type = mime_type_from_extension
    
    # Filename
    sanitized_script_name = sanitize_filename(script_name)
    filename = f"{sanitized_script_name}{extension}"
    
    if len(filename) > MAX_FILENAME_LENGTH:
        name_part = sanitized_script_name
        max_name_length = MAX_FILENAME_LENGTH - len(extension)
        if max_name_length > 0:
            filename = name_part[:max_name_length] + extension
        else:
            raise InvalidInputError(
                field_name="script_name",
                message=f"Filename too long (max {MAX_FILENAME_LENGTH} characters)"
            )
    
    # Build path
    workspace_script_path = get_workspace_custom_script_path(workspace_id)
    ensure_directory(workspace_script_path)
    
    if category:
        safe_category = sanitize_filename(category)
        workspace_script_path = os.path.join(workspace_script_path, safe_category)
        ensure_directory(workspace_script_path)
        if subcategory:
            safe_subcategory = sanitize_filename(subcategory)
            workspace_script_path = os.path.join(workspace_script_path, safe_subcategory)
            ensure_directory(workspace_script_path)
    
    file_path_obj = Path(workspace_script_path) / filename
    _validate_path_traversal(file_path_obj, Path(workspace_script_path))
    final_path_str = str(file_path_obj.resolve())
    
    # Atomic write
    _atomic_file_write(content, final_path_str, is_binary=False)
    
    return {
        "file_path": final_path_str,
        "file_size": content_size,
        "mime_type": mime_type,
        "extension": extension_lower,
        "file_name": filename
    }


def upload_global_script(
    content: str,
    script_name: str,
    extension: str,
    category: Optional[str] = None,
    subcategory: Optional[str] = None,
    quota_limit_mb: Optional[int] = None
) -> UploadResult:
    """
    Global script yükler.
    
    Args:
        content: Script içeriği
        script_name: Script adı
        extension: Dosya uzantısı
        category: Kategori (opsiyonel)
        subcategory: Alt kategori (opsiyonel)
        quota_limit_mb: Global scripts quota limiti (MB)
    
    Returns:
        UploadResult: Script dosya bilgileri
    """
    if not content:
        raise InvalidInputError(
            field_name="content",
            message="Content cannot be empty"
        )
    
    if not script_name:
        raise InvalidInputError(
            field_name="script_name",
            message="Script name cannot be empty"
        )
    
    if not extension:
        raise InvalidInputError(
            field_name="extension",
            message="Extension cannot be empty"
        )
    
    try:
        ConfigurationHandler.load_config()
    except Exception:
        pass
    
    if not extension.startswith('.'):
        extension = '.' + extension
    
    extension_lower = extension.lower()
    
    # Extension validation (optional)
    allowed_script_extensions_list = ConfigurationHandler.get_value_as_list(
        "GLOBAL SCRIPTS", "allowed_script_extensions", []
    )
    if allowed_script_extensions_list:
        allowed_script_extensions = {ext.strip().lower() for ext in allowed_script_extensions_list}
        if extension_lower not in allowed_script_extensions:
            raise InvalidInputError(
                field_name="extension",
                message=f"Script extension not allowed: {extension}. Allowed extensions: {', '.join(allowed_script_extensions)}"
            )
    
    # Size validation (optional)
    max_script_size_mb = ConfigurationHandler.get_value_as_int(
        "GLOBAL SCRIPTS", "max_script_size_mb", None
    )
    content_bytes = content.encode('utf-8')
    content_size = len(content_bytes)
    if max_script_size_mb:
        max_script_size_bytes = max_script_size_mb * 1024 * 1024
        if content_size > max_script_size_bytes:
            raise InvalidInputError(
                field_name="content",
                message=f"Script size ({content_size / 1024 / 1024:.2f} MB) exceeds maximum allowed size ({max_script_size_mb} MB)"
            )
    
    # Global scripts quota check (optional)
    if quota_limit_mb is not None:
        try:
            global_script_path = get_global_script_path()
            current_usage = get_folder_size(global_script_path)
            quota_limit_bytes = quota_limit_mb * 1024 * 1024
            
            if current_usage + content_size > quota_limit_bytes:
                raise InvalidInputError(
                    field_name="content",
                    message=f"Global scripts quota exceeded. Remaining space: {(quota_limit_bytes - current_usage) / 1024 / 1024:.2f} MB, Required: {content_size / 1024 / 1024:.2f} MB"
                )
        except ResourceNotFoundError:
            quota_limit_bytes = quota_limit_mb * 1024 * 1024
            if content_size > quota_limit_bytes:
                raise InvalidInputError(
                    field_name="content",
                    message=f"Global scripts quota exceeded. Required: {content_size / 1024 / 1024:.2f} MB, Limit: {quota_limit_mb} MB"
                )
    
    # MIME type detection
    mime_type_from_extension, _ = mimetypes.guess_type(f"file{extension}")
    if not mime_type_from_extension:
        mime_type_from_extension = _SCRIPT_MIME_TYPE_MAP.get(extension_lower, 'text/plain')
    mime_type = mime_type_from_extension
    
    # MIME type validation (optional)
    allowed_script_mime_types_list = ConfigurationHandler.get_value_as_list(
        "GLOBAL SCRIPTS", "allowed_script_mime_types", []
    )
    if allowed_script_mime_types_list:
        allowed_script_mime_types = {mime.strip().lower() for mime in allowed_script_mime_types_list}
        if mime_type.lower() not in allowed_script_mime_types:
            raise InvalidInputError(
                field_name="extension",
                message=f"Script MIME type not allowed: {mime_type}. Allowed MIME types: {', '.join(allowed_script_mime_types)}"
            )
    
    # Filename
    sanitized_script_name = sanitize_filename(script_name)
    filename = f"{sanitized_script_name}{extension}"
    
    if len(filename) > MAX_FILENAME_LENGTH:
        name_part = sanitized_script_name
        max_name_length = MAX_FILENAME_LENGTH - len(extension)
        if max_name_length > 0:
            filename = name_part[:max_name_length] + extension
        else:
            raise InvalidInputError(
                field_name="script_name",
                message=f"Filename too long (max {MAX_FILENAME_LENGTH} characters)"
            )
    
    # Build path
    global_script_path = get_global_script_path()
    ensure_directory(global_script_path)
    
    if category:
        safe_category = sanitize_filename(category)
        global_script_path = os.path.join(global_script_path, safe_category)
        ensure_directory(global_script_path)
        if subcategory:
            safe_subcategory = sanitize_filename(subcategory)
            global_script_path = os.path.join(global_script_path, safe_subcategory)
            ensure_directory(global_script_path)
    
    file_path_obj = Path(global_script_path) / filename
    _validate_path_traversal(file_path_obj, Path(global_script_path))
    final_path_str = str(file_path_obj.resolve())
    
    # Atomic write
    _atomic_file_write(content, final_path_str, is_binary=False)
    
    return {
        "file_path": final_path_str,
        "file_size": content_size,
        "mime_type": mime_type,
        "extension": extension_lower,
        "file_name": filename
    }