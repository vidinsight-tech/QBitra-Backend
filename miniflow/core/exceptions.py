from enum import Enum
from typing import Optional, Dict, Any


class ErrorCode(Enum):
    # Database Errors (500/503)
    DATABASE_CONNECTION_ERROR = "DATABASE_CONNECTION_ERROR"                         # 503
    DATABASE_QUERY_ERROR = "DATABASE_QUERY_ERROR"                                   # 500
    DATABASE_TRANSACTION_ERROR = "DATABASE_TRANSACTION_ERROR"                       # 500
    DATABASE_SESSION_ERROR = "DATABASE_SESSION_ERROR"                               # 503
    DATABASE_ENGINE_ERROR = "DATABASE_ENGINE_ERROR"                                 # 503
    DATABASE_CONFIGURATION_ERROR = "DATABASE_CONFIGURATION_ERROR"                   # 500
    DATABASE_VALIDATION_ERROR = "DATABASE_VALIDATION_ERROR"                         # 400 (kullanıcı hatası)
    DATABASE_MIGRATION_ERROR = "DATABASE_MIGRATION_ERROR"                           # 500
    
    # Internal Service Errors (500)
    INTERNAL_SERVICE_ERROR = "INTERNAL_SERVICE_ERROR"                               # 500
    INTERNAL_SERVICE_NOT_INITIALIZED = "INTERNAL_SERVICE_NOT_INITIALIZED"           # 500
    INTERNAL_SERVICE_CONFIGURATION_ERROR = "INTERNAL_SERVICE_CONFIGURATION_ERROR"   # 500
    INTERNAL_SERVICE_VALIDATION_ERROR = "INTERNAL_SERVICE_VALIDATION_ERROR"         # 400
    INTERNAL_RESOURCE_NOT_FOUND = "INTERNAL_RESOURCE_NOT_FOUND"                     # 404
    
    # External Service Errors (502/503/504)
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"                                # 502
    EXTERNAL_SERVICE_UNAVAILABLE = "EXTERNAL_SERVICE_UNAVAILABLE"                   # 503
    EXTERNAL_SERVICE_TIMEOUT = "EXTERNAL_SERVICE_TIMEOUT"                           # 504
    EXTERNAL_SERVICE_AUTHENTICATION_ERROR = "EXTERNAL_SERVICE_AUTHENTICATION_ERROR" # 401
    EXTERNAL_SERVICE_RATE_LIMIT_ERROR = "EXTERNAL_SERVICE_RATE_LIMIT_ERROR"         # 429
    EXTERNAL_SERVICE_INVALID_RESPONSE = "EXTERNAL_SERVICE_INVALID_RESPONSE"         # 502



class AppException(Exception):
    def __init__(self, error_code: ErrorCode, error_message: str, error_details: Optional[Dict[str, Any]] = None):
        self.error_code = error_code
        self.error_message = error_message
        self.error_details = error_details
        super().__init__(self.error_message)

    def __str__(self):
        return f"Message: {self.error_message}"

    def to_dict(self):
        return {
            "error_code": self.error_code.value,
            "error_message": self.error_message,
            "error_details": self.error_details
        }
    

# ============================================
# DATABASE SERVICE EXCEPTIONS
# ============================================

class DatabaseConnectionError(AppException):
    def __init__(self, message: str = None):
        message = message or "Unable to establish a connection to the database. The service may be temporarily unavailable. Please try again later."
        super().__init__(ErrorCode.DATABASE_CONNECTION_ERROR, message)

class DatabaseQueryError(AppException):
    def __init__(self, message: str = None):
        message = message or "A database query operation failed. This may be due to invalid data or a temporary database issue. Please try again or contact support if the problem persists."
        super().__init__(ErrorCode.DATABASE_QUERY_ERROR, message)

class DatabaseTransactionError(AppException):
    def __init__(self, message: str = None):
        message = message or "A database transaction failed to complete. All changes have been rolled back. Please try again or contact support if the problem persists."
        super().__init__(ErrorCode.DATABASE_TRANSACTION_ERROR, message)

class DatabaseSessionError(AppException):
    def __init__(self, message: str = None):
        message = message or "A database session error occurred. The connection may have been lost or timed out. Please try again."
        super().__init__(ErrorCode.DATABASE_SESSION_ERROR, message)

class DatabaseEngineError(AppException):
    def __init__(self, message: str = None):
        message = message or "A critical database engine error occurred. The database service may be experiencing issues. Please try again later or contact support."
        super().__init__(ErrorCode.DATABASE_ENGINE_ERROR, message)

