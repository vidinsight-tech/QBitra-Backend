"""
Database Engine testleri için fixture'lar.
"""

import pytest
import tempfile
import os
from pathlib import Path
from typing import Generator

from miniflow.database.config.database_type import DatabaseType
from miniflow.database.config.database_config import DatabaseConfig
from miniflow.database.config.engine_config import EngineConfig
from miniflow.database.engine.engine import DatabaseEngine
from miniflow.database.engine.manager import DatabaseManager


# --- SQLite Konfigürasyon Fixture'ları ---
@pytest.fixture
def sqlite_config_memory() -> DatabaseConfig:
    """SQLite bellek içi veritabanı konfigürasyonu sağlayan fixture."""
    return DatabaseConfig(
        db_type=DatabaseType.SQLITE,
        sqlite_path=":memory:"
    )


@pytest.fixture
def sqlite_config_file() -> DatabaseConfig:
    """SQLite dosya tabanlı veritabanı konfigürasyonu sağlayan fixture."""
    return DatabaseConfig(
        db_type=DatabaseType.SQLITE,
        sqlite_path="./test.db"
    )


@pytest.fixture
def temp_db_file() -> Generator[str, None, None]:
    """Geçici SQLite veritabanı dosya yolu sağlayan fixture."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
        db_path = tmp_file.name
    
    yield db_path
    
    # Temizlik
    if os.path.exists(db_path):
        os.unlink(db_path)


# --- PostgreSQL Konfigürasyon Fixture'ları ---
@pytest.fixture
def postgresql_config_default() -> DatabaseConfig:
    """Varsayılan değerlerle PostgreSQL konfigürasyonu sağlayan fixture."""
    return DatabaseConfig(
        db_type=DatabaseType.POSTGRESQL,
        db_name="testdb",
        host="localhost",
        port=5432,
        username="postgres",
        password="testpass"
    )


# --- MySQL Konfigürasyon Fixture'ları ---
@pytest.fixture
def mysql_config_default() -> DatabaseConfig:
    """Varsayılan değerlerle MySQL konfigürasyonu sağlayan fixture."""
    return DatabaseConfig(
        db_type=DatabaseType.MYSQL,
        db_name="testdb",
        host="localhost",
        port=3306,
        username="root",
        password="testpass"
    )


# --- Engine Config Fixture'ları ---
@pytest.fixture
def engine_config_minimal() -> EngineConfig:
    """Minimal EngineConfig sağlayan fixture (test için küçük pool boyutları)."""
    return EngineConfig(
        pool_size=1,
        max_overflow=0,
        pool_timeout=5,
        pool_recycle=0,
        pool_pre_ping=False
    )


# --- DatabaseEngine Fixture'ları ---
@pytest.fixture
def database_engine_not_started(sqlite_config_memory) -> DatabaseEngine:
    """Başlatılmamış DatabaseEngine sağlayan fixture."""
    return DatabaseEngine(sqlite_config_memory)


@pytest.fixture
def database_engine_started(sqlite_config_memory) -> Generator[DatabaseEngine, None, None]:
    """Başlatılmış DatabaseEngine sağlayan fixture.
    
    Test sonunda otomatik olarak engine durdurulur ve temizlenir.
    """
    engine = DatabaseEngine(sqlite_config_memory)
    engine.start()
    
    yield engine
    
    # Temizlik
    try:
        engine.stop()
    except Exception:
        pass


# --- DatabaseManager Fixture'ları ---
@pytest.fixture
def database_manager_not_initialized() -> DatabaseManager:
    """Başlatılmamış DatabaseManager sağlayan fixture.
    
    Test sonunda otomatik olarak manager sıfırlanır.
    """
    # Singleton'ı sıfırla
    DatabaseManager._instance = None
    DatabaseManager._is_resetting = False
    
    manager = DatabaseManager()
    
    yield manager
    
    # Temizlik
    try:
        manager.reset(full_reset=True)
    except Exception:
        pass


@pytest.fixture
def database_manager_initialized(sqlite_config_memory) -> Generator[DatabaseManager, None, None]:
    """Başlatılmış DatabaseManager sağlayan fixture.
    
    Test sonunda otomatik olarak manager sıfırlanır.
    """
    # Singleton'ı sıfırla
    DatabaseManager._instance = None
    DatabaseManager._is_resetting = False
    
    manager = DatabaseManager()
    manager.initialize(sqlite_config_memory, auto_start=True)
    
    yield manager
    
    # Temizlik
    try:
        manager.reset(full_reset=True)
    except Exception:
        pass

