"""
Alembic Başlatma Yardımcı Fonksiyonları

Bu modül, projede Alembic'i başlatmak için yardımcı fonksiyonlar sağlar.
"""

from pathlib import Path
from typing import Optional, Any, TYPE_CHECKING

from miniflow.core.exceptions import DatabaseMigrationError, DatabaseEngineError

# Alembic kullanılabilirliğini kontrol et
try:
    from alembic import config as alembic_config
    from alembic import command
    from alembic.config import Config as AlembicConfig
    ALEMBIC_AVAILABLE = True
except ImportError:
    ALEMBIC_AVAILABLE = False
    alembic_config = None
    command = None
    AlembicConfig = None

if TYPE_CHECKING:
    from miniflow.database.engine.engine import DatabaseEngine
    from sqlalchemy import MetaData


def init_alembic(
    script_location: str = "alembic",
    template: str = "generic",
    package: bool = False
) -> None:
    """Mevcut dizinde Alembic'i başlatır.
    
    Bu fonksiyon, Alembic'i gerekli dizin yapısını ve konfigürasyon dosyalarını
    oluşturarak başlatır.
    
    Args:
        script_location: Alembic script konumu dizini (varsayılan: "alembic")
        template: Kullanılacak Alembic şablonu (varsayılan: "generic")
        package: Python paketi olarak oluştur (varsayılan: False)
    
    Raises:
        DatabaseMigrationError: Alembic yüklü değilse veya başlatma başarısız olursa
    
    Örnekler:
        >>> # Temel başlatma
        >>> init_alembic()
        >>> 
        >>> # Özel konum
        >>> init_alembic(script_location="migrations")
        >>> 
        >>> # Paket olarak
        >>> init_alembic(package=True)
    
    Notlar:
        - Alembic yüklü olmalı (pip install alembic)
        - Alembic dizin yapısını oluşturur
        - env.py dosyasını modellerinizle manuel olarak güncellemeniz gerekebilir
    """
    if not ALEMBIC_AVAILABLE:
        raise DatabaseMigrationError(
            message="Alembic yüklü değil. Yüklemek için: pip install alembic",
            operation="init_alembic"
        )
    
    script_path = Path(script_location)
    
    if script_path.exists():
        raise DatabaseMigrationError(
            message=f"Alembic dizini zaten mevcut: {script_location}",
            operation="init_alembic"
        )
    
    try:
        # Alembic init için geçici bir config dosyası oluştur
        # Alembic'in init komutu bir config dosyası gerektirir
        import os
        from pathlib import Path as PathLib
        
        # Script location'ın parent dizininde geçici alembic.ini oluştur
        script_path = PathLib(script_location)
        parent_dir = script_path.parent if script_path.parent != script_path else PathLib.cwd()
        # Parent dizin yoksa oluştur
        parent_dir.mkdir(parents=True, exist_ok=True)
        temp_config_path = parent_dir / "alembic_temp.ini"
        
        # Geçici config dosyası oluştur
        temp_config_path.write_text("[alembic]\nscript_location = {}\n".format(script_location))
        
        try:
            config = AlembicConfig(str(temp_config_path))
            # Alembic'i başlat
            command.init(config, script_location, template=template, package=package)
        finally:
            # Geçici config dosyasını temizle
            if temp_config_path.exists():
                temp_config_path.unlink()
    except Exception as e:
        raise DatabaseMigrationError(
            message=f"Alembic başlatma başarısız: {e}",
            operation="init_alembic",
            original_error=e
        )


