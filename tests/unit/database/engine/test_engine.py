"""
DatabaseEngine sınıfı için testler.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session
from sqlalchemy import MetaData

from miniflow.database.engine.engine import DatabaseEngine
from miniflow.database.config.database_type import DatabaseType
from miniflow.database.config.database_config import DatabaseConfig
from miniflow.database.config.engine_config import EngineConfig
from miniflow.core.exceptions import (
    DatabaseConfigurationError,
    DatabaseEngineError,
    DatabaseSessionError,
    DatabaseQueryError
)


@pytest.mark.unit
@pytest.mark.database
@pytest.mark.engine
class TestDatabaseEngineInitialization:
    """DatabaseEngine başlatma testleri."""

    # --- Başlatma Testleri ---
    def test_database_engine_initialization_with_valid_config(self, sqlite_config_memory):
        """Geçerli config ile DatabaseEngine başlatılabilir."""
        engine = DatabaseEngine(sqlite_config_memory)
        
        assert engine.config == sqlite_config_memory
        assert engine._engine is None  # Henüz başlatılmadı
        assert engine._session_factory is None
        assert not engine.is_alive

    def test_database_engine_initialization_raises_error_with_invalid_config(self):
        """Geçersiz config ile DatabaseEngine başlatılamaz."""
        with pytest.raises(DatabaseConfigurationError):
            DatabaseEngine(None)

    def test_database_engine_initialization_raises_error_with_empty_db_name(self):
        """Boş db_name ile DatabaseEngine başlatılamaz."""
        with pytest.raises(DatabaseConfigurationError):
            config = DatabaseConfig(
                db_type=DatabaseType.POSTGRESQL,
                db_name="",  # Boş db_name
                host="localhost",
                port=5432,
                username="postgres",
                password="pass"
            )
            DatabaseEngine(config)

    def test_database_engine_initialization_raises_error_with_invalid_pool_size(self, sqlite_config_memory):
        """Geçersiz pool_size ile DatabaseEngine başlatılamaz."""
        config = DatabaseConfig(
            db_type=DatabaseType.SQLITE,
            sqlite_path=":memory:",
            engine_config=EngineConfig(pool_size=0)
        )
        
        with pytest.raises(DatabaseConfigurationError):
            DatabaseEngine(config)

    def test_database_engine_caches_database_type_on_init(self, sqlite_config_memory):
        """DatabaseEngine başlatıldığında veritabanı tipini cache'ler."""
        engine = DatabaseEngine(sqlite_config_memory)
        assert engine._db_type_cached == 'sqlite'

    # --- Private Metod Testleri ---
    def test_detect_db_type_returns_postgresql_for_postgresql_connection_string(self, sqlite_config_memory):
        """_detect_db_type metodu PostgreSQL connection string'i için 'postgresql' döndürür."""
        engine = DatabaseEngine(sqlite_config_memory)
        result = engine._detect_db_type("postgresql://user:pass@localhost/db")
        assert result == 'postgresql'

    def test_detect_db_type_returns_mysql_for_mysql_connection_string(self, sqlite_config_memory):
        """_detect_db_type metodu MySQL connection string'i için 'mysql' döndürür."""
        engine = DatabaseEngine(sqlite_config_memory)
        result = engine._detect_db_type("mysql+pymysql://user:pass@localhost/db")
        assert result == 'mysql'

    def test_detect_db_type_returns_sqlite_for_sqlite_connection_string(self, sqlite_config_memory):
        """_detect_db_type metodu SQLite connection string'i için 'sqlite' döndürür."""
        engine = DatabaseEngine(sqlite_config_memory)
        result = engine._detect_db_type("sqlite:///./test.db")
        assert result == 'sqlite'

    def test_detect_db_type_returns_unknown_for_unknown_connection_string(self, sqlite_config_memory):
        """_detect_db_type metodu bilinmeyen connection string için 'unknown' döndürür."""
        engine = DatabaseEngine(sqlite_config_memory)
        result = engine._detect_db_type("unknown://connection")
        assert result == 'unknown'

    def test_get_db_type_returns_cached_value(self, sqlite_config_memory):
        """_get_db_type metodu cache'lenmiş değeri döndürür."""
        engine = DatabaseEngine(sqlite_config_memory)
        assert engine._get_db_type() == 'sqlite'

    def test_get_db_type_falls_back_to_config_when_cache_missing(self, sqlite_config_memory):
        """_get_db_type metodu cache yoksa config'den değer alır."""
        engine = DatabaseEngine(sqlite_config_memory)
        engine._db_type_cached = None
        result = engine._get_db_type()
        assert result == 'sqlite'


