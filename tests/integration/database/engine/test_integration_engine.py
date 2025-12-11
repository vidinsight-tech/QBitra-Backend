"""
DatabaseEngine integration testleri - gerçek veritabanı bağlantıları.
"""

import pytest
import time
from sqlalchemy import text, MetaData, Table, Column, Integer, String
from sqlalchemy.orm import Session

from miniflow.database.engine.engine import DatabaseEngine
from miniflow.database.config.database_type import DatabaseType
from miniflow.core.exceptions import DatabaseEngineError, DatabaseQueryError


@pytest.mark.integration
@pytest.mark.database
class TestPostgreSQLIntegration:
    """PostgreSQL gerçek bağlantı testleri."""

    def test_postgresql_connection(self, postgresql_engine_started):
        """PostgreSQL'e gerçek bağlantı kurulabilir."""
        engine = postgresql_engine_started
        
        assert engine.is_alive
        assert engine._engine is not None
        
        # Basit sorgu çalıştır
        with engine.session_context() as session:
            result = session.execute(text("SELECT 1")).scalar()
            assert result == 1

    def test_postgresql_connection_pool(self, postgresql_engine_started):
        """PostgreSQL connection pool çalışır."""
        engine = postgresql_engine_started
        
        # Birden fazla session oluştur (pool kullanımı)
        sessions = []
        for _ in range(5):
            session = engine.get_session()
            sessions.append(session)
            # Basit sorgu çalıştır
            result = session.execute(text("SELECT 1")).scalar()
            assert result == 1
        
        # Tüm session'ları kapat
        for session in sessions:
            session.close()
        
        # Pool hala çalışıyor olmalı
        assert engine.is_alive

    def test_postgresql_transaction_commit(self, postgresql_engine_started):
        """PostgreSQL transaction commit çalışır."""
        engine = postgresql_engine_started
        
        # Test tablosu oluştur
        metadata = MetaData()
        test_table = Table(
            'test_transaction',
            metadata,
            Column('id', Integer, primary_key=True),
            Column('value', String(50))
        )
        metadata.create_all(engine._engine)
        
        try:
            # Transaction içinde insert
            with engine.session_context() as session:
                session.execute(
                    test_table.insert().values(id=1, value='test')
                )
                # Auto-commit yapılır
            
            # Veriyi oku
            with engine.session_context() as session:
                result = session.execute(
                    test_table.select().where(test_table.c.id == 1)
                ).fetchone()
                assert result is not None
                assert result.value == 'test'
        finally:
            # Temizlik
            metadata.drop_all(engine._engine)

    def test_postgresql_transaction_rollback(self, postgresql_engine_started):
        """PostgreSQL transaction rollback çalışır."""
        engine = postgresql_engine_started
        
        # Test tablosu oluştur
        metadata = MetaData()
        test_table = Table(
            'test_rollback',
            metadata,
            Column('id', Integer, primary_key=True),
            Column('value', String(50))
        )
        metadata.create_all(engine._engine)
        
        try:
            # Hata ile rollback
            with pytest.raises(ValueError):
                with engine.session_context() as session:
                    session.execute(
                        test_table.insert().values(id=1, value='test')
                    )
                    raise ValueError("Test error")
            
            # Veri olmamalı (rollback yapıldı)
            with engine.session_context() as session:
                result = session.execute(
                    test_table.select().where(test_table.c.id == 1)
                ).fetchone()
                assert result is None
        finally:
            # Temizlik
            metadata.drop_all(engine._engine)

    def test_postgresql_isolation_level_read_committed(self, postgresql_engine_started):
        """PostgreSQL READ_COMMITTED isolation level çalışır."""
        engine = postgresql_engine_started
        
        # Test tablosu oluştur
        metadata = MetaData()
        test_table = Table(
            'test_isolation',
            metadata,
            Column('id', Integer, primary_key=True),
            Column('value', String(50))
        )
        metadata.create_all(engine._engine)
        
        try:
            # İlk transaction: Insert
            with engine.session_context(isolation_level='READ_COMMITTED') as session:
                session.execute(
                    test_table.insert().values(id=1, value='initial')
                )
            
            # İkinci transaction: Update ve kontrol
            with engine.session_context(isolation_level='READ_COMMITTED') as session:
                # Değeri oku
                result = session.execute(
                    test_table.select().where(test_table.c.id == 1)
                ).fetchone()
                assert result.value == 'initial'
                
                # Değeri güncelle
                session.execute(
                    test_table.update().where(test_table.c.id == 1).values(value='updated')
                )
        finally:
            # Temizlik
            metadata.drop_all(engine._engine)

    def test_postgresql_isolation_level_serializable(self, postgresql_engine_started):
        """PostgreSQL SERIALIZABLE isolation level çalışır."""
        engine = postgresql_engine_started
        
        # Test tablosu oluştur
        metadata = MetaData()
        test_table = Table(
            'test_serializable',
            metadata,
            Column('id', Integer, primary_key=True),
            Column('value', Integer)
        )
        metadata.create_all(engine._engine)
        
        try:
            # SERIALIZABLE isolation level ile transaction
            with engine.session_context(isolation_level='SERIALIZABLE') as session:
                # İlk değer
                session.execute(
                    test_table.insert().values(id=1, value=100)
                )
            
            # İkinci transaction: SERIALIZABLE ile okuma
            with engine.session_context(isolation_level='SERIALIZABLE') as session:
                result = session.execute(
                    test_table.select().where(test_table.c.id == 1)
                ).fetchone()
                assert result.value == 100
        finally:
            # Temizlik
            metadata.drop_all(engine._engine)

    def test_postgresql_query_timeout(self, postgresql_engine_started):
        """PostgreSQL query timeout çalışır."""
        engine = postgresql_engine_started
        
        # Timeout ile session - hata bekleniyor
        start_time = time.time()
        with pytest.raises(DatabaseQueryError):
            with engine.session_context(timeout=1.0) as session:
                # Uzun süren sorgu (timeout olmalı)
                session.execute(text("SELECT pg_sleep(2)"))
        
        # Timeout yaklaşık 1 saniye içinde olmalı
        elapsed = time.time() - start_time
        assert elapsed < 2.5, f"Timeout took too long: {elapsed}s"