def init_alembic_auto(
    engine: 'DatabaseEngine',
    base_metadata: 'MetaData',
    script_location: str = "alembic",
    template: str = "generic",
    package: bool = False,
    models_import_path: Optional[str] = None
) -> None:
    """DatabaseEngine'den otomatik konfigürasyon ile Alembic'i başlatır.
    
    Bu fonksiyon, Alembic'i başlatır ve env.py dosyasını DatabaseEngine'in
    connection string'i ve base_metadata'sı ile otomatik olarak yapılandırır.
    Bu sayede manuel konfigürasyon gerekmez.
    
    Args:
        engine: DatabaseEngine örneği (başlatılmış olmalı)
        base_metadata: SQLAlchemy Base.metadata nesnesi
        script_location: Alembic script konumu dizini (varsayılan: "alembic")
        template: Kullanılacak Alembic şablonu (varsayılan: "generic")
        package: Python paketi olarak oluştur (varsayılan: False)
        models_import_path: Modeller için import path (örn: "myapp.models")
    
    Raises:
        DatabaseMigrationError: Alembic yüklü değilse veya başlatma başarısız olursa
        DatabaseEngineError: Engine başlatılmamışsa
    
    Örnekler:
        >>> from miniflow.database.engine import DatabaseManager
        >>> from database.models import Base
        >>> 
        >>> manager = DatabaseManager()
        >>> manager.initialize(config, auto_start=True)
        >>> 
        >>> # Alembic'i otomatik başlat
        >>> init_alembic_auto(
        ...     manager.engine, 
        ...     Base.metadata,
        ...     models_import_path="database.models"
        ... )
        >>> 
        >>> # Artık migration oluşturmaya hazır
        >>> from miniflow.database.migrations import create_migration
        >>> create_migration(manager, "initial_schema")
    
    Notlar:
        - Bu fonksiyon çağrılmadan önce engine başlatılmış olmalı
        - Tamamen yapılandırılmış bir Alembic kurulumu oluşturur
        - env.py connection string ve metadata ile otomatik yapılandırılır
        - Güvenlik için connection string environment variable ile saklanır
    """
    if not ALEMBIC_AVAILABLE:
        raise DatabaseMigrationError(
            message="Alembic yüklü değil. Yüklemek için: pip install alembic",
            operation="init_alembic_auto"
        )
    
    # Circular dependency'yi önlemek için burada import et
    from miniflow.database.engine.engine import DatabaseEngine
    
    if not isinstance(engine, DatabaseEngine):
        raise DatabaseMigrationError(
            message=f"Geçersiz engine tipi. DatabaseEngine bekleniyor, {type(engine).__name__} alındı",
            operation="init_alembic_auto"
        )
    
    if not engine.is_alive:
        raise DatabaseEngineError(
            message="Engine başlatılmamış. Önce engine.start() çağırın."
        )
    
    script_path = Path(script_location)
    
    if script_path.exists():
        raise DatabaseMigrationError(
            message=f"Alembic dizini zaten mevcut: {script_location}",
            operation="init_alembic_auto"
        )
    
    try:
        # Alembic'i başlat
        init_alembic(script_location=script_location, template=template, package=package)
        
        # env.py'yi otomatik yapılandır
        env_py_path = script_path / "env.py"
        
        if not env_py_path.exists():
            raise DatabaseMigrationError(
                message=f"env.py başlatma sonrası bulunamadı: {env_py_path}",
                operation="init_alembic_auto"
            )
        
        # Engine'den connection string oluştur
        connection_string = engine._connection_string
        
        # Models import path'i belirtilmemişse varsayılan kullan
        if models_import_path is None:
            # Metadata'nın bind'inden almayı dene veya varsayılan kullan
            models_import_path = "models"
        
        # Doğru konfigürasyon ile yeni env.py oluştur
        new_env_py = _generate_env_py_content(
            connection_string=connection_string,
            models_import_path=models_import_path
        )
        
        # Orijinali yedekle
        backup_path = env_py_path.with_suffix('.py.bak')
        env_py_path.rename(backup_path)
        
        # Yeni env.py'yi yaz
        env_py_path.write_text(new_env_py)
        
    except DatabaseMigrationError:
        raise
    except Exception as e:
        raise DatabaseMigrationError(
            message=f"Otomatik başlatma başarısız: {e}",
            operation="init_alembic_auto",
            original_error=e
        )


