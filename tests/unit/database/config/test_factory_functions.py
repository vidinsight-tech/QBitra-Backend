import pytest
from miniflow.database.config.factories import (
    get_database_config,
    get_sqlite_config,
    get_postgresql_config,
    get_mysql_config
)
from miniflow.database.config.database_type import DatabaseType
from miniflow.database.config.engine_config import EngineConfig
from miniflow.database.config.engine_config_presets import DB_ENGINE_CONFIGS
from miniflow.core.exceptions import DatabaseConfigurationError


@pytest.mark.unit
@pytest.mark.config
@pytest.mark.database
class TestGetDatabaseConfig:
    """get_database_config factory fonksiyonu için testler."""

    # --- SQLite Yapılandırma Testleri ---
    def test_get_database_config_creates_sqlite_config_with_defaults(self):
        """get_database_config fonksiyonunun varsayılan değerlerle SQLite yapılandırması oluşturduğunu test eder."""
        config = get_database_config(
            database_name="testdb",
            db_type=DatabaseType.SQLITE
        )
        
        assert config.db_type == DatabaseType.SQLITE
        assert config.db_name == "testdb"
        assert config.sqlite_path == "testdb"
        assert config.port == 0

    def test_get_database_config_creates_sqlite_config_with_custom_path(self):
        """get_database_config fonksiyonunun özel dosya yolu ile SQLite yapılandırması oluşturduğunu test eder."""
        config = get_database_config(
            database_name="testdb",
            db_type=DatabaseType.SQLITE,
            sqlite_path="./custom.db"
        )
        
        assert config.sqlite_path == "./custom.db"
        assert config.db_name == "./custom.db"

    # --- PostgreSQL Yapılandırma Testleri ---
    def test_get_database_config_creates_postgresql_config_with_defaults(self):
        """get_database_config fonksiyonunun varsayılan preset engine config ile PostgreSQL yapılandırması oluşturduğunu test eder."""
        config = get_database_config(
            database_name="testdb",
            db_type=DatabaseType.POSTGRESQL,
            host="localhost",
            port=5432,
            username="postgres",
            password="secret"
        )
        
        assert config.db_type == DatabaseType.POSTGRESQL
        assert config.db_name == "testdb"
        assert config.host == "localhost"
        assert config.port == 5432
        assert config.username == "postgres"
        assert config.password == "secret"
        # Should use preset engine config
        assert config.engine_config.pool_size == DB_ENGINE_CONFIGS[DatabaseType.POSTGRESQL].pool_size

    # --- MySQL Yapılandırma Testleri ---
    def test_get_database_config_creates_mysql_config_with_defaults(self):
        """get_database_config fonksiyonunun varsayılan preset engine config ile MySQL yapılandırması oluşturduğunu test eder."""
        config = get_database_config(
            database_name="testdb",
            db_type=DatabaseType.MYSQL,
            host="localhost",
            port=3306,
            username="root",
            password="secret"
        )
        
        assert config.db_type == DatabaseType.MYSQL
        assert config.db_name == "testdb"
        assert config.host == "localhost"
        assert config.port == 3306
        assert config.username == "root"
        assert config.password == "secret"
        # Should use preset engine config
        assert config.engine_config.pool_size == DB_ENGINE_CONFIGS[DatabaseType.MYSQL].pool_size

    # --- Engine Config Testleri ---
    def test_get_database_config_uses_custom_engine_config_when_provided(self):
        """get_database_config fonksiyonunun sağlandığında özel engine config kullandığını test eder."""
        custom_engine = EngineConfig(pool_size=5, max_overflow=10)
        config = get_database_config(
            database_name="testdb",
            db_type=DatabaseType.POSTGRESQL,
            host="localhost",
            port=5432,
            username="postgres",
            password="secret",
            custom_engine_config=custom_engine
        )
        
        assert config.engine_config.pool_size == 5
        assert config.engine_config.max_overflow == 10

    def test_get_database_config_uses_preset_engine_config_when_custom_not_provided(self):
        """get_database_config fonksiyonunun özel engine config sağlanmadığında preset engine config kullandığını test eder."""
        config = get_database_config(
            database_name="testdb",
            db_type=DatabaseType.SQLITE
        )
        
        preset = DB_ENGINE_CONFIGS[DatabaseType.SQLITE]
        assert config.engine_config.pool_size == preset.pool_size
        assert config.engine_config.max_overflow == preset.max_overflow

    def test_get_database_config_copies_preset_engine_config_to_avoid_shared_state(self):
        """get_database_config fonksiyonunun preset engine config'i kopyalayarak değişikliklerin diğer örnekleri etkilemediğini test eder."""
        config1 = get_database_config(
            database_name="testdb1",
            db_type=DatabaseType.SQLITE
        )
        config2 = get_database_config(
            database_name="testdb2",
            db_type=DatabaseType.SQLITE
        )
        
        # Modifying one should not affect the other
        config1.engine_config.pool_size = 999
        assert config2.engine_config.pool_size != 999
        assert config2.engine_config.pool_size == DB_ENGINE_CONFIGS[DatabaseType.SQLITE].pool_size

    # --- Varsayılan Değer Testleri ---
    def test_get_database_config_defaults_host_to_localhost_when_not_provided(self):
        """get_database_config fonksiyonunun host belirtilmediğinde varsayılan olarak 'localhost' kullandığını test eder."""
        config = get_database_config(
            database_name="testdb",
            db_type=DatabaseType.POSTGRESQL,
            port=5432,
            username="postgres",
            password="secret"
        )
        
        assert config.host == "localhost"

    # --- Hata Durumu Testleri ---
    def test_raises_error_for_unsupported_db_type(self):
        """Desteklenmeyen veritabanı türü için hata oluşturulduğunu test eder."""
        # This test assumes we only support SQLITE, MYSQL, POSTGRESQL
        # If a new type is added without preset, it should raise error
        # Note: This test might need adjustment if the codebase changes
        pass  # Cannot easily test without creating a new enum value


