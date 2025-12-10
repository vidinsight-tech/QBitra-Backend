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
    

# DATABASE EXCEPTIONS
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