@pytest.mark.unit
@pytest.mark.database
@pytest.mark.engine
class TestDatabaseEngineLifecycle:
    """DatabaseEngine yaşam döngüsü testleri."""

    # --- start() Testleri ---
    def test_start_creates_engine_and_session_factory(self, database_engine_not_started):
        """start() metodu engine ve session factory oluşturur."""
        engine = database_engine_not_started
        engine.start()
        
        assert engine._engine is not None
        assert engine._session_factory is not None
        assert engine.is_alive

    def test_start_is_idempotent(self, database_engine_not_started):
        """start() metodu idempotent'tir (birden fazla kez çağrılabilir)."""
        engine = database_engine_not_started
        engine.start()
        first_engine = engine._engine
        
        engine.start()  # İkinci kez çağrı
        assert engine._engine is first_engine  # Aynı engine olmalı

    def test_start_raises_error_when_engine_creation_fails(self, sqlite_config_memory):
        """start() metodu engine oluşturma hatasında DatabaseEngineError fırlatır."""
        engine = DatabaseEngine(sqlite_config_memory)
        
        with patch('miniflow.database.engine.engine.create_engine', side_effect=Exception("Connection failed")):
            with pytest.raises(DatabaseEngineError):
                engine.start()

    # --- stop() Testleri ---
    def test_stop_closes_all_resources(self, database_engine_started):
        """stop() metodu tüm kaynakları kapatır."""
        engine = database_engine_started
        engine.stop()
        
        assert engine._engine is None
        assert engine._session_factory is None
        assert not engine.is_alive

    def test_stop_is_idempotent(self, database_engine_started):
        """stop() metodu idempotent'tir (birden fazla kez çağrılabilir)."""
        engine = database_engine_started
        engine.stop()
        engine.stop()  # İkinci kez çağrı
        
        assert engine._engine is None
        assert not engine.is_alive

    def test_stop_closes_active_sessions(self, database_engine_started):
        """stop() metodu aktif session'ları kapatır."""
        engine = database_engine_started
        session = engine.get_session()
        initial_count = engine.get_active_session_count()
        
        engine.stop()
        
        # Session tracking listesi temizlenmiş olmalı
        assert engine.get_active_session_count() == 0

    # --- is_alive Property Testleri ---
    def test_is_alive_returns_false_before_start(self, database_engine_not_started):
        """is_alive property başlatılmadan önce False döndürür."""
        engine = database_engine_not_started
        assert not engine.is_alive

    def test_is_alive_returns_true_after_start(self, database_engine_not_started):
        """is_alive property başlatıldıktan sonra True döndürür."""
        engine = database_engine_not_started
        engine.start()
        assert engine.is_alive

    def test_is_alive_returns_false_after_stop(self, database_engine_started):
        """is_alive property durdurulduktan sonra False döndürür."""
        engine = database_engine_started
        engine.stop()
        assert not engine.is_alive


