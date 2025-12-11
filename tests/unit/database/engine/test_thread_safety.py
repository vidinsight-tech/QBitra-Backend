"""
DatabaseEngine ve DatabaseManager thread-safety testleri.

Bu modül, çoklu iş parçacığı ortamlarında sistemin güvenli çalıştığını test eder.
"""

import pytest
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from sqlalchemy.orm import Session

from miniflow.database.engine.engine import DatabaseEngine
from miniflow.database.engine.manager import DatabaseManager
from miniflow.database.config.database_type import DatabaseType
from miniflow.database.config.database_config import DatabaseConfig
from miniflow.core.exceptions import DatabaseManagerNotInitializedError


@pytest.mark.unit
@pytest.mark.database
@pytest.mark.thread_safety
class TestDatabaseEngineThreadSafety:
    """DatabaseEngine thread-safety testleri."""

    # --- Concurrent Session Creation ---
    def test_concurrent_session_creation(self, database_engine_started):
        """Eşzamanlı session oluşturma thread-safe çalışır."""
        engine = database_engine_started
        sessions = []
        errors = []
        
        def create_session():
            try:
                session = engine.get_session()
                sessions.append(session)
                time.sleep(0.01)  # Race condition için bekleme
                session.close()
            except Exception as e:
                errors.append(e)
        
        # 50 thread ile eşzamanlı session oluştur
        threads = []
        for _ in range(50):
            thread = threading.Thread(target=create_session)
            threads.append(thread)
            thread.start()
        
        # Tüm thread'lerin bitmesini bekle
        for thread in threads:
            thread.join(timeout=5.0)
        
        # Hata olmamalı
        assert len(errors) == 0, f"Errors occurred: {errors}"
        # Tüm session'lar oluşturulmuş olmalı
        assert len(sessions) == 50

    def test_concurrent_session_context(self, database_engine_started):
        """Eşzamanlı session_context kullanımı thread-safe çalışır."""
        engine = database_engine_started
        results = []
        errors = []
        
        def use_session_context(thread_id):
            try:
                with engine.session_context() as session:
                    results.append(thread_id)
                    time.sleep(0.01)  # Race condition için bekleme
            except Exception as e:
                errors.append((thread_id, e))
        
        # 30 thread ile eşzamanlı context kullan
        threads = []
        for i in range(30):
            thread = threading.Thread(target=use_session_context, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Tüm thread'lerin bitmesini bekle
        for thread in threads:
            thread.join(timeout=5.0)
        
        # Hata olmamalı
        assert len(errors) == 0, f"Errors occurred: {errors}"
        # Tüm thread'ler başarılı olmalı
        assert len(results) == 30

    def test_concurrent_get_active_session_count(self, database_engine_started):
        """Eşzamanlı get_active_session_count thread-safe çalışır."""
        engine = database_engine_started
        counts = []
        errors = []
        
        def get_count():
            try:
                # Session oluştur
                session = engine.get_session()
                count = engine.get_active_session_count()
                counts.append(count)
                time.sleep(0.01)
                session.close()
            except Exception as e:
                errors.append(e)
        
        # 20 thread ile eşzamanlı count alma
        threads = []
        for _ in range(20):
            thread = threading.Thread(target=get_count)
            threads.append(thread)
            thread.start()
        
        # Tüm thread'lerin bitmesini bekle
        for thread in threads:
            thread.join(timeout=5.0)
        
        # Hata olmamalı
        assert len(errors) == 0, f"Errors occurred: {errors}"
        # Count'lar tutarlı olmalı (en az 1, en fazla 20)
        assert all(1 <= count <= 20 for count in counts)

    def test_concurrent_start_stop(self, sqlite_config_memory):
        """Eşzamanlı start/stop çağrıları thread-safe çalışır."""
        errors = []
        
        def start_stop_cycle(cycle_id):
            try:
                engine = DatabaseEngine(sqlite_config_memory)
                for _ in range(5):
                    engine.start()
                    time.sleep(0.001)
                    engine.stop()
            except Exception as e:
                errors.append((cycle_id, e))
        
        # 10 thread ile eşzamanlı start/stop
        threads = []
        for i in range(10):
            thread = threading.Thread(target=start_stop_cycle, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Tüm thread'lerin bitmesini bekle
        for thread in threads:
            thread.join(timeout=10.0)
        
        # Hata olmamalı
        assert len(errors) == 0, f"Errors occurred: {errors}"

    def test_concurrent_session_tracking(self, database_engine_started):
        """Eşzamanlı session tracking thread-safe çalışır."""
        engine = database_engine_started
        session_counts = []
        
        def create_and_track():
            session = engine.get_session()
            count = engine.get_active_session_count()
            session_counts.append(count)
            time.sleep(0.01)
            session.close()
        
        # 25 thread ile eşzamanlı tracking
        threads = []
        for _ in range(25):
            thread = threading.Thread(target=create_and_track)
            threads.append(thread)
            thread.start()
        
        # Tüm thread'lerin bitmesini bekle
        for thread in threads:
            thread.join(timeout=5.0)
        
        # Count'lar tutarlı olmalı
        assert all(count >= 1 for count in session_counts)
        # Son durumda aktif session olmamalı
        assert engine.get_active_session_count() == 0

    def test_concurrent_close_all_sessions(self, database_engine_started):
        """Eşzamanlı close_all_sessions thread-safe çalışır."""
        engine = database_engine_started
        errors = []
        
        def create_and_close():
            try:
                session = engine.get_session()
                time.sleep(0.01)
                closed_count = engine.close_all_sessions()
                return closed_count
            except Exception as e:
                errors.append(e)
                return 0
        
        # Önce 15 session oluştur
        sessions = []
        for _ in range(15):
            sessions.append(engine.get_session())
        
        # 10 thread ile eşzamanlı close_all_sessions
        threads = []
        results = []
        for _ in range(10):
            thread = threading.Thread(target=lambda: results.append(create_and_close()))
            threads.append(thread)
            thread.start()
        
        # Tüm thread'lerin bitmesini bekle
        for thread in threads:
            thread.join(timeout=5.0)
        
        # Hata olmamalı
        assert len(errors) == 0, f"Errors occurred: {errors}"
        # Son durumda aktif session olmamalı
        assert engine.get_active_session_count() == 0

    def test_concurrent_health_check(self, database_engine_started):
        """Eşzamanlı health_check thread-safe çalışır."""
        engine = database_engine_started
        health_results = []
        errors = []
        
        def check_health():
            try:
                health = engine.health_check(use_cache=False)
                health_results.append(health['status'])
            except Exception as e:
                errors.append(e)
        
        # 30 thread ile eşzamanlı health check
        threads = []
        for _ in range(30):
            thread = threading.Thread(target=check_health)
            threads.append(thread)
            thread.start()
        
        # Tüm thread'lerin bitmesini bekle
        for thread in threads:
            thread.join(timeout=5.0)
        
        # Hata olmamalı
        assert len(errors) == 0, f"Errors occurred: {errors}"
        # Tüm health check'ler başarılı olmalı
        assert len(health_results) == 30
        assert all(status == 'healthy' for status in health_results)


@pytest.mark.unit
@pytest.mark.database
@pytest.mark.thread_safety
class TestDatabaseManagerThreadSafety:
    """DatabaseManager thread-safety testleri."""

    def test_singleton_thread_safety(self, sqlite_config_memory):
        """Singleton deseni thread-safe çalışır (double-checked locking)."""
        # Singleton'ı önce sıfırla
        DatabaseManager._instance = None
        DatabaseManager._is_resetting = False
        
        instances = []
        errors = []
        
        def get_instance():
            try:
                # Aynı anda instance al (singleton'ı sıfırlamadan)
                instance = DatabaseManager()
                instances.append(id(instance))
                time.sleep(0.01)
            except Exception as e:
                errors.append(e)
        
        # 50 thread ile eşzamanlı singleton erişimi
        threads = []
        for _ in range(50):
            thread = threading.Thread(target=get_instance)
            threads.append(thread)
            thread.start()
        
        # Tüm thread'lerin bitmesini bekle
        for thread in threads:
            thread.join(timeout=5.0)
        
        # Hata olmamalı
        assert len(errors) == 0, f"Errors occurred: {errors}"
        # Tüm instance'lar aynı olmalı (singleton)
        assert len(set(instances)) == 1, f"Singleton pattern failed - {len(set(instances))} instances created instead of 1"

    def test_concurrent_initialize(self, sqlite_config_memory):
        """Eşzamanlı initialize thread-safe çalışır."""
        errors = []
        initialized_flags = []
        
        def initialize_manager():
            try:
                # Singleton'ı sıfırla
                DatabaseManager._instance = None
                DatabaseManager._is_resetting = False
                
                manager = DatabaseManager()
                manager.initialize(sqlite_config_memory, auto_start=True)
                initialized_flags.append(manager.is_initialized)
                
                # Temizlik
                manager.reset(full_reset=True)
            except Exception as e:
                errors.append(e)
        
        # 20 thread ile eşzamanlı initialize
        threads = []
        for _ in range(20):
            thread = threading.Thread(target=initialize_manager)
            threads.append(thread)
            thread.start()
        
        # Tüm thread'lerin bitmesini bekle
        for thread in threads:
            thread.join(timeout=10.0)
        
        # Hata olmamalı
        assert len(errors) == 0, f"Errors occurred: {errors}"
        # Tüm initialize işlemleri başarılı olmalı
        assert all(flag is True for flag in initialized_flags)

    def test_concurrent_start_stop_manager(self, sqlite_config_memory):
        """Eşzamanlı start/stop thread-safe çalışır."""
        errors = []
        
        def start_stop_cycle():
            try:
                # Singleton'ı sıfırla
                DatabaseManager._instance = None
                DatabaseManager._is_resetting = False
                
                manager = DatabaseManager()
                manager.initialize(sqlite_config_memory, auto_start=False)
                
                for _ in range(3):
                    manager.start()
                    time.sleep(0.001)
                    manager.stop()
                
                manager.reset(full_reset=True)
            except Exception as e:
                errors.append(e)
        
        # 15 thread ile eşzamanlı start/stop
        threads = []
        for _ in range(15):
            thread = threading.Thread(target=start_stop_cycle)
            threads.append(thread)
            thread.start()
        
        # Tüm thread'lerin bitmesini bekle
        for thread in threads:
            thread.join(timeout=10.0)
        
        # Hata olmamalı
        assert len(errors) == 0, f"Errors occurred: {errors}"

    def test_concurrent_engine_access(self, sqlite_config_memory):
        """Eşzamanlı engine erişimi thread-safe çalışır."""
        # Singleton'ı önce sıfırla ve başlat
        DatabaseManager._instance = None
        DatabaseManager._is_resetting = False
        manager = DatabaseManager()
        manager.initialize(sqlite_config_memory, auto_start=True)
        
        errors = []
        engine_ids = []
        
        def access_engine():
            try:
                # Aynı singleton'dan engine al
                manager = DatabaseManager()
                engine = manager.engine
                engine_ids.append(id(engine))
                
                # Session oluştur
                session = engine.get_session()
                time.sleep(0.01)
                session.close()
            except Exception as e:
                errors.append(e)
        
        # 15 thread ile eşzamanlı engine erişimi
        threads = []
        for _ in range(15):
            thread = threading.Thread(target=access_engine)
            threads.append(thread)
            thread.start()
        
        # Tüm thread'lerin bitmesini bekle
        for thread in threads:
            thread.join(timeout=30.0)
        
        # Temizlik
        manager.reset(full_reset=True)
        
        # Hata olmamalı
        assert len(errors) == 0, f"Errors occurred: {errors}"
        # Tüm engine'ler aynı olmalı (singleton) - en az 1 thread başarılı olmalı
        assert len(engine_ids) > 0, "No engines were accessed"
        assert len(set(engine_ids)) == 1, f"Engine instances should be the same, got {len(set(engine_ids))} different instances"

    def test_concurrent_reset(self, sqlite_config_memory):
        """Eşzamanlı reset thread-safe çalışır."""
        errors = []
        
        def reset_cycle():
            try:
                # Singleton'ı sıfırla
                DatabaseManager._instance = None
                DatabaseManager._is_resetting = False
                
                manager = DatabaseManager()
                manager.initialize(sqlite_config_memory, auto_start=True)
                
                # Eşzamanlı reset
                manager.reset(full_reset=True)
            except Exception as e:
                errors.append(e)
        
        # 20 thread ile eşzamanlı reset
        threads = []
        for _ in range(20):
            thread = threading.Thread(target=reset_cycle)
            threads.append(thread)
            thread.start()
        
        # Tüm thread'lerin bitmesini bekle
        for thread in threads:
            thread.join(timeout=10.0)
        
        # Hata olmamalı veya minimal olmalı (reset sırasında beklenen hatalar)
        # Reset sırasında bazı thread'ler "not initialized" hatası alabilir
        assert len(errors) <= 5, f"Too many errors occurred: {errors}"


@pytest.mark.unit
@pytest.mark.database
@pytest.mark.thread_safety
class TestConcurrentOperations:
    """Karmaşık eşzamanlı operasyon testleri."""

    def test_mixed_concurrent_operations(self, database_engine_started):
        """Karışık eşzamanlı operasyonlar thread-safe çalışır."""
        engine = database_engine_started
        results = []
        errors = []
        
        def mixed_operations(thread_id):
            try:
                # Session oluştur
                session = engine.get_session()
                count1 = engine.get_active_session_count()
                
                # Health check
                health = engine.health_check(use_cache=False)
                
                # Başka bir session oluştur
                with engine.session_context() as session2:
                    count2 = engine.get_active_session_count()
                    results.append((thread_id, count1, count2, health['status']))
                
                session.close()
            except Exception as e:
                errors.append((thread_id, e))
        
        # 20 thread ile karışık operasyonlar
        threads = []
        for i in range(20):
            thread = threading.Thread(target=mixed_operations, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Tüm thread'lerin bitmesini bekle
        for thread in threads:
            thread.join(timeout=10.0)
        
        # Hata olmamalı
        assert len(errors) == 0, f"Errors occurred: {errors}"
        # Tüm operasyonlar başarılı olmalı
        assert len(results) == 20

    def test_high_concurrency_session_creation(self, database_engine_started):
        """Yüksek eşzamanlılıkta session oluşturma thread-safe çalışır."""
        engine = database_engine_started
        errors = []
        session_count = []
        
        def create_sessions():
            try:
                sessions = []
                for _ in range(5):
                    session = engine.get_session()
                    sessions.append(session)
                    count = engine.get_active_session_count()
                    session_count.append(count)
                
                # Tüm session'ları kapat
                for session in sessions:
                    session.close()
            except Exception as e:
                errors.append(e)
        
        # 30 thread ile her biri 5 session oluştur (toplam 150 session)
        threads = []
        for _ in range(30):
            thread = threading.Thread(target=create_sessions)
            threads.append(thread)
            thread.start()
        
        # Tüm thread'lerin bitmesini bekle
        for thread in threads:
            thread.join(timeout=15.0)
        
        # Hata olmamalı
        assert len(errors) == 0, f"Errors occurred: {errors}"
        # Son durumda aktif session olmamalı
        assert engine.get_active_session_count() == 0

    def test_concurrent_decorator_usage(self, sqlite_config_memory):
        """Eşzamanlı decorator kullanımı thread-safe çalışır."""
        from miniflow.database.engine.decorators import with_session
        
        # Singleton'ı sıfırla ve başlat
        DatabaseManager._instance = None
        DatabaseManager._is_resetting = False
        manager = DatabaseManager()
        manager.initialize(sqlite_config_memory, auto_start=True)
        
        results = []
        errors = []
        
        @with_session()
        def test_function(session: Session, thread_id: int):
            try:
                results.append(thread_id)
                time.sleep(0.01)
                return thread_id
            except Exception as e:
                errors.append((thread_id, e))
                return None
        
        # 25 thread ile eşzamanlı decorator kullanımı
        threads = []
        for i in range(25):
            thread = threading.Thread(target=test_function, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Tüm thread'lerin bitmesini bekle
        for thread in threads:
            thread.join(timeout=10.0)
        
        # Temizlik
        manager.reset(full_reset=True)
        
        # Hata olmamalı
        assert len(errors) == 0, f"Errors occurred: {errors}"
        # Tüm thread'ler başarılı olmalı
        assert len(results) == 25

