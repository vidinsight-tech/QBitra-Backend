import pytest
from miniflow.database.config.engine_config import EngineConfig
from miniflow.database.config.engine_config_presets import DB_ENGINE_CONFIGS
from miniflow.database.config.database_type import DatabaseType
from miniflow.core.exceptions import DatabaseConfigurationError


@pytest.mark.unit
@pytest.mark.config
@pytest.mark.database
class TestEngineConfigBase:
    """EngineConfig sınıfı için genel testler."""

    # --- Başlatma Testleri ---
    def test_engine_config_has_correct_default_values(self):
        """EngineConfig'in üretim için hazır varsayılan değerlerle başlatıldığını test eder."""
        config = EngineConfig()
        
        assert config.pool_size == 10
        assert config.max_overflow == 20
        assert config.pool_timeout == 30
        assert config.pool_recycle == 3600
        assert config.pool_pre_ping is True
        assert config.echo is False
        assert config.echo_pool is False
        assert config.autocommit is False
        assert config.autoflush is True
        assert config.expire_on_commit is True
        assert config.isolation_level is None
        assert config.connect_args == {}

    def test_engine_config_accepts_custom_values(self):
        """EngineConfig'in özel yapılandırma değerlerini kabul ettiğini test eder."""
        config = EngineConfig(
            pool_size=5,
            max_overflow=10,
            pool_timeout=20,
            pool_recycle=1800,
            pool_pre_ping=False,
            echo=True,
            echo_pool=True,
            autocommit=True,
            autoflush=False,
            expire_on_commit=False,
            isolation_level='READ_COMMITTED',
            connect_args={'sslmode': 'require'}
        )
        
        assert config.pool_size == 5
        assert config.max_overflow == 10
        assert config.pool_timeout == 20
        assert config.pool_recycle == 1800
        assert config.pool_pre_ping is False
        assert config.echo is True
        assert config.echo_pool is True
        assert config.autocommit is True
        assert config.autoflush is False
        assert config.expire_on_commit is False
        assert config.isolation_level == 'READ_COMMITTED'
        assert config.connect_args == {'sslmode': 'require'}

    # --- __post_init__ Testleri ---
    def test_post_init_accepts_valid_positive_integer_pool_parameters(self):
        """__post_init__ metodunun geçerli pozitif tamsayı pool parametrelerini kabul ettiğini test eder."""
        # Valid values should work
        config = EngineConfig(pool_size=5, max_overflow=10, pool_timeout=15, pool_recycle=1800)
        assert config.pool_size == 5
        assert config.max_overflow == 10
        assert config.pool_timeout == 15
        assert config.pool_recycle == 1800

    def test_post_init_converts_string_numbers_to_integers(self):
        """__post_init__ metodunun string sayıları otomatik olarak tamsayıya dönüştürdüğünü test eder."""
        config = EngineConfig(pool_size="5", max_overflow="10", pool_timeout="15", pool_recycle="1800")
        assert config.pool_size == 5
        assert config.max_overflow == 10
        assert config.pool_timeout == 15
        assert config.pool_recycle == 1800

    def test_post_init_raises_error_for_negative_pool_parameters(self):
        """__post_init__ metodunun negatif pool parametreleri için DatabaseConfigurationError oluşturduğunu test eder."""
        with pytest.raises(DatabaseConfigurationError):
            EngineConfig(pool_size=-1)
        
        with pytest.raises(DatabaseConfigurationError):
            EngineConfig(max_overflow=-5)
        
        with pytest.raises(DatabaseConfigurationError):
            EngineConfig(pool_timeout=-10)
        
        with pytest.raises(DatabaseConfigurationError):
            EngineConfig(pool_recycle=-100)

    def test_post_init_raises_error_for_invalid_pool_parameter_types(self):
        """__post_init__ metodunun geçersiz parametre türleri için DatabaseConfigurationError oluşturduğunu test eder."""
        with pytest.raises(DatabaseConfigurationError):
            EngineConfig(pool_size="invalid")
        
        with pytest.raises(DatabaseConfigurationError):
            EngineConfig(max_overflow=None)
        
        with pytest.raises(DatabaseConfigurationError):
            EngineConfig(pool_timeout=[1, 2, 3])

    def test_post_init_allows_zero_values_for_pool_parameters(self):
        """__post_init__ metodunun pool parametreleri için sıfır değerlerine izin verdiğini test eder."""
        config = EngineConfig(pool_size=0, max_overflow=0, pool_timeout=0, pool_recycle=0)
        assert config.pool_size == 0
        assert config.max_overflow == 0
        assert config.pool_timeout == 0
        assert config.pool_recycle == 0

    # --- Metod Testleri ---
    def test_repr_returns_formatted_string_representation(self):
        """__repr__ metodunun EngineConfig'in formatlanmış string temsilini döndürdüğünü test eder."""
        config = EngineConfig()
        repr_str = repr(config)
        
        assert "EngineConfig(" in repr_str
        assert "pool_size=10" in repr_str
        assert "max_overflow=20" in repr_str
        assert "pre_ping=True" in repr_str
        assert "echo=False" in repr_str

    def test_to_dict_returns_complete_dictionary_representation(self):
        """to_dict metodunun tüm engine ve session ayarlarını içeren tam bir sözlük döndürdüğünü test eder."""
        config = EngineConfig(
            pool_size=5,
            max_overflow=10,
            isolation_level='READ_COMMITTED',
            connect_args={'test': 'value'}
        )
        
        result = config.to_dict()
        
        assert result['pool_size'] == 5
        assert result['max_overflow'] == 10
        assert result['pool_timeout'] == 30
        assert result['pool_recycle'] == 3600
        assert result['pool_pre_ping'] is True
        assert result['echo'] is False
        assert result['echo_pool'] is False
        assert result['isolation_level'] == 'READ_COMMITTED'
        assert result['connect_args'] == {'test': 'value'}
        assert result['autocommit'] is False
        assert result['autoflush'] is True
        assert result['expire_on_commit'] is True

    def test_to_engine_kwargs_returns_only_engine_related_parameters(self):
        """to_engine_kwargs metodunun sadece create_engine() için ilgili parametreleri döndürdüğünü test eder."""
        config = EngineConfig(
            pool_size=5,
            max_overflow=10,
            isolation_level='READ_COMMITTED',
            connect_args={'test': 'value'}
        )
        
        result = config.to_engine_kwargs()
        
        assert result['pool_size'] == 5
        assert result['max_overflow'] == 10
        assert result['pool_timeout'] == 30
        assert result['pool_recycle'] == 3600
        assert result['pool_pre_ping'] is True
        assert result['echo'] is False
        assert result['echo_pool'] is False
        assert result['isolation_level'] == 'READ_COMMITTED'
        assert result['connect_args'] == {'test': 'value'}
        # Session-related settings should not be in engine kwargs
        assert 'autocommit' not in result
        assert 'autoflush' not in result
        assert 'expire_on_commit' not in result

    def test_to_session_kwargs_returns_only_session_related_parameters(self):
        """to_session_kwargs metodunun sadece sessionmaker/Session için ilgili parametreleri döndürdüğünü test eder."""
        config = EngineConfig(
            autocommit=True,
            autoflush=False,
            expire_on_commit=False
        )
        
        result = config.to_session_kwargs()
        
        assert result['autocommit'] is True
        assert result['autoflush'] is False
        assert result['expire_on_commit'] is False
        # Engine-related settings should not be in session kwargs
        assert 'pool_size' not in result
        assert 'max_overflow' not in result
        assert 'echo' not in result