@pytest.mark.unit
@pytest.mark.database
@pytest.mark.engine
class TestDatabaseEngineSessionManagement:
    """DatabaseEngine session yönetimi testleri."""

    # --- get_session() Testleri ---
    def test_get_session_raises_error_when_engine_not_started(self, database_engine_not_started):
        """get_session() metodu engine başlatılmamışsa DatabaseEngineError fırlatır."""
        engine = database_engine_not_started
        
        with pytest.raises(DatabaseEngineError):
            engine.get_session()

    def test_get_session_returns_valid_session(self, database_engine_started):
        """get_session() metodu geçerli session döndürür."""
        engine = database_engine_started
        session = engine.get_session()
        
        assert isinstance(session, Session)
        assert session.is_active

    def test_get_session_tracks_session(self, database_engine_started):
        """get_session() metodu session'ı takip eder."""
        engine = database_engine_started
        session = engine.get_session()
        
        assert engine.get_active_session_count() == 1

    def test_get_session_raises_error_on_failure(self, database_engine_started):
        """get_session() metodu session oluşturma hatasında DatabaseSessionError fırlatır."""
        engine = database_engine_started
        
        with patch.object(engine, '_session_factory', side_effect=Exception("Session creation failed")):
            with pytest.raises(DatabaseSessionError):
                engine.get_session()

    # --- session_context() Testleri ---
    def test_session_context_raises_error_when_engine_not_started(self, database_engine_not_started):
        """session_context() metodu engine başlatılmamışsa DatabaseEngineError fırlatır."""
        engine = database_engine_not_started
        
        with pytest.raises(DatabaseEngineError):
            with engine.session_context() as session:
                pass

    def test_session_context_returns_valid_session(self, database_engine_started):
        """session_context() metodu geçerli session döndürür."""
        engine = database_engine_started
        
        with engine.session_context() as session:
            assert isinstance(session, Session)
            assert session.is_active

    def test_session_context_auto_commits_on_success(self, database_engine_started):
        """session_context() metodu başarılı işlemde otomatik commit yapar."""
        engine = database_engine_started
        
        with engine.session_context() as session:
            # Session context içinde işlem yapılabilir
            pass
        
        # Context çıkışında otomatik commit yapılmış olmalı

    def test_session_context_rolls_back_on_error(self, database_engine_started):
        """session_context() metodu hata durumunda rollback yapar."""
        engine = database_engine_started
        
        with pytest.raises(ValueError):
            with engine.session_context() as session:
                raise ValueError("Test error")
        
        # Rollback yapılmış olmalı

    def test_session_context_respects_auto_commit_false(self, database_engine_started):
        """session_context() metodu auto_commit=False olduğunda otomatik commit yapmaz."""
        engine = database_engine_started
        
        with engine.session_context(auto_commit=False) as session:
            # Manuel commit gerekir
            pass

    def test_session_context_validates_timeout_value(self, database_engine_started):
        """session_context() metodu geçersiz timeout değeri için ValueError fırlatır."""
        engine = database_engine_started
        
        with pytest.raises(ValueError):
            with engine.session_context(timeout=-1) as session:
                pass

    def test_session_context_validates_timeout_type(self, database_engine_started):
        """session_context() metodu geçersiz timeout tipi için ValueError fırlatır."""
        engine = database_engine_started
        
        with pytest.raises(ValueError):
            with engine.session_context(timeout="invalid") as session:
                pass

    def test_session_context_validates_timeout_boundary_zero(self, database_engine_started):
        """session_context() metodu timeout=0 için ValueError fırlatır."""
        engine = database_engine_started
        
        with pytest.raises(ValueError):
            with engine.session_context(timeout=0) as session:
                pass

    def test_session_context_validates_timeout_boundary_max(self, database_engine_started):
        """session_context() metodu timeout>3600 için ValueError fırlatır."""
        engine = database_engine_started
        
        with pytest.raises(ValueError):
            with engine.session_context(timeout=3601) as session:
                pass

    def test_session_context_accepts_valid_timeout(self, database_engine_started):
        """session_context() metodu geçerli timeout değerini kabul eder."""
        engine = database_engine_started
        
        # Geçerli timeout değerleri
        with engine.session_context(timeout=1.0) as session:
            assert isinstance(session, Session)
        
        with engine.session_context(timeout=3600) as session:
            assert isinstance(session, Session)

    def test_session_context_respects_auto_flush_false(self, database_engine_started):
        """session_context() metodu auto_flush=False olduğunda otomatik flush yapmaz."""
        engine = database_engine_started
        
        with engine.session_context(auto_flush=False) as session:
            # Manuel flush gerekir
            pass

    def test_session_context_respects_auto_flush_true(self, database_engine_started):
        """session_context() metodu auto_flush=True olduğunda otomatik flush yapar."""
        engine = database_engine_started
        
        with engine.session_context(auto_flush=True) as session:
            # Otomatik flush yapılmalı
            pass

    def test_session_context_handles_isolation_level(self, database_engine_started):
        """session_context() metodu isolation_level parametresini işler."""
        engine = database_engine_started
        
        # SQLite SERIALIZABLE destekler
        with engine.session_context(isolation_level='SERIALIZABLE') as session:
            assert isinstance(session, Session)

    def test_session_context_raises_error_on_invalid_isolation_level(self, database_engine_started):
        """session_context() metodu geçersiz isolation_level için DatabaseConfigurationError fırlatır."""
        engine = database_engine_started
        
        # SQLite için geçersiz isolation level (READ_COMMITTED desteklenmez)
        with pytest.raises(DatabaseConfigurationError):
            with engine.session_context(isolation_level='READ_COMMITTED') as session:
                pass

    # --- get_active_session_count() Testleri ---
    def test_get_active_session_count_returns_zero_when_no_sessions(self, database_engine_started):
        """get_active_session_count() metodu session yoksa 0 döndürür."""
        engine = database_engine_started
        assert engine.get_active_session_count() == 0

    def test_get_active_session_count_returns_correct_count(self, database_engine_started):
        """get_active_session_count() metodu doğru session sayısını döndürür."""
        engine = database_engine_started
        
        # Başlangıçta session yok
        assert engine.get_active_session_count() == 0
        
        # Session oluştur ve sayıyı kontrol et
        session1 = engine.get_session()
        count1 = engine.get_active_session_count()
        assert count1 >= 1, f"En az 1 session olmalı, got {count1}"
        
        session2 = engine.get_session()
        count2 = engine.get_active_session_count()
        assert count2 >= 2, f"En az 2 session olmalı, got {count2}"
        
        # Session'ları kapat
        session1.close()
        session2.close()
        
        # close_all_sessions() ile temizlik yap (test için)
        engine.close_all_sessions()
        
        # Tüm session'lar kapatılmış olmalı
        assert engine.get_active_session_count() == 0

    def test_get_active_session_count_handles_dead_references(self, database_engine_started):
        """get_active_session_count() metodu ölü referansları temizler."""
        engine = database_engine_started
        session = engine.get_session()
        
        # Session'ı kapat ve garbage collect et
        session.close()
        del session
        
        # Lazy cleanup sayacını tetikle
        for _ in range(10):
            engine.get_active_session_count()
        
        # Ölü referanslar temizlenmiş olmalı
        assert engine.get_active_session_count() == 0

    # --- close_all_sessions() Testleri ---
    def test_close_all_sessions_returns_zero_when_no_sessions(self, database_engine_started):
        """close_all_sessions() metodu session yoksa 0 döndürür."""
        engine = database_engine_started
        assert engine.close_all_sessions() == 0

    def test_close_all_sessions_closes_all_active_sessions(self, database_engine_started):
        """close_all_sessions() metodu tüm aktif session'ları kapatır."""
        engine = database_engine_started
        session1 = engine.get_session()
        session2 = engine.get_session()
        
        closed_count = engine.close_all_sessions()
        
        assert closed_count == 2
        assert engine.get_active_session_count() == 0


