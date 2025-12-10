"""
Yüksek Seviye Migration Komutları

Bu modül, yaygın migration işlemleri için kolaylık fonksiyonları sağlar.
Bu fonksiyonlar hem DatabaseEngine hem de DatabaseManager örnekleriyle çalışır.
"""

from typing import Optional, Union, TYPE_CHECKING

from miniflow.core.exceptions import DatabaseMigrationError

# MigrationManager mevcut olmayabilir - zarif şekilde handle et
try:
    from miniflow.database.migrations.manager import MigrationManager
except ImportError:
    # MigrationManager henüz implement edilmemiş
    MigrationManager = None

if TYPE_CHECKING:
    from miniflow.database.engine.engine import DatabaseEngine
    from miniflow.database.engine.manager import DatabaseManager
    EngineOrManager = Union['DatabaseEngine', 'DatabaseManager']


def run_migrations(
    engine_or_manager: 'EngineOrManager',
    revision: str = "head",
    script_location: str = "alembic"
) -> None:
    """Belirtilen revision'a migration'ları çalıştırır (kolaylık fonksiyonu).
    
    Bu, bir MigrationManager oluşturan ve migration'ları çalıştıran bir
    kolaylık fonksiyonudur. Esneklik için DatabaseEngine veya DatabaseManager
    örneği kabul eder.
    
    Args:
        engine_or_manager: DatabaseEngine veya DatabaseManager örneği
        revision: Hedef revision (varsayılan: "head" - en son)
        script_location: Alembic script konumu dizini
    
    Raises:
        DatabaseMigrationError: Geçersiz argüman veya migration başarısız olursa
    
    Örnekler:
        >>> # DatabaseEngine kullanarak
        >>> engine.start()
        >>> run_migrations(engine, revision="head")
        >>> 
        >>> # DatabaseManager kullanarak
        >>> manager.initialize(config, auto_start=True)
        >>> run_migrations(manager, revision="head")
    """
    if MigrationManager is None:
        raise ImportError(
            "MigrationManager mevcut değil. "
            "Alembic yüklü olmayabilir veya MigrationManager implementasyonu eksik. "
            "Yüklemek için: pip install alembic"
        )
    
    engine = _extract_engine(engine_or_manager)
    mgr = MigrationManager(engine, script_location=script_location)
    mgr.upgrade(revision)


def create_migration(
    engine_or_manager: 'EngineOrManager',
    message: str,
    autogenerate: bool = True,
    script_location: str = "alembic"
) -> str:
    """Yeni migration oluşturur (kolaylık fonksiyonu).
    
    Bu, bir MigrationManager oluşturan ve yeni bir migration dosyası
    oluşturan bir kolaylık fonksiyonudur.
    
    Args:
        engine_or_manager: DatabaseEngine veya DatabaseManager örneği
        message: Migration mesajı/açıklaması
        autogenerate: Modellerden otomatik migration oluştur (varsayılan: True)
        script_location: Alembic script konumu dizini
    
    Returns:
        Oluşturulan migration dosya yolu (bilgilendirme amaçlı)
    
    Raises:
        DatabaseMigrationError: Geçersiz argüman veya migration oluşturma başarısız olursa
    
    Örnekler:
        >>> # DatabaseManager ile migration oluştur
        >>> create_migration(manager, "add_user_table", autogenerate=True)
        >>> 
        >>> # Manuel migration oluştur
        >>> create_migration(engine, "custom_changes", autogenerate=False)
    """
    if MigrationManager is None:
        raise ImportError(
            "MigrationManager mevcut değil. "
            "Alembic yüklü olmayabilir veya MigrationManager implementasyonu eksik. "
            "Yüklemek için: pip install alembic"
        )
    
    engine = _extract_engine(engine_or_manager)
    mgr = MigrationManager(engine, script_location=script_location)
    return mgr.create_migration(message, autogenerate=autogenerate)


def get_current_revision(
    engine_or_manager: 'EngineOrManager',
    script_location: str = "alembic"
) -> Optional[str]:
    """Mevcut veritabanı revision'ını alır (kolaylık fonksiyonu).
    
    Bu, bir MigrationManager oluşturan ve mevcut veritabanı revision'ını
    alan bir kolaylık fonksiyonudur.
    
    Args:
        engine_or_manager: DatabaseEngine veya DatabaseManager örneği
        script_location: Alembic script konumu dizini
    
    Returns:
        Mevcut revision string'i veya migration uygulanmamışsa None
    
    Raises:
        DatabaseMigrationError: Geçersiz argüman veya revision alma başarısız olursa
    
    Örnekler:
        >>> # Mevcut revision'ı al
        >>> current = get_current_revision(manager)
        >>> if current:
        ...     print(f"Mevcut revision: {current}")
        >>> else:
        ...     print("Migration uygulanmamış")
    """
    if MigrationManager is None:
        raise ImportError(
            "MigrationManager mevcut değil. "
            "Alembic yüklü olmayabilir veya MigrationManager implementasyonu eksik. "
            "Yüklemek için: pip install alembic"
        )
    
    engine = _extract_engine(engine_or_manager)
    mgr = MigrationManager(engine, script_location=script_location)
    return mgr.get_current_revision()


