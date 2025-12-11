"""
Integration testleri için fixture'lar - gerçek veritabanı bağlantıları.
"""

import os
import pytest
from typing import Generator, Optional
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

from miniflow.database.config.database_type import DatabaseType
from miniflow.database.config.database_config import DatabaseConfig
from miniflow.database.engine.engine import DatabaseEngine
from miniflow.database.engine.manager import DatabaseManager


# --- Environment Variable Helpers ---
def get_env_or_skip(env_var: str, default: Optional[str] = None) -> str:
    """Environment variable'dan değer alır, yoksa test'i skip eder."""
    value = os.getenv(env_var, default)
    if value is None:
        pytest.skip(f"Environment variable {env_var} not set. Skipping integration test.")
    return value


def check_database_connection(config: DatabaseConfig) -> bool:
    """Veritabanı bağlantısını kontrol eder, bağlanamazsa False döner."""
    try:
        from sqlalchemy import create_engine, text
        engine = create_engine(config.get_connection_string(), pool_pre_ping=True)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        engine.dispose()
        return True
    except Exception:
        return False


# --- PostgreSQL Fixtures ---
@pytest.fixture(scope="session")
def postgresql_config() -> DatabaseConfig:
    """PostgreSQL integration test konfigürasyonu."""
    import os
    # Homebrew PostgreSQL için sistem kullanıcı adını kullan
    default_user = os.getenv("USER", "postgres")
    return DatabaseConfig(
        db_type=DatabaseType.POSTGRESQL,
        db_name=get_env_or_skip("TEST_POSTGRES_DB", "testdb"),
        host=get_env_or_skip("TEST_POSTGRES_HOST", "localhost"),
        port=int(get_env_or_skip("TEST_POSTGRES_PORT", "5432")),
        username=get_env_or_skip("TEST_POSTGRES_USER", default_user),
        password=get_env_or_skip("TEST_POSTGRES_PASSWORD", "")
    )


@pytest.fixture(scope="session")
def postgresql_engine_started(postgresql_config) -> Generator[DatabaseEngine, None, None]:
    """Başlatılmış PostgreSQL DatabaseEngine."""
    # Veritabanı bağlantısını kontrol et
    admin_config = DatabaseConfig(
        db_type=DatabaseType.POSTGRESQL,
        db_name="postgres",  # Admin database
        host=postgresql_config.host,
        port=postgresql_config.port,
        username=postgresql_config.username,
        password=postgresql_config.password
    )
    
    if not check_database_connection(admin_config):
        pytest.skip("PostgreSQL server is not running or not accessible. Skipping integration test.")
    
    # Test database'i oluştur (eğer yoksa)
    try:
        admin_engine = create_engine(admin_config.get_connection_string())
        with admin_engine.connect() as conn:
            conn.execute(text("COMMIT"))  # Autocommit mode
            # PostgreSQL'de IF NOT EXISTS kullan
            conn.execute(text(f"CREATE DATABASE {postgresql_config.db_name}"))
        admin_engine.dispose()
    except OperationalError as e:
        # Database zaten var veya başka bir hata, devam et
        if "already exists" not in str(e).lower():
            raise
    except Exception as e:
        # DuplicateDatabase hatası da beklenen bir durum
        if "duplicate" not in str(e).lower() and "already exists" not in str(e).lower():
            raise
    
    # Engine oluştur ve başlat
    engine = DatabaseEngine(postgresql_config)
    engine.start()
    
    yield engine
    
    # Temizlik
    try:
        engine.stop()
    except Exception:
        pass


# --- MySQL Fixtures ---
@pytest.fixture(scope="session")
def mysql_config() -> DatabaseConfig:
    """MySQL integration test konfigürasyonu."""
    return DatabaseConfig(
        db_type=DatabaseType.MYSQL,
        db_name=get_env_or_skip("TEST_MYSQL_DB", "testdb"),
        host=get_env_or_skip("TEST_MYSQL_HOST", "localhost"),
        port=int(get_env_or_skip("TEST_MYSQL_PORT", "3306")),
        username=get_env_or_skip("TEST_MYSQL_USER", "root"),
        password=get_env_or_skip("TEST_MYSQL_PASSWORD", "root")
    )


@pytest.fixture(scope="session")
def mysql_engine_started(mysql_config) -> Generator[DatabaseEngine, None, None]:
    """Başlatılmış MySQL DatabaseEngine."""
    # Veritabanı bağlantısını kontrol et
    from sqlalchemy.engine import URL
    admin_url = URL.create(
        "mysql+pymysql",
        username=mysql_config.username,
        password=mysql_config.password,
        host=mysql_config.host,
        port=mysql_config.port
    )
    
    try:
        test_engine = create_engine(admin_url, pool_pre_ping=True)
        with test_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        test_engine.dispose()
    except Exception:
        pytest.skip("MySQL server is not running or not accessible. Skipping integration test.")
    
    # Test database'i oluştur (eğer yoksa)
    try:
        admin_engine = create_engine(admin_url)
        with admin_engine.connect() as conn:
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {mysql_config.db_name}"))
        admin_engine.dispose()
    except OperationalError:
        # Database zaten var veya oluşturulamadı, devam et
        pass
    
    # Engine oluştur ve başlat
    engine = DatabaseEngine(mysql_config)
    engine.start()
    
    yield engine
    
    # Temizlik
    try:
        engine.stop()
    except Exception:
        pass


# --- Test Table Fixtures ---
@pytest.fixture
def test_table_metadata():
    """Test için basit bir tablo metadata'sı."""
    from sqlalchemy import MetaData, Table, Column, Integer, String
    
    metadata = MetaData()
    Table(
        'test_users',
        metadata,
        Column('id', Integer, primary_key=True),
        Column('name', String(100)),
        Column('email', String(100))
    )
    return metadata