class DatabaseConfigurationError(AppException):
    def __init__(self, field_name: Dict[str, Any], message: str = None):
        message = message or "A database configuration error was detected. The database settings may be incorrect or incomplete. Please contact system administrator."
        super().__init__(ErrorCode.DATABASE_CONFIGURATION_ERROR, message, error_details={"config_field_name": field_name})


# Database Manager Exceptions
class DatabaseManagerNotInitializedError(AppException):
    def __init__(self, message: str = None):
        message = message or "DatabaseManager not initialized. Call initialize() first."
        super().__init__(ErrorCode.DATABASE_ENGINE_ERROR, message)


class DatabaseManagerAlreadyInitializedError(AppException):
    def __init__(self, message: str = None):
        message = message or "DatabaseManager already initialized. Use force_reinitialize=True to reinitialize."
        super().__init__(ErrorCode.DATABASE_ENGINE_ERROR, message)


# Database Decorator Exceptions
class DatabaseDecoratorManagerError(AppException):
    def __init__(self, decorator_name: str, message: str = None):
        message = message or f"DatabaseManager not initialized for decorator '{decorator_name}'. Call DatabaseManager().initialize(config) first."
        super().__init__(ErrorCode.DATABASE_ENGINE_ERROR, message, error_details={"decorator_name": decorator_name})


class DatabaseDecoratorSignatureError(AppException):
    def __init__(self, decorator_name: str, function_name: str, expected: str, received: str):
        message = f"Function '{function_name}' does not have required '{expected}' for decorator '{decorator_name}'. Received: {received}"
        super().__init__(ErrorCode.DATABASE_VALIDATION_ERROR, message, error_details={
            "decorator_name": decorator_name,
            "function_name": function_name,
            "expected": expected,
            "received": received
        })


# Database Migration Exceptions
class DatabaseMigrationError(AppException):
    def __init__(self, message: str = None, operation: str = None, original_error: Exception = None):
        message = message or "A database migration error occurred. The migration operation may have failed or the migration files may be invalid."
        error_details = {}
        if operation:
            error_details["operation"] = operation
        if original_error:
            error_details["original_error"] = str(original_error)
            error_details["original_error_type"] = type(original_error).__name__
        super().__init__(ErrorCode.DATABASE_MIGRATION_ERROR, message, error_details=error_details if error_details else None)


# ============================================
# INTERNAL SERVICE EXCEPTIONS
# ============================================

class InternalServiceError(AppException):
    """Internal servislerde genel hata (configuration, environment handlers)"""
    def __init__(self, service_name: str, message: str = None, error_details: Dict[str, Any] = None):
        message = message or f"An internal service error occurred in '{service_name}'. This is an internal system issue. Please contact system administrator."
        super().__init__(
            ErrorCode.INTERNAL_SERVICE_ERROR, 
            message,
            error_details={"service_name": service_name, **(error_details or {})}
        )


class InternalServiceNotInitializedError(AppException):
    """Internal servis başlatılmamış"""
    def __init__(self, service_name: str, message: str = None):
        message = message or f"Internal service '{service_name}' is not initialized. Please call initialize() method first."
        super().__init__(
            ErrorCode.INTERNAL_SERVICE_NOT_INITIALIZED,
            message,
            error_details={"service_name": service_name}
        )


class InternalServiceConfigurationError(AppException):
    """Internal servis konfigürasyon hatası"""
    def __init__(self, service_name: str, config_path: str = None, message: str = None, error_details: Dict[str, Any] = None):
        message = message or f"Configuration error in internal service '{service_name}'. Configuration file may be missing, corrupted, or contains invalid values."
        details = {"service_name": service_name}
        if config_path:
            details["config_path"] = config_path
        if error_details:
            details.update(error_details)
        super().__init__(
            ErrorCode.INTERNAL_SERVICE_CONFIGURATION_ERROR,
            message,
            error_details=details
        )


class InternalServiceValidationError(AppException):
    """Internal servis validasyon hatası"""
    def __init__(self, service_name: str, validation_field: str = None, expected_value: Any = None, actual_value: Any = None, message: str = None):
        message = message or f"Validation failed in internal service '{service_name}'. The service configuration does not meet the required criteria."
        error_details = {
            "service_name": service_name,
            "validation_field": validation_field,
            "expected_value": str(expected_value) if expected_value is not None else None,
            "actual_value": str(actual_value) if actual_value is not None else None
        }
        super().__init__(
            ErrorCode.INTERNAL_SERVICE_VALIDATION_ERROR,
            message,
            error_details=error_details
        )


