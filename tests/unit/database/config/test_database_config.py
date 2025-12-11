import pytest
from miniflow.database.config.database_config import DatabaseConfig
from miniflow.database.config.database_type import DatabaseType
from miniflow.database.config.engine_config import EngineConfig
from miniflow.core.exceptions import DatabaseConfigurationError


@pytest.mark.unit
@pytest.mark.config
@pytest.mark.database
class TestDatabaseConfigBase:
    """DatabaseConfig sınıfı için genel testler."""

    # --- Başlatma Testleri ---
    def test_database_config_initiliazed_with_correct_default_values(self):
        """DatabaseConfig'in değer verilmeden oluşturulduğunda doğru varsayılan değerleri aldığını test eder."""
        config = DatabaseConfig()

        assert config.db_name == "miniflow"
        assert config.db_type == DatabaseType.SQLITE
        assert config.host == "localhost"
        assert config.port == 0 
        assert config.username is None
        assert config.password is None
        assert config.sqlite_path == "./miniflow.db"
        assert config.connect_args is None
        assert isinstance(config.engine_config, EngineConfig)
        assert config.application_name is None
        assert config.statement_timeout_ms is None

    # --- __post_init__ Testleri ---
    def test_post_init_converts_port_string_to_integer(self):
        """__post_init__ metodunun port string değerini tamsayıya dönüştürdüğünü test eder."""
        config = DatabaseConfig(
            db_type=DatabaseType.MYSQL,
            db_name="testdb",
            host="localhost",
            port="3306",
            username="root",
            password="secret"
        )
        
        assert config.port == 3306
        assert isinstance(config.port, int)


@pytest.mark.unit
@pytest.mark.config
@pytest.mark.database
class TestDatabaseConfigSqlite:
    """DatabaseConfig sınıfı için SQLite'a özel testler."""

    # --- Başlatma Testleri ---
    def test_sqlite_configuration_creation(self):
        """SQLite yapılandırmasının doğru şekilde oluşturulduğunu test eder."""
        config = DatabaseConfig(
            db_type=DatabaseType.SQLITE,
            sqlite_path="./test.db"
        )
        
        assert config.sqlite_path == "./test.db"
        assert config.port == 0

    # --- __post_init__ Testleri ---
    def test_post_init_raises_error_when_sqlite_path_is_empty(self):
        """__post_init__ metodunun SQLite path boş olduğunda DatabaseConfigurationError oluşturduğunu test eder."""
        with pytest.raises(DatabaseConfigurationError):
            DatabaseConfig(
                db_type=DatabaseType.SQLITE,
                sqlite_path=""  # Empty path
            )

    # --- __repr__ Testleri ---
    def test_repr_returns_formatted_string_for_sqlite_config(self):
        """__repr__ metodunun SQLite yapılandırması için formatlanmış string temsilini döndürdüğünü test eder."""
        config = DatabaseConfig(
            db_type=DatabaseType.SQLITE,
            sqlite_path="./test.db"
        )
        repr_str = repr(config)
        assert "DatabaseConfig" in repr_str
        assert "sqlite" in repr_str
        assert "./test.db" in repr_str

    # --- get_connection_string Testleri ---
    def test_get_connection_string_returns_sqlite_file_url(self):
        """get_connection_string metodunun doğru SQLite dosya URL'i döndürdüğünü test eder."""
        config = DatabaseConfig(
            db_type=DatabaseType.SQLITE,
            sqlite_path="./test.db"
        )
        conn_str = config.get_connection_string()
        assert conn_str == "sqlite:///./test.db"

    def test_get_connection_string_returns_sqlite_memory_url_with_shared_cache(self):
        """get_connection_string metodunun çoklu thread için paylaşılan cache ile SQLite bellek URL'i döndürdüğünü test eder."""
        config = DatabaseConfig(
            db_type=DatabaseType.SQLITE,
            sqlite_path=":memory:"
        )
        conn_str = config.get_connection_string()
        assert "sqlite:///file::memory:" in conn_str
        assert "cache=shared" in conn_str

    # --- get_pool_class Testleri ---
    def test_get_pool_class_returns_nullpool_for_sqlite_file(self):
        """get_pool_class metodunun dosya tabanlı SQLite veritabanları için NullPool döndürdüğünü test eder."""
        config = DatabaseConfig(
            db_type=DatabaseType.SQLITE,
            sqlite_path="./test.db"
        )
        from sqlalchemy.pool import NullPool
        assert config.get_pool_class() == NullPool

    def test_get_pool_class_returns_staticpool_for_sqlite_memory(self):
        """get_pool_class metodunun bellek içi SQLite veritabanları için StaticPool döndürdüğünü test eder."""
        config = DatabaseConfig(
            db_type=DatabaseType.SQLITE,
            sqlite_path=":memory:"
        )
        from sqlalchemy.pool import StaticPool
        assert config.get_pool_class() == StaticPool

    # --- get_connect_args Testleri ---
    def test_get_connect_args_returns_sqlite_default_connect_args(self):
        """get_connect_args metodunun SQLite'a özel varsayılan bağlantı argümanlarını döndürdüğünü test eder."""
        config = DatabaseConfig(
            db_type=DatabaseType.SQLITE,
            sqlite_path="./test.db"
        )
        args = config.get_connect_args()
        assert args['check_same_thread'] is False

    def test_get_connect_args_allows_overriding_sqlite_defaults(self):
        """get_connect_args metodunun SQLite varsayılan bağlantı argümanlarının üzerine yazılmasına izin verdiğini test eder."""
        config = DatabaseConfig(
            db_type=DatabaseType.SQLITE,
            sqlite_path="./test.db",
            connect_args={'check_same_thread': True}
        )
        args = config.get_connect_args()
        assert args['check_same_thread'] is True  # Override should work


