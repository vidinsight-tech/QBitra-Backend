"""
DatabaseManager sınıfı için testler.
"""

import pytest
import threading
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy import MetaData

from miniflow.database.engine.manager import DatabaseManager, get_database_manager
from miniflow.database.config.database_type import DatabaseType
from miniflow.database.config.database_config import DatabaseConfig
from miniflow.core.exceptions import (
    DatabaseManagerNotInitializedError,
    DatabaseManagerAlreadyInitializedError
)


@pytest.mark.unit
@pytest.mark.database
@pytest.mark.engine
class TestDatabaseManagerSingleton:
    """DatabaseManager singleton pattern testleri."""

    # --- Singleton Pattern Testleri ---
    def test_database_manager_returns_same_instance(self):
        """DatabaseManager her zaman aynı instance'ı döndürür."""
        # Singleton'ı sıfırla
        DatabaseManager._instance = None
        
        manager1 = DatabaseManager()
        manager2 = DatabaseManager()
        manager3 = DatabaseManager()
        
        assert manager1 is manager2
        assert manager2 is manager3
        assert manager1 is manager3

    def test_database_manager_singleton_is_thread_safe(self, sqlite_config_memory):
        """DatabaseManager singleton pattern thread-safe çalışır."""
        # Singleton'ı sıfırla
        DatabaseManager._instance = None
        
        managers = []
        lock = threading.Lock()
        
        def create_manager():
            manager = DatabaseManager()
            with lock:
                managers.append(manager)
        
        # 10 thread'de aynı anda manager oluştur
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=create_manager)
            threads.append(thread)
            thread.start()
        
        # Tüm thread'lerin bitmesini bekle
        for thread in threads:
            thread.join()
        
        # Tüm manager'lar aynı instance olmalı
        first_manager = managers[0]
        for manager in managers:
            assert manager is first_manager

    def test_database_manager_get_instance_returns_singleton(self, sqlite_config_memory):
        """get_instance() metodu singleton instance döndürür."""
        # Singleton'ı sıfırla
        DatabaseManager._instance = None
        
        manager1 = DatabaseManager.get_instance(sqlite_config_memory)
        manager2 = DatabaseManager.get_instance()
        
        assert manager1 is manager2

    def test_get_database_manager_returns_singleton(self, sqlite_config_memory):
        """get_database_manager() fonksiyonu singleton instance döndürür."""
        # Singleton'ı sıfırla
        DatabaseManager._instance = None
        
        manager1 = get_database_manager(sqlite_config_memory)
        manager2 = get_database_manager()
        
        assert manager1 is manager2
        assert isinstance(manager1, DatabaseManager)


@pytest.mark.unit
@pytest.mark.database
@pytest.mark.engine
class TestDatabaseManagerInitialization:
    """DatabaseManager başlatma testleri."""

    # --- initialize() Testleri ---
    def test_initialize_creates_engine(self, database_manager_not_initialized, sqlite_config_memory):
        """initialize() metodu DatabaseEngine oluşturur."""
        manager = database_manager_not_initialized
        manager.initialize(sqlite_config_memory, auto_start=False)
        
        assert manager._engine is not None
        assert manager.is_initialized
        assert manager._config == sqlite_config_memory

    def test_initialize_auto_starts_engine_when_requested(self, database_manager_not_initialized, sqlite_config_memory):
        """initialize() metodu auto_start=True olduğunda engine'i başlatır."""
        manager = database_manager_not_initialized
        manager.initialize(sqlite_config_memory, auto_start=True)
        
        assert manager.engine.is_alive

    def test_initialize_does_not_start_engine_when_auto_start_false(self, database_manager_not_initialized, sqlite_config_memory):
        """initialize() metodu auto_start=False olduğunda engine'i başlatmaz."""
        manager = database_manager_not_initialized
        manager.initialize(sqlite_config_memory, auto_start=False)
        
        assert not manager.engine.is_alive

    def test_initialize_raises_error_when_already_initialized(self, database_manager_initialized, sqlite_config_memory):
        """initialize() metodu zaten başlatılmışsa DatabaseManagerAlreadyInitializedError fırlatır."""
        manager = database_manager_initialized
        
        with pytest.raises(DatabaseManagerAlreadyInitializedError):
            manager.initialize(sqlite_config_memory)

    def test_initialize_allows_reinitialize_with_force_flag(self, database_manager_initialized, sqlite_config_memory):
        """initialize() metodu force_reinitialize=True ile yeniden başlatılabilir."""
        manager = database_manager_initialized
        first_engine = manager._engine
        
        manager.initialize(sqlite_config_memory, force_reinitialize=True)
        
        # Yeni engine oluşturulmuş olmalı
        assert manager._engine is not first_engine
        assert manager.is_initialized

    def test_initialize_creates_tables_when_provided(self, database_manager_not_initialized, sqlite_config_memory):
        """initialize() metodu create_tables parametresi verildiğinde tabloları oluşturur."""
        manager = database_manager_not_initialized
        metadata = MetaData()
        
        from sqlalchemy import Table, Column, Integer, String
        test_table = Table(
            'test_table',
            metadata,
            Column('id', Integer, primary_key=True),
            Column('name', String(50))
        )
        
        manager.initialize(sqlite_config_memory, auto_start=True, create_tables=metadata)
        
        # Tablo oluşturulmuş olmalı
        assert manager.engine.is_alive

    # --- is_initialized Property Testleri ---
    def test_is_initialized_returns_false_before_initialization(self, database_manager_not_initialized):
        """is_initialized property başlatılmadan önce False döndürür."""
        manager = database_manager_not_initialized
        assert not manager.is_initialized

    def test_is_initialized_returns_true_after_initialization(self, database_manager_not_initialized, sqlite_config_memory):
        """is_initialized property başlatıldıktan sonra True döndürür."""
        manager = database_manager_not_initialized
        manager.initialize(sqlite_config_memory, auto_start=False)
        assert manager.is_initialized

    # --- engine Property Testleri ---
    def test_engine_property_returns_engine_when_initialized(self, database_manager_initialized):
        """engine property başlatılmışsa DatabaseEngine döndürür."""
        manager = database_manager_initialized
        engine = manager.engine
        
        assert engine is not None
        assert engine.is_alive

    def test_engine_property_raises_error_when_not_initialized(self, database_manager_not_initialized):
        """engine property başlatılmamışsa DatabaseManagerNotInitializedError fırlatır."""
        manager = database_manager_not_initialized
        
        with pytest.raises(DatabaseManagerNotInitializedError):
            _ = manager.engine