@pytest.mark.unit
@pytest.mark.config
@pytest.mark.database
class TestEngineConfigSqlite:
    """EngineConfig sınıfı için SQLite'a özel testler."""

    # --- Preset Testleri ---
    def test_sqlite_preset_has_correct_values(self):
        """SQLite preset yapılandırmasının doğru değerlere sahip olduğunu test eder."""
        preset = DB_ENGINE_CONFIGS[DatabaseType.SQLITE]
        
        assert preset.pool_size == 1
        assert preset.max_overflow == 0
        assert preset.pool_timeout == 20
        assert preset.pool_recycle == 0
        assert preset.pool_pre_ping is False
        assert preset.isolation_level is None
        assert preset.connect_args['check_same_thread'] is False
        assert preset.connect_args['timeout'] == 20

    def test_sqlite_preset_allows_zero_pool_recycle(self):
        """SQLite preset'inin pool_recycle=0 değerini kabul ettiğini test eder."""
        preset = DB_ENGINE_CONFIGS[DatabaseType.SQLITE]
        assert preset.pool_recycle == 0


@pytest.mark.unit
@pytest.mark.config
@pytest.mark.database
class TestEngineConfigPostgreSQL:
    """EngineConfig sınıfı için PostgreSQL'e özel testler."""

    # --- Preset Testleri ---
    def test_postgresql_preset_has_correct_values(self):
        """PostgreSQL preset yapılandırmasının doğru değerlere sahip olduğunu test eder."""
        preset = DB_ENGINE_CONFIGS[DatabaseType.POSTGRESQL]
        
        assert preset.pool_size == 20
        assert preset.max_overflow == 30
        assert preset.pool_timeout == 60
        assert preset.pool_recycle == 3600
        assert preset.pool_pre_ping is True
        assert preset.isolation_level == 'READ_COMMITTED'
        assert preset.connect_args['connect_timeout'] == 30
        assert preset.connect_args['sslmode'] == 'require'
        assert preset.connect_args['application_name'] == 'miniflow_app'

    def test_postgresql_preset_has_isolation_level(self):
        """PostgreSQL preset'inin isolation_level değerine sahip olduğunu test eder."""
        preset = DB_ENGINE_CONFIGS[DatabaseType.POSTGRESQL]
        assert preset.isolation_level == 'READ_COMMITTED'

    def test_postgresql_preset_has_ssl_mode(self):
        """PostgreSQL preset'inin SSL modunu içerdiğini test eder."""
        preset = DB_ENGINE_CONFIGS[DatabaseType.POSTGRESQL]
        assert 'sslmode' in preset.connect_args
        assert preset.connect_args['sslmode'] == 'require'