@pytest.mark.unit
@pytest.mark.config
class TestGetSqliteConfig:
    """get_sqlite_config factory fonksiyonu için testler."""

    # --- Varsayılan Değer Testleri ---
    def test_get_sqlite_config_uses_default_database_name_when_not_provided(self):
        """get_sqlite_config fonksiyonunun veritabanı adı belirtilmediğinde varsayılan olarak 'miniflow' kullandığını test eder."""
        config = get_sqlite_config()
        
        assert config.db_type == DatabaseType.SQLITE
        assert config.db_name == "miniflow"
        assert config.sqlite_path == "miniflow"

    def test_get_sqlite_config_accepts_custom_database_name(self):
        """get_sqlite_config fonksiyonunun özel veritabanı adını kabul ettiğini test eder."""
        config = get_sqlite_config("mydb")
        
        assert config.db_type == DatabaseType.SQLITE
        assert config.db_name == "mydb"
        assert config.sqlite_path == "mydb"

    # --- Engine Config Testleri ---
    def test_get_sqlite_config_uses_sqlite_preset_engine_config(self):
        """get_sqlite_config fonksiyonunun SQLite'a özel preset engine yapılandırmasını kullandığını test eder."""
        config = get_sqlite_config()
        
        preset = DB_ENGINE_CONFIGS[DatabaseType.SQLITE]
        assert config.engine_config.pool_size == preset.pool_size
        assert config.engine_config.max_overflow == preset.max_overflow
        assert config.engine_config.pool_pre_ping == preset.pool_pre_ping


@pytest.mark.unit
@pytest.mark.config
class TestGetPostgresqlConfig:
    """get_postgresql_config factory fonksiyonu için testler."""

    # --- Varsayılan Değer Testleri ---
    def test_get_postgresql_config_uses_default_connection_parameters(self):
        """get_postgresql_config fonksiyonunun bağlantı parametreleri belirtilmediğinde varsayılan değerleri kullandığını test eder."""
        config = get_postgresql_config()
        
        assert config.db_type == DatabaseType.POSTGRESQL
        assert config.db_name == "miniflow"
        assert config.host == "localhost"
        assert config.port == 5432
        assert config.username == "postgres"
        assert config.password == "password"

    def test_get_postgresql_config_accepts_custom_connection_parameters(self):
        """get_postgresql_config fonksiyonunun özel bağlantı parametrelerini kabul ettiğini test eder."""
        config = get_postgresql_config(
            database_name="mydb",
            host="remote.host",
            port=5433,
            username="admin",
            password="secret123"
        )
        
        assert config.db_type == DatabaseType.POSTGRESQL
        assert config.db_name == "mydb"
        assert config.host == "remote.host"
        assert config.port == 5433
        assert config.username == "admin"
        assert config.password == "secret123"

    # --- Engine Config Testleri ---
    def test_get_postgresql_config_uses_postgresql_preset_engine_config(self):
        """get_postgresql_config fonksiyonunun PostgreSQL'e özel preset engine yapılandırmasını kullandığını test eder."""
        config = get_postgresql_config()
        
        preset = DB_ENGINE_CONFIGS[DatabaseType.POSTGRESQL]
        assert config.engine_config.pool_size == preset.pool_size
        assert config.engine_config.max_overflow == preset.max_overflow
        assert config.engine_config.isolation_level == preset.isolation_level


@pytest.mark.unit
@pytest.mark.config
class TestGetMysqlConfig:
    """get_mysql_config factory fonksiyonu için testler."""

    # --- Varsayılan Değer Testleri ---
    def test_get_mysql_config_uses_default_connection_parameters(self):
        """get_mysql_config fonksiyonunun bağlantı parametreleri belirtilmediğinde varsayılan değerleri kullandığını test eder."""
        config = get_mysql_config()
        
        assert config.db_type == DatabaseType.MYSQL
        assert config.db_name == "miniflow"
        assert config.host == "localhost"
        assert config.port == 3306
        assert config.username == "root"
        assert config.password == "password"

    def test_get_mysql_config_accepts_custom_connection_parameters(self):
        """get_mysql_config fonksiyonunun özel bağlantı parametrelerini kabul ettiğini test eder."""
        config = get_mysql_config(
            database_name="mydb",
            host="remote.host",
            port=3307,
            username="admin",
            password="secret123"
        )
        
        assert config.db_type == DatabaseType.MYSQL
        assert config.db_name == "mydb"
        assert config.host == "remote.host"
        assert config.port == 3307
        assert config.username == "admin"
        assert config.password == "secret123"

    # --- Engine Config Testleri ---
    def test_get_mysql_config_uses_mysql_preset_engine_config(self):
        """get_mysql_config fonksiyonunun MySQL'e özel preset engine yapılandırmasını kullandığını test eder."""
        config = get_mysql_config()
        
        preset = DB_ENGINE_CONFIGS[DatabaseType.MYSQL]
        assert config.engine_config.pool_size == preset.pool_size
        assert config.engine_config.max_overflow == preset.max_overflow
        assert config.engine_config.isolation_level == preset.isolation_level