@pytest.mark.unit
@pytest.mark.config
@pytest.mark.database
class TestDatabaseConfigPostgreSQL:
    """DatabaseConfig sınıfı için PostgreSQL'e özel testler."""

    # --- Başlatma Testleri ---
    def test_postgresql_cconfiguration_creation(self):
        """PostgreSQL yapılandırmasının doğru şekilde oluşturulduğunu test eder."""
        config = DatabaseConfig(
            db_type=DatabaseType.POSTGRESQL,
            db_name="testdb",
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

    # --- __post_init__ Testleri ---
    def test_post_init_sets_default_port_when_port_is_none(self):
        """__post_init__ metodunun port None olduğunda varsayılan port değerini ayarladığını test eder."""
        config = DatabaseConfig(
            db_type=DatabaseType.POSTGRESQL,
            db_name="testdb",
            host="localhost",
            username="postgres",
            password="secret"
        )
        
        assert config.port == 5432  # PostgreSQL default from Type class

    def test_post_init_raises_error_when_postgresql_missing_credentials(self):
        """__post_init__ metodunun PostgreSQL için kimlik bilgileri eksik olduğunda DatabaseConfigurationError oluşturduğunu test eder."""
        with pytest.raises(DatabaseConfigurationError):
            DatabaseConfig(
                db_type=DatabaseType.POSTGRESQL,
                db_name="testdb",
                host="localhost",
                port=5432
                # Missing username and password
            )

    def test_post_init_raises_error_when_postgresql_missing_host(self):
        """__post_init__ metodunun PostgreSQL için host boş olduğunda DatabaseConfigurationError oluşturduğunu test eder."""
        with pytest.raises(DatabaseConfigurationError):
            DatabaseConfig(
                db_type=DatabaseType.POSTGRESQL,
                db_name="testdb",
                host="",  # Empty host
                port=5432,
                username="postgres",
                password="secret"
            )

    def test_post_init_raises_error_when_postgresql_missing_db_name(self):
        """__post_init__ metodunun PostgreSQL için db_name boş olduğunda DatabaseConfigurationError oluşturduğunu test eder."""
        with pytest.raises(DatabaseConfigurationError):
            DatabaseConfig(
                db_type=DatabaseType.POSTGRESQL,
                db_name="",  # Empty db_name
                host="localhost",
                port=5432,
                username="root",
                password="secret"
            )

    def test_post_init_raises_error_when_postgresql_has_invalid_port(self):
        """__post_init__ metodunun PostgreSQL için geçersiz port olduğunda DatabaseConfigurationError oluşturduğunu test eder."""
        with pytest.raises(DatabaseConfigurationError):
            DatabaseConfig(
                db_type=DatabaseType.POSTGRESQL,
                db_name="testdb",
                host="localhost",
                port=0,  # Invalid port
                username="postgres",
                password="secret"
            )

    def test_post_init_validates_statement_timeout_ms_for_postgresql(self):
        """__post_init__ metodunun PostgreSQL yapılandırmaları için statement_timeout_ms değerini doğruladığını test eder."""
        # Valid timeout
        config = DatabaseConfig(
            db_type=DatabaseType.POSTGRESQL,
            db_name="testdb",
            host="localhost",
            port=5432,
            username="postgres",
            password="secret",
            statement_timeout_ms=5000
        )
        assert config.statement_timeout_ms == 5000

        # Invalid: negative value
        with pytest.raises(DatabaseConfigurationError):
            DatabaseConfig(
                db_type=DatabaseType.POSTGRESQL,
                db_name="testdb",
                host="localhost",
                port=5432,
                username="postgres",
                password="secret",
                statement_timeout_ms=-100
            )

        # Invalid: non-integer
        with pytest.raises(DatabaseConfigurationError):
            DatabaseConfig(
                db_type=DatabaseType.POSTGRESQL,
                db_name="testdb",
                host="localhost",
                port=5432,
                username="postgres",
                password="secret",
                statement_timeout_ms="invalid"
            )

    # --- __repr__ Testleri ---
    def test_repr_returns_formatted_string_for_postgresql_config(self):
        """__repr__ metodunun PostgreSQL yapılandırması için formatlanmış string temsilini döndürdüğünü test eder."""
        config = DatabaseConfig(
            db_type=DatabaseType.POSTGRESQL,
            db_name="testdb",
            host="localhost",
            port=5432,
            username="postgres",
            password="secret"
        )
        repr_str = repr(config)
        assert "DatabaseConfig" in repr_str
        assert "postgresql" in repr_str
        assert "localhost" in repr_str
        assert "5432" in repr_str
        assert "testdb" in repr_str
        assert "postgres" in repr_str
        # Password should not be in repr
        assert "secret" not in repr_str

    # --- get_connection_string Testleri ---
    def test_get_connection_string_returns_postgresql_url_with_credentials(self):
        """get_connection_string metodunun kimlik bilgileriyle doğru PostgreSQL URL'i döndürdüğünü test eder."""
        config = DatabaseConfig(
            db_type=DatabaseType.POSTGRESQL,
            db_name="testdb",
            host="localhost",
            port=5432,
            username="postgres",
            password="secret"
        )
        conn_str = config.get_connection_string()
        assert "postgresql://" in conn_str
        assert "postgres" in conn_str
        assert "localhost" in conn_str
        assert "5432" in conn_str
        assert "testdb" in conn_str
        assert "charset=utf8mb4" not in conn_str  # Only for MySQL

    def test_get_connection_string_includes_application_name_in_postgresql_url(self):
        """get_connection_string metodunun PostgreSQL URL'inde application_name'i query parametrelerine eklediğini test eder."""
        config = DatabaseConfig(
            db_type=DatabaseType.POSTGRESQL,
            db_name="testdb",
            host="localhost",
            port=5432,
            username="postgres",
            password="secret",
            application_name="myapp"
        )
        conn_str = config.get_connection_string()
        assert "application_name=myapp" in conn_str

    def test_get_connection_string_includes_statement_timeout_in_postgresql_url(self):
        """get_connection_string metodunun PostgreSQL URL'inde statement_timeout'u eklediğini test eder."""
        config = DatabaseConfig(
            db_type=DatabaseType.POSTGRESQL,
            db_name="testdb",
            host="localhost",
            port=5432,
            username="postgres",
            password="secret",
            statement_timeout_ms=5000
        )
        conn_str = config.get_connection_string()
        # URL encoding: = becomes %3D
        assert "statement_timeout" in conn_str
        assert "5000ms" in conn_str

    # --- get_pool_class Testleri ---
    def test_get_pool_class_returns_queuepool_for_postgresql(self):
        """get_pool_class metodunun PostgreSQL veritabanları için QueuePool döndürdüğünü test eder."""
        config = DatabaseConfig(
            db_type=DatabaseType.POSTGRESQL,
            db_name="testdb",
            host="localhost",
            port=5432,
            username="postgres",
            password="secret"
        )
        from sqlalchemy.pool import QueuePool
        assert config.get_pool_class() == QueuePool

    # --- get_connect_args Testleri ---
    def test_get_connect_args_returns_postgresql_default_connect_args(self):
        """get_connect_args metodunun PostgreSQL'e özel varsayılan bağlantı argümanlarını döndürdüğünü test eder."""
        config = DatabaseConfig(
            db_type=DatabaseType.POSTGRESQL,
            db_name="testdb",
            host="localhost",
            port=5432,
            username="postgres",
            password="secret"
        )
        args = config.get_connect_args()
        assert args['connect_timeout'] == 10

    def test_get_connect_args_merges_engine_config_connect_args(self):
        """get_connect_args metodunun engine_config'den gelen connect_args'i veritabanına özel varsayılanlarla birleştirdiğini test eder."""
        engine_config = EngineConfig(connect_args={'custom_arg': 'value'})
        config = DatabaseConfig(
            db_type=DatabaseType.POSTGRESQL,
            db_name="testdb",
            host="localhost",
            port=5432,
            username="postgres",
            password="secret",
            engine_config=engine_config
        )
        args = config.get_connect_args()
        assert args['custom_arg'] == 'value'
        assert args['connect_timeout'] == 10  # DB-specific default

    # --- to_dict Testleri ---
    def test_to_dict_returns_complete_dictionary_excluding_password(self):
        """to_dict metodunun güvenlik için şifre hariç tam sözlük temsilini döndürdüğünü test eder."""
        config = DatabaseConfig(
            db_type=DatabaseType.POSTGRESQL,
            db_name="testdb",
            host="localhost",
            port=5432,
            username="postgres",
            password="secret",
            application_name="myapp",
            statement_timeout_ms=5000
        )
        
        result = config.to_dict()
        
        assert result['db_name'] == "testdb"
        assert result['db_type'] == "postgresql"
        assert result['host'] == "localhost"
        assert result['port'] == 5432
        assert result['username'] == "postgres"
        assert 'password' not in result  # Password should not be in dict
        assert 'connection_string' in result
        assert 'pool_class' in result
        assert result['pool_class'] == "QueuePool"
        assert result['application_name'] == "myapp"
        assert result['statement_timeout_ms'] == 5000
        assert 'engine' in result
        assert isinstance(result['engine'], dict)
        assert 'connect_args' in result


@pytest.mark.unit
@pytest.mark.config
@pytest.mark.database
class TestDatabaseConfigMySQL:
    """DatabaseConfig sınıfı için MySQL'e özel testler."""

    # --- Başlatma Testleri ---
    def test_mysql_configuration_creation(self):
        """MySQL yapılandırmasının doğru şekilde oluşturulduğunu test eder."""
        config = DatabaseConfig(
            db_type=DatabaseType.MYSQL,
            db_name="testdb",
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

    # --- __post_init__ Testleri ---
    def test_post_init_raises_error_when_mysql_missing_credentials(self):
        """__post_init__ metodunun MySQL için kimlik bilgileri eksik olduğunda DatabaseConfigurationError oluşturduğunu test eder."""
        with pytest.raises(DatabaseConfigurationError):
            DatabaseConfig(
                db_type=DatabaseType.MYSQL,
                db_name="testdb",
                host="localhost",
                port=3306
                # Missing username and password
            )

    def test_post_init_raises_error_when_mysql_missing_host(self):
        """__post_init__ metodunun MySQL için host boş olduğunda DatabaseConfigurationError oluşturduğunu test eder."""
        with pytest.raises(DatabaseConfigurationError):
            DatabaseConfig(
                db_type=DatabaseType.MYSQL,
                db_name="testdb",
                host="",  # Empty host
                port=3306,
                username="postgres",
                password="secret"
            )

    def test_post_init_raises_error_when_mysql_missing_db_name(self):
        """__post_init__ metodunun MySQL için db_name boş olduğunda DatabaseConfigurationError oluşturduğunu test eder."""
        with pytest.raises(DatabaseConfigurationError):
            DatabaseConfig(
                db_type=DatabaseType.MYSQL,
                db_name="",  # Empty db_name
                host="localhost",
                port=3306,
                username="root",
                password="secret"
            )

    def test_post_init_raises_error_when_mysql_has_invalid_port(self):
        """__post_init__ metodunun MySQL için geçersiz port olduğunda DatabaseConfigurationError oluşturduğunu test eder."""
        with pytest.raises(DatabaseConfigurationError):
            DatabaseConfig(
                db_type=DatabaseType.MYSQL,
                db_name="testdb",
                host="localhost",
                port=0,  # Invalid port
                username="postgres",
                password="secret"
            )

    # --- get_connection_string Testleri ---
    def test_get_connection_string_returns_mysql_url_with_charset(self):
        """get_connection_string metodunun query parametrelerinde utf8mb4 charset ile MySQL URL'i döndürdüğünü test eder."""
        config = DatabaseConfig(
            db_type=DatabaseType.MYSQL,
            db_name="testdb",
            host="localhost",
            port=3306,
            username="root",
            password="secret"
        )
        conn_str = config.get_connection_string()
        assert "mysql+pymysql://" in conn_str
        assert "root" in conn_str
        assert "localhost" in conn_str
        assert "3306" in conn_str
        assert "testdb" in conn_str
        assert "charset=utf8mb4" in conn_str

    # --- get_pool_class Testleri ---
    def test_get_pool_class_returns_queuepool_for_mysql(self):
        """get_pool_class metodunun MySQL veritabanları için QueuePool döndürdüğünü test eder."""
        config = DatabaseConfig(
            db_type=DatabaseType.MYSQL,
            db_name="testdb",
            host="localhost",
            port=3306,
            username="root",
            password="secret"
        )
        from sqlalchemy.pool import QueuePool
        assert config.get_pool_class() == QueuePool

    # --- get_connect_args Testleri ---
    def test_get_connect_args_returns_mysql_default_connect_args(self):
        """get_connect_args metodunun timeout'larla MySQL'e özel varsayılan bağlantı argümanlarını döndürdüğünü test eder."""
        config = DatabaseConfig(
            db_type=DatabaseType.MYSQL,
            db_name="testdb",
            host="localhost",
            port=3306,
            username="root",
            password="secret"
        )
        args = config.get_connect_args()
        assert args['connect_timeout'] == 10
        assert args['read_timeout'] == 30
        assert args['write_timeout'] == 30

    def test_get_connect_args_gives_highest_priority_to_database_config_connect_args(self):
        """get_connect_args metodunun DatabaseConfig.connect_args'e varsayılanlar üzerinde en yüksek öncelik verdiğini test eder."""
        engine_config = EngineConfig(connect_args={'timeout': 10})
        config = DatabaseConfig(
            db_type=DatabaseType.MYSQL,
            db_name="testdb",
            host="localhost",
            port=3306,
            username="root",
            password="secret",
            engine_config=engine_config,
            connect_args={'connect_timeout': 20}  # Override DB default
        )
        args = config.get_connect_args()
        assert args['connect_timeout'] == 20  # Override should win
        assert args['read_timeout'] == 30  # DB default still there