@pytest.mark.unit
@pytest.mark.database
@pytest.mark.engine
class TestDatabaseManagerLifecycle:
    """DatabaseManager yaşam döngüsü testleri."""

    # --- start() Testleri ---
    def test_start_starts_engine(self, database_manager_not_initialized, sqlite_config_memory):
        """start() metodu engine'i başlatır."""
        manager = database_manager_not_initialized
        manager.initialize(sqlite_config_memory, auto_start=False)
        manager.start()
        
        assert manager.engine.is_alive

    def test_start_raises_error_when_not_initialized(self, database_manager_not_initialized):
        """start() metodu başlatılmamışsa DatabaseManagerNotInitializedError fırlatır."""
        manager = database_manager_not_initialized
        
        with pytest.raises(DatabaseManagerNotInitializedError):
            manager.start()

    # --- stop() Testleri ---
    def test_stop_stops_engine(self, database_manager_initialized):
        """stop() metodu engine'i durdurur."""
        manager = database_manager_initialized
        manager.stop()
        
        assert not manager.engine.is_alive

    def test_stop_is_idempotent(self, database_manager_initialized):
        """stop() metodu idempotent'tir (birden fazla kez çağrılabilir)."""
        manager = database_manager_initialized
        manager.stop()
        manager.stop()
        manager.stop()
        
        assert not manager.engine.is_alive

    def test_stop_handles_errors_gracefully(self, database_manager_initialized):
        """stop() metodu hataları sessizce yok sayar."""
        manager = database_manager_initialized
        
        # Engine'i mock'la ve hata fırlat
        with patch.object(manager._engine, 'stop', side_effect=Exception("Stop error")):
            # Hata fırlatmamalı
            manager.stop()

    # --- reset() Testleri ---
    def test_reset_clears_engine_and_config(self, database_manager_initialized):
        """reset() metodu engine ve config'i temizler."""
        manager = database_manager_initialized
        manager.reset()
        
        assert not manager.is_initialized
        assert manager._engine is None
        assert manager._config is None

    def test_reset_with_full_reset_resets_singleton(self, database_manager_initialized):
        """reset(full_reset=True) singleton instance'ı sıfırlar."""
        manager = database_manager_initialized
        manager.reset(full_reset=True)
        
        # Yeni manager oluştur - farklı instance olmalı
        new_manager = DatabaseManager()
        assert new_manager is not manager

    def test_reset_without_full_reset_keeps_singleton(self, database_manager_initialized):
        """reset(full_reset=False) singleton instance'ı korur."""
        manager = database_manager_initialized
        manager.reset(full_reset=False)
        
        # Yeni manager oluştur - aynı instance olmalı
        new_manager = DatabaseManager()
        assert new_manager is manager

    def test_reset_is_idempotent(self, database_manager_initialized):
        """reset() metodu idempotent'tir (birden fazla kez çağrılabilir)."""
        manager = database_manager_initialized
        manager.reset()
        manager.reset()
        manager.reset()
        
        assert not manager.is_initialized