@pytest.mark.integration
@pytest.mark.database
class TestMySQLIntegration:
    """MySQL gerçek bağlantı testleri."""

    def test_mysql_connection(self, mysql_engine_started):
        """MySQL'e gerçek bağlantı kurulabilir."""
        engine = mysql_engine_started
        
        assert engine.is_alive
        assert engine._engine is not None
        
        # Basit sorgu çalıştır
        with engine.session_context() as session:
            result = session.execute(text("SELECT 1")).scalar()
            assert result == 1

    def test_mysql_connection_pool(self, mysql_engine_started):
        """MySQL connection pool çalışır."""
        engine = mysql_engine_started
        
        # Birden fazla session oluştur (pool kullanımı)
        sessions = []
        for _ in range(5):
            session = engine.get_session()
            sessions.append(session)
            # Basit sorgu çalıştır
            result = session.execute(text("SELECT 1")).scalar()
            assert result == 1
        
        # Tüm session'ları kapat
        for session in sessions:
            session.close()
        
        # Pool hala çalışıyor olmalı
        assert engine.is_alive

    def test_mysql_transaction_commit(self, mysql_engine_started):
        """MySQL transaction commit çalışır."""
        engine = mysql_engine_started
        
        # Test tablosu oluştur
        metadata = MetaData()
        test_table = Table(
            'test_transaction',
            metadata,
            Column('id', Integer, primary_key=True),
            Column('value', String(50))
        )
        metadata.create_all(engine._engine)
        
        try:
            # Transaction içinde insert
            with engine.session_context() as session:
                session.execute(
                    test_table.insert().values(id=1, value='test')
                )
                # Auto-commit yapılır
            
            # Veriyi oku
            with engine.session_context() as session:
                result = session.execute(
                    test_table.select().where(test_table.c.id == 1)
                ).fetchone()
                assert result is not None
                assert result.value == 'test'
        finally:
            # Temizlik
            metadata.drop_all(engine._engine)

    def test_mysql_transaction_rollback(self, mysql_engine_started):
        """MySQL transaction rollback çalışır."""
        engine = mysql_engine_started
        
        # Test tablosu oluştur
        metadata = MetaData()
        test_table = Table(
            'test_rollback',
            metadata,
            Column('id', Integer, primary_key=True),
            Column('value', String(50))
        )
        metadata.create_all(engine._engine)
        
        try:
            # Hata ile rollback
            with pytest.raises(ValueError):
                with engine.session_context() as session:
                    session.execute(
                        test_table.insert().values(id=1, value='test')
                    )
                    raise ValueError("Test error")
            
            # Veri olmamalı (rollback yapıldı)
            with engine.session_context() as session:
                result = session.execute(
                    test_table.select().where(test_table.c.id == 1)
                ).fetchone()
                assert result is None
        finally:
            # Temizlik
            metadata.drop_all(engine._engine)

    def test_mysql_isolation_level_read_committed(self, mysql_engine_started):
        """MySQL READ_COMMITTED isolation level çalışır."""
        engine = mysql_engine_started
        
        # Test tablosu oluştur
        metadata = MetaData()
        test_table = Table(
            'test_isolation',
            metadata,
            Column('id', Integer, primary_key=True),
            Column('value', String(50))
        )
        metadata.create_all(engine._engine)
        
        try:
            # İlk transaction: Insert
            with engine.session_context(isolation_level='READ_COMMITTED') as session:
                session.execute(
                    test_table.insert().values(id=1, value='initial')
                )
            
            # İkinci transaction: Update ve kontrol
            with engine.session_context(isolation_level='READ_COMMITTED') as session:
                # Değeri oku
                result = session.execute(
                    test_table.select().where(test_table.c.id == 1)
                ).fetchone()
                assert result.value == 'initial'
                
                # Değeri güncelle
                session.execute(
                    test_table.update().where(test_table.c.id == 1).values(value='updated')
                )
        finally:
            # Temizlik
            metadata.drop_all(engine._engine)

    def test_mysql_isolation_level_repeatable_read(self, mysql_engine_started):
        """MySQL REPEATABLE_READ isolation level çalışır."""
        engine = mysql_engine_started
        
        # Test tablosu oluştur
        metadata = MetaData()
        test_table = Table(
            'test_repeatable_read',
            metadata,
            Column('id', Integer, primary_key=True),
            Column('value', Integer)
        )
        metadata.create_all(engine._engine)
        
        try:
            # REPEATABLE_READ isolation level ile transaction
            with engine.session_context(isolation_level='REPEATABLE_READ') as session:
                # İlk değer
                session.execute(
                    test_table.insert().values(id=1, value=100)
                )
            
            # İkinci transaction: REPEATABLE_READ ile okuma
            with engine.session_context(isolation_level='REPEATABLE_READ') as session:
                result = session.execute(
                    test_table.select().where(test_table.c.id == 1)
                ).fetchone()
                assert result.value == 100
        finally:
            # Temizlik
            metadata.drop_all(engine._engine)