@pytest.mark.unit
@pytest.mark.config
@pytest.mark.database
class TestEngineConfigMySQL:
    """EngineConfig sınıfı için MySQL'e özel testler."""

    # --- Preset Testleri ---
    def test_mysql_preset_has_correct_values(self):
        """MySQL preset yapılandırmasının doğru değerlere sahip olduğunu test eder."""
        preset = DB_ENGINE_CONFIGS[DatabaseType.MYSQL]
        
        assert preset.pool_size == 15
        assert preset.max_overflow == 25
        assert preset.pool_timeout == 45
        assert preset.pool_recycle == 7200
        assert preset.pool_pre_ping is True
        assert preset.isolation_level == 'READ_COMMITTED'
        assert preset.connect_args['connect_timeout'] == 30

    def test_mysql_preset_has_isolation_level(self):
        """MySQL preset'inin isolation_level değerine sahip olduğunu test eder."""
        preset = DB_ENGINE_CONFIGS[DatabaseType.MYSQL]
        assert preset.isolation_level == 'READ_COMMITTED'

    def test_mysql_preset_has_longer_pool_recycle(self):
        """MySQL preset'inin daha uzun pool_recycle değerine sahip olduğunu test eder."""
        preset = DB_ENGINE_CONFIGS[DatabaseType.MYSQL]
        postgresql_preset = DB_ENGINE_CONFIGS[DatabaseType.POSTGRESQL]
        assert preset.pool_recycle == 7200
        assert preset.pool_recycle > postgresql_preset.pool_recycle