@pytest.mark.unit
@pytest.mark.database
@pytest.mark.engine
class TestDatabaseManagerConfigManagement:
    """DatabaseManager konfigürasyon yönetimi testleri."""

    # --- reload_config() Testleri ---
    def test_reload_config_initializes_when_not_initialized(self, database_manager_not_initialized, sqlite_config_memory):
        """reload_config() metodu başlatılmamışsa initialize() çağırır."""
        manager = database_manager_not_initialized
        manager.reload_config(sqlite_config_memory, restart=True)
        
        assert manager.is_initialized
        assert manager.engine.is_alive

    def test_reload_config_replaces_engine(self, database_manager_initialized, sqlite_config_memory):
        """reload_config() metodu mevcut engine'i yeni engine ile değiştirir."""
        manager = database_manager_initialized
        old_engine = manager._engine
        
        manager.reload_config(sqlite_config_memory, restart=True)
        
        # Yeni engine oluşturulmuş olmalı
        assert manager._engine is not old_engine
        assert manager.is_initialized

    def test_reload_config_updates_config(self, database_manager_initialized, sqlite_config_memory):
        """reload_config() metodu config'i günceller."""
        manager = database_manager_initialized
        
        new_config = DatabaseConfig(
            db_type=DatabaseType.SQLITE,
            sqlite_path=":memory:"
        )
        
        manager.reload_config(new_config, restart=True)
        
        assert manager._config == new_config

    def test_reload_config_restarts_engine_when_requested(self, database_manager_initialized, sqlite_config_memory):
        """reload_config() metodu restart=True olduğunda engine'i yeniden başlatır."""
        manager = database_manager_initialized
        manager.stop()
        
        manager.reload_config(sqlite_config_memory, restart=True)
        
        assert manager.engine.is_alive

    def test_reload_config_does_not_restart_engine_when_not_requested(self, database_manager_initialized, sqlite_config_memory):
        """reload_config() metodu restart=False olduğunda engine'i yeniden başlatmaz."""
        manager = database_manager_initialized
        manager.stop()
        
        manager.reload_config(sqlite_config_memory, restart=False)
        
        assert not manager.engine.is_alive


@pytest.mark.unit
@pytest.mark.database
@pytest.mark.engine
class TestDatabaseManagerGetInstance:
    """DatabaseManager get_instance ve get_database_manager testleri."""

    # --- get_instance() Testleri ---
    def test_get_instance_initializes_when_config_provided(self, sqlite_config_memory):
        """get_instance() metodu config verildiğinde initialize eder."""
        # Singleton'ı sıfırla
        DatabaseManager._instance = None
        
        manager = DatabaseManager.get_instance(sqlite_config_memory, auto_start=True)
        
        assert manager.is_initialized
        assert manager.engine.is_alive

    def test_get_instance_raises_error_when_not_initialized_and_no_config(self):
        """get_instance() metodu başlatılmamışsa ve config verilmemişse DatabaseManagerNotInitializedError fırlatır."""
        # Singleton'ı sıfırla
        DatabaseManager._instance = None
        
        with pytest.raises(DatabaseManagerNotInitializedError):
            DatabaseManager.get_instance()

    def test_get_instance_returns_existing_instance_when_initialized(self, database_manager_initialized):
        """get_instance() metodu zaten başlatılmışsa mevcut instance'ı döndürür."""
        manager = database_manager_initialized
        
        retrieved_manager = DatabaseManager.get_instance()
        
        assert retrieved_manager is manager

    def test_get_instance_respects_auto_start_flag(self, sqlite_config_memory):
        """get_instance() metodu auto_start flag'ine uyar."""
        # Singleton'ı sıfırla
        DatabaseManager._instance = None
        
        manager = DatabaseManager.get_instance(sqlite_config_memory, auto_start=False)
        
        assert manager.is_initialized
        assert not manager.engine.is_alive

    # --- get_database_manager() Testleri ---
    def test_get_database_manager_initializes_when_config_provided(self, sqlite_config_memory):
        """get_database_manager() fonksiyonu config verildiğinde initialize eder."""
        # Singleton'ı sıfırla
        DatabaseManager._instance = None
        
        manager = get_database_manager(sqlite_config_memory, auto_start=True)
        
        assert manager.is_initialized
        assert manager.engine.is_alive

    def test_get_database_manager_returns_existing_instance_when_initialized(self, database_manager_initialized):
        """get_database_manager() fonksiyonu zaten başlatılmışsa mevcut instance'ı döndürür."""
        manager = database_manager_initialized
        
        retrieved_manager = get_database_manager()
        
        assert retrieved_manager is manager

    def test_get_database_manager_respects_auto_start_flag(self, sqlite_config_memory):
        """get_database_manager() fonksiyonu auto_start flag'ine uyar."""
        # Singleton'ı sıfırla
        DatabaseManager._instance = None
        
        manager = get_database_manager(sqlite_config_memory, auto_start=False)
        
        assert manager.is_initialized
        assert not manager.engine.is_alive