def _generate_env_py_content(
    connection_string: str,
    models_import_path: str
) -> str:
    """Otomatik konfigürasyon ile env.py içeriği oluşturur.
    
    Args:
        connection_string: Veritabanı connection string'i (fallback olarak kullanılır)
        models_import_path: Modeller modülü için import path
    
    Returns:
        Oluşturulmuş env.py içeriği
    """
    # Güvenlik için connection string'deki şifreyi maskele (fallback için)
    masked_connection_string = _mask_password_in_url(connection_string)
    
    env_py_template = '''"""
Otomatik oluşturulmuş Alembic ortam konfigürasyonu.

Bu dosya miniflow.database.migrations.init_alembic_auto() tarafından otomatik oluşturuldu.
Connection string ve metadata otomatik olarak yapılandırıldı.

GÜVENLİK NOTU: Kimlik bilgilerini açığa çıkarmamak için connection string'i
hardcode etmek yerine DATABASE_URL environment variable'ını kullanın.
"""

import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# Modellerinizin Base.metadata'sını buraya import edin
# Bu import path'i proje yapınıza uygun şekilde güncelleyin
try:
    from {models_import_path} import Base
    target_metadata = Base.metadata
except ImportError:
    # Fallback: yaygın pattern'leri dene
    try:
        from models import Base
        target_metadata = Base.metadata
    except ImportError:
        # Modeller import edilemezse None olarak ayarla
        # Bunu manuel olarak yapılandırmanız gerekecek
        target_metadata = None
        import warnings
        warnings.warn(
            "Modeller import edilemedi. Lütfen env.py'de target_metadata'yı manuel olarak ayarlayın"
        )

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Connection string'i environment variable'dan al (güvenlik için önerilir)
# Ayarlanmamışsa placeholder'a düşer
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "{masked_connection_string}"  # Bunu güncelleyin veya DATABASE_URL env var'ını ayarlayın
)
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# 'autogenerate' desteği için model'inizin MetaData nesnesini buraya ekleyin
# target_metadata = mymodel.Base.metadata

# env.py'nin ihtiyaçlarına göre tanımlanan config'deki diğer değerler
# şu şekilde alınabilir:
# my_important_option = config.get_main_option("my_important_option")
# ... vb.


def run_migrations_offline() -> None:
    """Migration'ları 'offline' modda çalıştır.

    Bu, context'i sadece bir URL ile yapılandırır
    ve bir Engine ile değil, ancak burada bir Engine de kabul edilebilir.
    Engine oluşturmayı atlayarak DBAPI'nin mevcut olmasına bile gerek yok.

    Buradaki context.execute() çağrıları verilen string'i
    script çıktısına yazar.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={{"paramstyle": "named"}},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Migration'ları 'online' modda çalıştır.

    Bu senaryoda bir Engine oluşturmamız
    ve context ile bir bağlantı ilişkilendirmemiz gerekir.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {{}}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
'''.format(
        models_import_path=models_import_path,
        masked_connection_string=masked_connection_string
    )
    
    return env_py_template


def _mask_password_in_url(url: str) -> str:
    """Güvenlik için veritabanı URL'indeki şifreyi maskeler.
    
    Args:
        url: Veritabanı connection URL'i
    
    Returns:
        Şifresi *** ile maskelenmiş URL
    """
    try:
        from urllib.parse import urlparse, urlunparse
        
        parsed = urlparse(url)
        
        if parsed.password:
            # Replace password with ***
            netloc = parsed.netloc.replace(f":{parsed.password}@", ":***@")
            masked = parsed._replace(netloc=netloc)
            return urlunparse(masked)
        
        return url
    except Exception:
        # If parsing fails, return placeholder
        return "postgresql://user:***@localhost/dbname"