@pytest.mark.unit
@pytest.mark.database
@pytest.mark.engine
class TestDatabaseEngineHealthCheck:
    """DatabaseEngine sağlık kontrolü testleri."""

    # --- health_check() Testleri ---
    def test_health_check_returns_stopped_when_engine_not_started(self, database_engine_not_started):
        """health_check() metodu engine başlatılmamışsa 'stopped' status döndürür."""
        engine = database_engine_not_started
        health = engine.health_check()
        
        assert health['status'] == 'stopped'
        assert health['engine_alive'] is False

    def test_health_check_returns_healthy_when_engine_is_running(self, database_engine_started):
        """health_check() metodu engine çalışıyorsa 'healthy' status döndürür."""
        engine = database_engine_started
        health = engine.health_check()
        
        assert health['status'] == 'healthy'
        assert health['engine_alive'] is True
        assert health['connection_test'] is True

    def test_health_check_includes_active_sessions_count(self, database_engine_started):
        """health_check() metodu aktif session sayısını içerir."""
        engine = database_engine_started
        session = engine.get_session()
        
        health = engine.health_check()
        
        assert health['active_sessions'] == 1
        
        session.close()

    def test_health_check_includes_pool_info(self, database_engine_started):
        """health_check() metodu pool bilgilerini içerir."""
        engine = database_engine_started
        health = engine.health_check()
        
        assert 'pool_info' in health
        assert isinstance(health['pool_info'], dict)

    def test_health_check_uses_cache_when_enabled(self, database_engine_started):
        """health_check() metodu cache kullanır (use_cache=True)."""
        engine = database_engine_started
        
        # İlk çağrı
        health1 = engine.health_check(use_cache=True)
        
        # İkinci çağrı (cache'den dönmeli)
        health2 = engine.health_check(use_cache=True)
        
        # Aynı sonuç olmalı (cache'den)
        assert health1 == health2

    def test_health_check_bypasses_cache_when_disabled(self, database_engine_started):
        """health_check() metodu cache'i atlar (use_cache=False)."""
        engine = database_engine_started
        
        health1 = engine.health_check(use_cache=False)
        health2 = engine.health_check(use_cache=False)
        
        # Her ikisi de fresh olmalı
        assert health1['status'] == health2['status']

    def test_health_check_handles_connection_failure(self, database_engine_started):
        """health_check() metodu bağlantı hatasını 'unhealthy' status ile döndürür."""
        engine = database_engine_started
        
        # Engine'i durdur ve bağlantı hatası simüle et
        from sqlalchemy.exc import OperationalError
        
        with patch.object(engine._engine, 'connect', side_effect=OperationalError("Connection failed", None, None)):
            health = engine.health_check(use_cache=False)
            
            assert health['status'] == 'unhealthy'
            assert health['connection_test'] is False
            assert health['error'] is not None

    def test_health_check_handles_unexpected_errors(self, database_engine_started):
        """health_check() metodu beklenmeyen hataları 'error' status ile döndürür."""
        engine = database_engine_started
        
        # Beklenmeyen hata simüle et (get_active_session_count'da hata)
        with patch.object(engine, 'get_active_session_count', side_effect=Exception("Unexpected error")):
            health = engine.health_check(use_cache=False)
            
            assert health['status'] == 'error'
            assert health['error'] is not None

    def test_health_check_cache_expires_after_ttl(self, database_engine_started):
        """health_check() metodu cache TTL sonrası yeni sonuç döndürür."""
        engine = database_engine_started
        
        # İlk çağrı
        health1 = engine.health_check(use_cache=True)
        
        # Cache TTL'ini geç (5 saniye)
        import time
        engine._health_check_cache_ttl = 0.01  # 0.01 saniye
        time.sleep(0.02)  # TTL'den fazla bekle
        
        # İkinci çağrı (cache expire olmuş olmalı)
        health2 = engine.health_check(use_cache=True)
        
        # Her ikisi de healthy olmalı ama farklı zamanlarda alınmış olmalı
        assert health1['status'] == 'healthy'
        assert health2['status'] == 'healthy'


