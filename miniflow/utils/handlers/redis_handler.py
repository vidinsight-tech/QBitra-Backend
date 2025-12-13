import json
import threading
from typing import Optional, Any, List

import redis
from redis.connection import ConnectionPool
from redis.exceptions import (
    ConnectionError as RedisConnectionError,
    TimeoutError as RedisTimeoutError,
    AuthenticationError as RedisAuthenticationError,
    ResponseError as RedisResponseError,
)

from miniflow.utils.handlers.configuration_handler import ConfigurationHandler
from miniflow.core.exceptions import (
    ExternalServiceError,
    ExternalServiceTimeoutError,
    ExternalServiceAuthenticationError,
    ExternalServiceUnavailableError,
    
)


class RedisHandler:
    """Thread-safe singleton pattern ile Redis bağlantı yönetimi sağlayan handler sınıfı."""
    
    # Class variables for singleton pattern
    _initialized: bool = False
    _lock: threading.RLock = threading.RLock()  # Reentrant lock for better thread safety
    _pool: Optional[ConnectionPool] = None
    _client: Optional[redis.Redis] = None
    
    # Configuration
    _host: str = "localhost"
    _port: int = 6379
    _db: int = 0
    _password: Optional[str] = None
    _max_connections: int = 50
    _socket_timeout: int = 5
    _socket_connect_timeout: int = 5
    _decode_responses: bool = True
    _retry_on_timeout: bool = True
    _health_check_interval: int = 30
    
    @classmethod
    def initialize(cls, environment_name: str = "dev") -> None:
        """Redis bağlantı havuzu ve client'ı thread-safe şekilde başlatır."""
        if cls._initialized:
            return
        
        with cls._lock:
            # Double-check locking pattern
            if cls._initialized:
                return
            
            # Load configuration
            cls._load_configuration(environment_name)
            
            # Create connection pool
            cls._create_pool()
            
            # Create client and test connection
            cls._create_client()
            
            cls._initialized = True
    
    @classmethod
    def _load_configuration(cls, environment_name: str) -> None:
        """ConfigurationHandler'dan Redis konfigürasyonunu yükler."""
        ConfigurationHandler.load_config(environment_name)
        
        cls._host = ConfigurationHandler.get_value_as_str("REDIS", "host", "localhost")
        cls._port = ConfigurationHandler.get_value_as_int("REDIS", "port", 6379)
        cls._db = ConfigurationHandler.get_value_as_int("REDIS", "db", 0)
        cls._password = ConfigurationHandler.get_value_as_str("REDIS", "password", None)
        cls._max_connections = ConfigurationHandler.get_value_as_int("REDIS", "max_connections", 50)
        cls._socket_timeout = ConfigurationHandler.get_value_as_int("REDIS", "socket_timeout", 5)
        cls._socket_connect_timeout = ConfigurationHandler.get_value_as_int("REDIS", "socket_connect_timeout", 5)
        cls._decode_responses = ConfigurationHandler.get_value_as_bool("REDIS", "decode_responses", True)
        cls._retry_on_timeout = ConfigurationHandler.get_value_as_bool("REDIS", "retry_on_timeout", True)
        cls._health_check_interval = ConfigurationHandler.get_value_as_int("REDIS", "health_check_interval", 30)
    
    @classmethod
    def _create_pool(cls) -> None:
        """Redis bağlantı havuzu oluşturur."""
        cls._pool = ConnectionPool(
            host=cls._host,
            port=cls._port,
            db=cls._db,
            password=cls._password,
            max_connections=cls._max_connections,
            socket_timeout=cls._socket_timeout,
            socket_connect_timeout=cls._socket_connect_timeout,
            decode_responses=cls._decode_responses,
            retry_on_timeout=cls._retry_on_timeout,
            health_check_interval=cls._health_check_interval,
        )
    
    @classmethod
    def _create_client(cls) -> None:
        """Redis client oluşturur ve bağlantıyı test eder."""
        try:
            cls._client = redis.Redis(connection_pool=cls._pool)
            cls._client.ping()
        except RedisAuthenticationError as e:
            raise ExternalServiceAuthenticationError(
                service_name="redis",
                service_type="cache",
                message=f"Redis authentication failed. Check password configuration. Host: {cls._host}:{cls._port}, Error: {str(e)}"
            )
        except RedisConnectionError as e:
            raise ExternalServiceUnavailableError(
                service_name="redis",
                service_type="cache",
                message=f"Failed to connect to Redis server at {cls._host}:{cls._port}: {str(e)}"
            )
        except RedisTimeoutError as e:
            raise ExternalServiceTimeoutError(
                service_name="redis",
                timeout_seconds=cls._socket_connect_timeout,
                service_type="cache",
                message=f"Redis connection timeout after {cls._socket_connect_timeout}s: {str(e)}"
            )
        except Exception as e:
            raise ExternalServiceError(
                service_name="redis",
                service_type="cache",
                message=f"Unexpected error during Redis initialization: {str(e)}",
                error_details={
                    "error_type": type(e).__name__,
                    "original_error": str(e),
                    "host": cls._host,
                    "port": cls._port
                }
            )
    
    @classmethod
    def _ensure_initialized(cls) -> None:
        """Handler'ın kullanımdan önce başlatıldığından emin olur."""
        if not cls._initialized:
            cls.initialize()
    
    @classmethod
    def _handle_error(cls, e: Exception, operation: str) -> None:
        """Redis exception'larını Miniflow exception'larına çevirir."""
        if isinstance(e, RedisAuthenticationError):
            raise ExternalServiceAuthenticationError(
                service_name="redis",
                service_type="cache",
                message=f"Redis authentication failed during {operation}: {str(e)}"
            )
        elif isinstance(e, RedisConnectionError):
            raise ExternalServiceUnavailableError(
                service_name="redis",
                service_type="cache",
                message=f"Redis connection lost during {operation}: {str(e)}"
            )
        elif isinstance(e, RedisTimeoutError):
            raise ExternalServiceTimeoutError(
                service_name="redis",
                timeout_seconds=cls._socket_timeout,
                service_type="cache",
                message=f"Redis operation '{operation}' timed out after {cls._socket_timeout}s: {str(e)}"
            )
        elif isinstance(e, RedisResponseError):
            raise ExternalServiceError(
                service_name="redis",
                service_type="cache",
                message=f"Redis response error during {operation}: {str(e)}",
                error_details={"operation": operation, "original_error": str(e)}
            )
        else:
            raise ExternalServiceError(
                service_name="redis",
                service_type="cache",
                message=f"Unexpected Redis error during {operation}: {str(e)}",
                error_details={"operation": operation, "error_type": type(e).__name__, "original_error": str(e)}
            )
    
    @classmethod
    def _serialize(cls, value: Any) -> str:
        """Değeri string'e çevirir (dict/list için JSON kullanır)."""
        if isinstance(value, (dict, list)):
            return json.dumps(value, ensure_ascii=False)
        return str(value)
    
    @classmethod
    def _deserialize(cls, value: Optional[str]) -> Optional[Any]:
        """String değeri parse eder (önce JSON dener)."""
        if value is None:
            return None
        
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value
    
    # ==================== Connection Management ====================
    
    @classmethod
    def close(cls) -> None:
        """Redis bağlantı havuzunu kapatır."""
        with cls._lock:
            if cls._pool:
                cls._pool.disconnect()
            cls._client = None
            cls._pool = None
            cls._initialized = False
    
    # ==================== Basic Operations ====================
    
    @classmethod
    def set(cls, key: str, value: Any, ex: Optional[int] = None, px: Optional[int] = None, nx: bool = False, xx: bool = False) -> bool:
        """Redis'te key-value çifti oluşturur (dict/list otomatik JSON'a çevrilir)."""
        cls._ensure_initialized()
        try:
            serialized = cls._serialize(value)
            result = cls._client.set(key, serialized, ex=ex, px=px, nx=nx, xx=xx)
            return bool(result)
        except Exception as e:
            cls._handle_error(e, "set")
    
    @classmethod
    def get(cls, key: str) -> Optional[Any]:
        """Redis'ten key'e göre değer alır (JSON ise otomatik deserialize edilir)."""
        cls._ensure_initialized()
        try:
            value = cls._client.get(key)
            return cls._deserialize(value)
        except Exception as e:
            cls._handle_error(e, "get")
    
    @classmethod
    def delete(cls, *keys: str) -> int:
        """Redis'ten bir veya daha fazla key siler ve silinen key sayısını döner."""
        cls._ensure_initialized()
        try:
            if not keys:
                return 0
            return cls._client.delete(*keys)
        except Exception as e:
            cls._handle_error(e, "delete")
    
    @classmethod
    def exists(cls, key: str) -> bool:
        """Redis'te key'in var olup olmadığını kontrol eder."""
        cls._ensure_initialized()
        try:
            return bool(cls._client.exists(key))
        except Exception as e:
            cls._handle_error(e, "exists")
    
    # ==================== Expiration Operations ====================
    
    @classmethod
    def expire(cls, key: str, seconds: int) -> bool:
        """Key için saniye cinsinden son kullanma süresi belirler."""
        cls._ensure_initialized()
        try:
            return cls._client.expire(key, seconds)
        except Exception as e:
            cls._handle_error(e, "expire")
    
    @classmethod
    def ttl(cls, key: str) -> int:
        """Key'in kalan yaşam süresini saniye cinsinden döner (-1 süre yoksa, -2 key yoksa)."""
        cls._ensure_initialized()
        try:
            return cls._client.ttl(key)
        except Exception as e:
            cls._handle_error(e, "ttl")
    
    # ==================== Atomic Operations ====================
    
    @classmethod
    def incr(cls, key: str, amount: int = 1) -> int:
        """Key'in değerini belirtilen miktar kadar artırır."""
        cls._ensure_initialized()
        try:
            return cls._client.incr(key, amount)
        except Exception as e:
            cls._handle_error(e, "incr")
    
    @classmethod
    def decr(cls, key: str, amount: int = 1) -> int:
        """Key'in değerini belirtilen miktar kadar azaltır."""
        cls._ensure_initialized()
        try:
            return cls._client.decr(key, amount)
        except Exception as e:
            cls._handle_error(e, "decr")
    
    # ==================== Multi-Key Operations ====================
    
    @classmethod
    def keys(cls, pattern: str = "*") -> List[str]:
        """Belirtilen pattern'e uyan tüm key'leri döner (production'da dikkatli kullanılmalı)."""
        cls._ensure_initialized()
        try:
            return cls._client.keys(pattern)
        except Exception as e:
            cls._handle_error(e, "keys")
    
    # ==================== Admin Operations ====================
    
    @classmethod
    def flushdb(cls) -> bool:
        """Mevcut veritabanındaki tüm key'leri siler (dikkatli kullanılmalı)."""
        cls._ensure_initialized()
        try:
            return cls._client.flushdb()
        except Exception as e:
            cls._handle_error(e, "flushdb")