def get_head_revision(
    engine_or_manager: 'EngineOrManager',
    script_location: str = "alembic"
) -> Optional[str]:
    """Head revision'ı (en son migration) alır (kolaylık fonksiyonu).
    
    Bu, bir MigrationManager oluşturan ve head (en son) migration revision'ını
    alan bir kolaylık fonksiyonudur.
    
    Args:
        engine_or_manager: DatabaseEngine veya DatabaseManager örneği
        script_location: Alembic script konumu dizini
    
    Returns:
        Head revision string'i veya migration yoksa None
    
    Raises:
        DatabaseMigrationError: Geçersiz argüman veya revision alma başarısız olursa
    
    Örnekler:
        >>> # Head revision'ı al
        >>> head = get_head_revision(manager)
        >>> print(f"En son migration: {head}")
    """
    if MigrationManager is None:
        raise ImportError(
            "MigrationManager mevcut değil. "
            "Alembic yüklü olmayabilir veya MigrationManager implementasyonu eksik. "
            "Yüklemek için: pip install alembic"
        )
    
    engine = _extract_engine(engine_or_manager)
    mgr = MigrationManager(engine, script_location=script_location)
    return mgr.get_head_revision()


def upgrade_dry_run(
    engine_or_manager: 'EngineOrManager',
    revision: str = "head",
    script_location: str = "alembic"
) -> str:
    """Dry-run upgrade - çalıştırılacak SQL'i gösterir (kolaylık fonksiyonu).
    
    Bu, bir dry-run upgrade gerçekleştiren ve çalıştırılacak SQL ifadelerini
    gösteren bir kolaylık fonksiyonudur. SQL ifadelerini gerçekten uygulamaz.
    
    Args:
        engine_or_manager: DatabaseEngine veya DatabaseManager örneği
        revision: Hedef revision (varsayılan: "head" - en son)
        script_location: Alembic script konumu dizini
    
    Returns:
        Çalıştırılacak SQL ifadeleri (string olarak)
    
    Raises:
        DatabaseMigrationError: Geçersiz argüman veya dry-run başarısız olursa
    
    Örnekler:
        >>> # Ne çalıştırılacağını gör
        >>> sql = upgrade_dry_run(manager, revision="head")
        >>> print(sql)
        >>> 
        >>> # Uygulamadan önce incele
        >>> if review_sql(sql):
        ...     run_migrations(manager, revision="head")
    """
    if MigrationManager is None:
        raise ImportError(
            "MigrationManager mevcut değil. "
            "Alembic yüklü olmayabilir veya MigrationManager implementasyonu eksik. "
            "Yüklemek için: pip install alembic"
        )
    
    engine = _extract_engine(engine_or_manager)
    mgr = MigrationManager(engine, script_location=script_location)
    return mgr.upgrade_dry_run(revision)


def upgrade_safe(
    engine_or_manager: 'EngineOrManager',
    revision: str = "head",
    verify: bool = True,
    script_location: str = "alembic"
) -> bool:
    """Doğrulama ile güvenli upgrade (kolaylık fonksiyonu).
    
    Bu, güvenlik kontrolleri ve doğrulama ile bir upgrade gerçekleştiren
    bir kolaylık fonksiyonudur.
    
    Args:
        engine_or_manager: DatabaseEngine veya DatabaseManager örneği
        revision: Hedef revision (varsayılan: "head" - en son)
        verify: Upgrade başarısını doğrula (varsayılan: True)
        script_location: Alembic script konumu dizini
    
    Returns:
        Upgrade başarılıysa True
    
    Raises:
        DatabaseMigrationError: Geçersiz argüman veya upgrade başarısız olursa
    """
    if MigrationManager is None:
        raise ImportError(
            "MigrationManager mevcut değil. "
            "Alembic yüklü olmayabilir veya MigrationManager implementasyonu eksik. "
            "Yüklemek için: pip install alembic"
        )
    
    engine = _extract_engine(engine_or_manager)
    mgr = MigrationManager(engine, script_location=script_location)
    return mgr.upgrade_safe(revision, verify=verify)


def _extract_engine(engine_or_manager: 'EngineOrManager') -> 'DatabaseEngine':
    """Argümandan DatabaseEngine'i çıkarır.
    
    Args:
        engine_or_manager: DatabaseEngine veya DatabaseManager örneği
    
    Returns:
        DatabaseEngine örneği
    
    Raises:
        DatabaseMigrationError: Geçersiz argüman tipi
    """
    # Circular import'ları önlemek için burada import et
    from miniflow.database.engine.engine import DatabaseEngine
    from miniflow.database.engine.manager import DatabaseManager
    
    if isinstance(engine_or_manager, DatabaseManager):
        return engine_or_manager.engine
    elif isinstance(engine_or_manager, DatabaseEngine):
        return engine_or_manager
    else:
        raise DatabaseMigrationError(
            message=f"Geçersiz argüman tipi. DatabaseEngine veya DatabaseManager bekleniyor, {type(engine_or_manager).__name__} alındı",
            operation="_extract_engine"
        )