class ResourceNotFoundError(AppException):
    """Internal kaynak bulunamadı (dosya, config vb.)"""
    def __init__(self, resource_type: str = None, resource_path: str = None, service_name: str = None, message: str = None):
        if message is None:
            if resource_type:
                message = f"Required resource '{resource_type}' not found. The resource may have been moved, deleted, or the path is incorrect."
            else:
                message = "Required resource not found. The resource may have been moved, deleted, or the path is incorrect."
        error_details = {}
        if resource_type:
            error_details["resource_type"] = resource_type
        if resource_path:
            error_details["resource_path"] = resource_path
        if service_name:
            error_details["service_name"] = service_name
        super().__init__(
            ErrorCode.INTERNAL_RESOURCE_NOT_FOUND,
            message,
            error_details=error_details if error_details else None
        )


class InternalError(AppException):
    """Internal servis genel hata (geriye dönük uyumluluk için)"""
    def __init__(self, component_name: str = None, message: str = None, error_details: Dict[str, Any] = None):
        message = message or f"An internal error occurred in component '{component_name or 'unknown'}'. This is an internal system issue."
        details = {}
        if component_name:
            details["component_name"] = component_name
        if error_details:
            details.update(error_details)
        super().__init__(
            ErrorCode.INTERNAL_SERVICE_ERROR,
            message,
            error_details=details if details else None
        )


# ============================================
# EXTERNAL SERVICE EXCEPTIONS
# ============================================

class ExternalServiceError(AppException):
    """External servislerde genel hata (mailtrap, email providers)"""
    def __init__(self, service_name: str, service_type: str = None, message: str = None, error_details: Dict[str, Any] = None):
        message = message or f"An error occurred while communicating with external service '{service_name}'. The service may be experiencing issues."
        details = {"service_name": service_name}
        if service_type:
            details["service_type"] = service_type
        if error_details:
            details.update(error_details)
        super().__init__(
            ErrorCode.EXTERNAL_SERVICE_ERROR,
            message,
            error_details=details
        )


class ExternalServiceUnavailableError(AppException):
    """External servis kullanılamıyor"""
    def __init__(self, service_name: str, service_type: str = None, retry_after: int = None, message: str = None):
        message = message or f"External service '{service_name}' is currently unavailable. The service may be down for maintenance or experiencing issues. Please try again later."
        error_details = {
            "service_name": service_name,
            "service_type": service_type,
            "retry_after_seconds": retry_after
        }
        super().__init__(
            ErrorCode.EXTERNAL_SERVICE_UNAVAILABLE,
            message,
            error_details=error_details
        )


class ExternalServiceTimeoutError(AppException):
    """External servis timeout"""
    def __init__(self, service_name: str, timeout_seconds: int = None, service_type: str = None, message: str = None):
        message = message or f"Request to external service '{service_name}' timed out. The service may be overloaded or experiencing network issues."
        error_details = {
            "service_name": service_name,
            "service_type": service_type,
            "timeout_seconds": timeout_seconds
        }
        super().__init__(
            ErrorCode.EXTERNAL_SERVICE_TIMEOUT,
            message,
            error_details=error_details
        )


class ExternalServiceAuthenticationError(AppException):
    """External servis kimlik doğrulama hatası"""
    def __init__(self, service_name: str, service_type: str = None, message: str = None):
        message = message or f"Authentication failed for external service '{service_name}'. Please check your API credentials and ensure they are valid and have not expired."
        super().__init__(
            ErrorCode.EXTERNAL_SERVICE_AUTHENTICATION_ERROR,
            message,
            error_details={"service_name": service_name, "service_type": service_type}
        )


class ExternalServiceRateLimitError(AppException):
    """External servis rate limit hatası"""
    def __init__(self, service_name: str, retry_after: int = None, service_type: str = None, message: str = None):
        message = message or f"Rate limit exceeded for external service '{service_name}'. Too many requests have been made. Please wait before retrying."
        error_details = {
            "service_name": service_name,
            "service_type": service_type,
            "retry_after_seconds": retry_after
        }
        super().__init__(
            ErrorCode.EXTERNAL_SERVICE_RATE_LIMIT_ERROR,
            message,
            error_details=error_details
        )


class ExternalServiceInvalidResponseError(AppException):
    """External servis geçersiz yanıt"""
    def __init__(self, service_name: str, response_status: int = None, response_body: str = None, service_type: str = None, message: str = None):
        message = message or f"External service '{service_name}' returned an invalid or unexpected response. The service may have changed its API or returned malformed data."
        error_details = {
            "service_name": service_name,
            "service_type": service_type,
            "response_status": response_status,
            "response_body_preview": response_body[:500] if response_body else None  # İlk 500 karakter
        }
        super().__init__(
            ErrorCode.EXTERNAL_SERVICE_INVALID_RESPONSE,
            message,
            error_details=error_details
        )