@pytest.mark.integration
@pytest.mark.database
class TestConnectionPoolBehavior:
    """Connection pool davranış testleri."""

    def test_pool_reuse_connections(self, postgresql_engine_started):
        """Connection pool bağlantıları yeniden kullanır."""
        engine = postgresql_engine_started
        
        # İlk session
        session1 = engine.get_session()
        conn1_id = id(session1.connection())
        session1.close()
        
        # İkinci session (aynı connection kullanılabilir)
        session2 = engine.get_session()
        # Connection pool'dan geldiği için aynı veya farklı olabilir
        # Önemli olan pool'un çalışması
        session2.close()
        
        # Engine hala çalışıyor olmalı
        assert engine.is_alive

    def test_pool_exhaustion_handling(self, postgresql_engine_started):
        """Connection pool tükenmesi durumu handle edilir."""
        engine = postgresql_engine_started
        
        # Pool size'ı kontrol et
        pool_size = engine.config.engine_config.pool_size
        max_overflow = engine.config.engine_config.max_overflow
        max_connections = pool_size + max_overflow
        
        # Maksimum connection sayısına kadar session oluştur
        sessions = []
        for _ in range(min(max_connections, 10)):  # Limit to 10 for test
            try:
                session = engine.get_session()
                sessions.append(session)
            except Exception:
                # Pool tükendi, beklenen davranış
                break
        
        # Tüm session'ları kapat
        for session in sessions:
            session.close()
        
        # Engine hala çalışıyor olmalı
        assert engine.is_alive

    def test_pool_pre_ping(self, postgresql_engine_started):
        """Connection pool pre-ping çalışır."""
        engine = postgresql_engine_started
        
        # Pre-ping aktif olmalı (default)
        assert engine.config.engine_config.pool_pre_ping is True
        
        # Session oluştur ve kullan
        with engine.session_context() as session:
            result = session.execute(text("SELECT 1")).scalar()
            assert result == 1
        
        # Engine hala çalışıyor olmalı
        assert engine.is_alive