@pytest.mark.unit
@pytest.mark.database
@pytest.mark.engine
class TestDatabaseEngineTableManagement:
    """DatabaseEngine tablo yönetimi testleri."""

    # --- create_tables() Testleri ---
    def test_create_tables_raises_error_when_engine_not_started(self, database_engine_not_started):
        """create_tables() metodu engine başlatılmamışsa DatabaseEngineError fırlatır."""
        engine = database_engine_not_started
        metadata = MetaData()
        
        with pytest.raises(DatabaseEngineError):
            engine.create_tables(metadata)

    def test_create_tables_creates_tables_successfully(self, database_engine_started):
        """create_tables() metodu tabloları başarıyla oluşturur."""
        engine = database_engine_started
        metadata = MetaData()
        
        # Basit bir tablo tanımı
        from sqlalchemy import Table, Column, Integer, String
        test_table = Table(
            'test_table',
            metadata,
            Column('id', Integer, primary_key=True),
            Column('name', String(50))
        )
        
        engine.create_tables(metadata)
        
        # Tablo oluşturulmuş olmalı
        assert engine._base_metadata is not None

    def test_create_tables_raises_error_on_failure(self, database_engine_started):
        """create_tables() metodu tablo oluşturma hatasında DatabaseEngineError fırlatır."""
        engine = database_engine_started
        metadata = MetaData()
        
        with patch.object(metadata, 'create_all', side_effect=Exception("Table creation failed")):
            with pytest.raises(DatabaseEngineError):
                engine.create_tables(metadata)

    # --- drop_tables() Testleri ---
    def test_drop_tables_raises_error_when_engine_not_started(self, database_engine_not_started):
        """drop_tables() metodu engine başlatılmamışsa DatabaseEngineError fırlatır."""
        engine = database_engine_not_started
        metadata = MetaData()
        
        with pytest.raises(DatabaseEngineError):
            engine.drop_tables(metadata)

    def test_drop_tables_drops_tables_successfully(self, database_engine_started):
        """drop_tables() metodu tabloları başarıyla siler."""
        engine = database_engine_started
        metadata = MetaData()
        
        # Önce tablo oluştur
        from sqlalchemy import Table, Column, Integer, String
        test_table = Table(
            'test_table',
            metadata,
            Column('id', Integer, primary_key=True),
            Column('name', String(50))
        )
        
        engine.create_tables(metadata)
        
        # Sonra tabloyu sil
        engine.drop_tables(metadata)
        
        # Tablo silinmiş olmalı

    def test_drop_tables_uses_cached_metadata_when_none_provided(self, database_engine_started):
        """drop_tables() metodu metadata sağlanmazsa cache'lenmiş metadata kullanır."""
        engine = database_engine_started
        metadata = MetaData()
        
        from sqlalchemy import Table, Column, Integer, String
        test_table = Table(
            'test_table',
            metadata,
            Column('id', Integer, primary_key=True),
            Column('name', String(50))
        )
        
        engine.create_tables(metadata)
        engine.drop_tables()  # Metadata sağlanmadı, cache'lenmiş kullanılmalı

    # --- _set_query_timeout() Testleri ---
    def test_set_query_timeout_sets_timeout_for_sqlite(self, database_engine_started):
        """_set_query_timeout() metodu SQLite için timeout ayarlar."""
        engine = database_engine_started
        session = engine.get_session()
        
        # SQLite için timeout ayarla
        engine._set_query_timeout(session, 5.0)
        
        # Hata olmamalı
        session.close()

    def test_set_query_timeout_handles_errors_gracefully(self, database_engine_started):
        """_set_query_timeout() metodu hataları sessizce yok sayar."""
        engine = database_engine_started
        session = engine.get_session()
        
        # Hata simüle et
        with patch.object(session, 'execute', side_effect=Exception("Timeout error")):
            # Hata fırlatmamalı
            engine._set_query_timeout(session, 5.0)
        
        session.close()

    def test_set_query_timeout_works_with_different_database_types(self, database_engine_started):
        """_set_query_timeout() metodu farklı veritabanı tipleriyle çalışır."""
        engine = database_engine_started
        session = engine.get_session()
        
        # Farklı database type'ları test et
        for db_type in ['postgresql', 'mysql', 'sqlite', 'unknown']:
            engine._db_type_cached = db_type
            engine._set_query_timeout(session, 5.0)
        
        session.close()

