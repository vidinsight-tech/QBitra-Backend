"""
Alembic Migration Manager

Bu modül, Alembic migration işlemlerini yönetmek için MigrationManager sınıfını sağlar.
DatabaseEngine ile entegre çalışır ve Alembic komutlarını yönetir.
"""

from pathlib import Path
from typing import Optional
from io import StringIO
import sys

from miniflow.database.engine.engine import DatabaseEngine
from miniflow.core.exceptions import DatabaseMigrationError, DatabaseEngineError

# Alembic kullanılabilirliğini kontrol et
try:
    from alembic.config import Config as AlembicConfig
    from alembic import command
    from alembic.script import ScriptDirectory
    from alembic.runtime.migration import MigrationContext
    ALEMBIC_AVAILABLE = True
except ImportError:
    ALEMBIC_AVAILABLE = False
    AlembicConfig = None
    command = None
    ScriptDirectory = None
    MigrationContext = None


class MigrationManager:
    """Alembic migration işlemlerini yöneten sınıf.
    
    Bu sınıf, DatabaseEngine ile entegre çalışarak Alembic migration
    işlemlerini kolaylaştırır. Migration oluşturma, uygulama ve sorgulama
    işlemlerini yönetir.
    
    Örnekler:
        >>> from miniflow.database.engine import DatabaseEngine
        >>> from miniflow.database.migrations.manager import MigrationManager
        >>> 
        >>> engine = DatabaseEngine(config)
        >>> engine.start()
        >>> 
        >>> manager = MigrationManager(engine, script_location="alembic")
        >>> manager.create_migration("initial_schema", autogenerate=True)
        >>> manager.upgrade("head")
    """
    
    def __init__(
        self,
        engine: DatabaseEngine,
        script_location: str = "alembic"
    ):
        """MigrationManager'ı başlatır.
        
        Args:
            engine: DatabaseEngine örneği (başlatılmış olmalı)
            script_location: Alembic script dizini (varsayılan: "alembic")
        
        Raises:
            DatabaseEngineError: Engine başlatılmamışsa
            DatabaseMigrationError: Script location mevcut değilse veya Alembic yüklü değilse
        """
        if not ALEMBIC_AVAILABLE:
            raise DatabaseMigrationError(
                message="Alembic yüklü değil. Yüklemek için: pip install alembic",
                operation="MigrationManager.__init__"
            )
        
        self._engine = engine
        self._script_location = Path(script_location)
        
        # Engine kontrolü
        self._validate_engine()
        
        # Script location kontrolü
        self._validate_script_location()
    
    def _validate_engine(self) -> None:
        """Engine'in başlatılmış olduğunu kontrol eder."""
        if not self._engine.is_alive:
            raise DatabaseEngineError(
                message="Engine başlatılmamış. Önce engine.start() çağırın."
            )
    
    def _validate_script_location(self) -> None:
        """Script location dizininin geçerli olduğunu kontrol eder."""
        if not self._script_location.exists():
            raise DatabaseMigrationError(
                message=f"Alembic script dizini bulunamadı: {self._script_location}",
                operation="MigrationManager.__init__"
            )
        
        env_py = self._script_location / "env.py"
        if not env_py.exists():
            raise DatabaseMigrationError(
                message=f"env.py dosyası bulunamadı: {env_py}. Alembic başlatılmamış olabilir.",
                operation="MigrationManager.__init__"
            )
    
    def _get_alembic_config(self) -> 'AlembicConfig':
        """Alembic Config nesnesi oluşturur ve yapılandırır.
        
        Returns:
            Yapılandırılmış AlembicConfig nesnesi
        
        Raises:
            DatabaseMigrationError: Config oluşturma başarısız olursa
        """
        try:
            # Alembic.ini dosyası var mı kontrol et
            alembic_ini = self._script_location.parent / "alembic.ini"
            
            if alembic_ini.exists():
                # Mevcut config dosyasını yükle
                config = AlembicConfig(str(alembic_ini))
            else:
                # Programatik config oluştur
                config = AlembicConfig()
                config.set_main_option("script_location", str(self._script_location))
            
            # Connection string'i engine'den al ve ayarla
            connection_string = self._engine._connection_string
            config.set_main_option("sqlalchemy.url", connection_string)
            
            return config
        except Exception as e:
            raise DatabaseMigrationError(
                message=f"Alembic config oluşturma başarısız: {e}",
                operation="_get_alembic_config",
                original_error=e
            )
    
    def upgrade(self, revision: str = "head") -> None:
        """Migration'ları belirtilen revision'a upgrade eder.
        
        Args:
            revision: Hedef revision (varsayılan: "head" - en son)
        
        Raises:
            DatabaseMigrationError: Upgrade başarısız olursa
        
        Örnekler:
            >>> manager.upgrade("head")
            >>> manager.upgrade("abc123")
        """
        try:
            config = self._get_alembic_config()
            command.upgrade(config, revision)
        except Exception as e:
            raise DatabaseMigrationError(
                message=f"Migration upgrade başarısız: {e}",
                operation="upgrade",
                original_error=e
            )
    
    def create_migration(
        self,
        message: str,
        autogenerate: bool = True
    ) -> str:
        """Yeni migration oluşturur.
        
        Args:
            message: Migration mesajı/açıklaması
            autogenerate: Modellerden otomatik migration oluştur (varsayılan: True)
        
        Returns:
            Oluşturulan migration dosya yolu (bilgilendirme amaçlı)
        
        Raises:
            DatabaseMigrationError: Migration oluşturma başarısız olursa
        
        Örnekler:
            >>> # Otomatik migration
            >>> path = manager.create_migration("add_users_table", autogenerate=True)
            >>> 
            >>> # Manuel migration
            >>> path = manager.create_migration("custom_changes", autogenerate=False)
        """
        try:
            config = self._get_alembic_config()
            
            if autogenerate:
                # Autogenerate ile revision oluştur
                command.revision(
                    config,
                    message=message,
                    autogenerate=True
                )
            else:
                # Manuel revision oluştur
                command.revision(config, message=message)
            
            # Oluşturulan migration dosyasını bul ve döndür
            script = ScriptDirectory.from_config(config)
            head = script.get_current_head()
            if head:
                revision_obj = script.get_revision(head)
                if revision_obj:
                    return str(revision_obj.path)
            
            # Head bulunamazsa script location'dan en son dosyayı bul
            versions_dir = self._script_location / "versions"
            if versions_dir.exists():
                migration_files = sorted(
                    versions_dir.glob("*.py"),
                    key=lambda p: p.stat().st_mtime,
                    reverse=True
                )
                if migration_files:
                    return str(migration_files[0])
            
            return ""
        except Exception as e:
            raise DatabaseMigrationError(
                message=f"Migration oluşturma başarısız: {e}",
                operation="create_migration",
                original_error=e
            )
    
    def get_current_revision(self) -> Optional[str]:
        """Mevcut veritabanı revision'ını alır.
        
        Returns:
            Mevcut revision string'i veya migration uygulanmamışsa None
        
        Raises:
            DatabaseMigrationError: Revision alma başarısız olursa
        
        Örnekler:
            >>> current = manager.get_current_revision()
            >>> if current:
            ...     print(f"Mevcut revision: {current}")
        """
        try:
            config = self._get_alembic_config()
            
            # Engine'den connection al
            with self._engine._engine.connect() as connection:
                context = MigrationContext.configure(connection)
                current_rev = context.get_current_revision()
                return current_rev
        except Exception as e:
            raise DatabaseMigrationError(
                message=f"Mevcut revision alma başarısız: {e}",
                operation="get_current_revision",
                original_error=e
            )
    
    def get_head_revision(self) -> Optional[str]:
        """Head (en son) revision'ı alır.
        
        Returns:
            Head revision string'i veya migration yoksa None
        
        Raises:
            DatabaseMigrationError: Head revision alma başarısız olursa
        
        Örnekler:
            >>> head = manager.get_head_revision()
            >>> print(f"En son migration: {head}")
        """
        try:
            config = self._get_alembic_config()
            script = ScriptDirectory.from_config(config)
            head = script.get_current_head()
            return head
        except Exception as e:
            raise DatabaseMigrationError(
                message=f"Head revision alma başarısız: {e}",
                operation="get_head_revision",
                original_error=e
            )
    
    def upgrade_dry_run(self, revision: str = "head") -> str:
        """Dry-run upgrade - çalıştırılacak SQL'i gösterir.
        
        Bu metod, migration'ları gerçekten uygulamadan önce çalıştırılacak
        SQL ifadelerini gösterir. Güvenlik için kullanılabilir.
        
        Args:
            revision: Hedef revision (varsayılan: "head" - en son)
        
        Returns:
            Çalıştırılacak SQL ifadeleri (string olarak)
        
        Raises:
            DatabaseMigrationError: Dry-run başarısız olursa
        
        Örnekler:
            >>> sql = manager.upgrade_dry_run("head")
            >>> print(sql)
        """
        try:
            config = self._get_alembic_config()
            
            # SQL çıktısını yakalamak için StringIO kullan
            output = StringIO()
            old_stdout = sys.stdout
            sys.stdout = output
            
            try:
                # SQL modunda upgrade (gerçekten uygulamaz)
                command.upgrade(config, revision, sql=True)
            finally:
                sys.stdout = old_stdout
            
            return output.getvalue()
        except Exception as e:
            raise DatabaseMigrationError(
                message=f"Dry-run upgrade başarısız: {e}",
                operation="upgrade_dry_run",
                original_error=e
            )
    
    def upgrade_safe(
        self,
        revision: str = "head",
        verify: bool = True
    ) -> bool:
        """Güvenli upgrade - doğrulama ile.
        
        Bu metod, upgrade işlemini gerçekleştirir ve isteğe bağlı olarak
        başarısını doğrular.
        
        Args:
            revision: Hedef revision (varsayılan: "head" - en son)
            verify: Upgrade başarısını doğrula (varsayılan: True)
        
        Returns:
            Upgrade başarılıysa True
        
        Raises:
            DatabaseMigrationError: Upgrade başarısız olursa
        
        Örnekler:
            >>> success = manager.upgrade_safe("head", verify=True)
            >>> if success:
            ...     print("Upgrade başarılı!")
        """
        try:
            # Upgrade yap
            self.upgrade(revision)
            
            # Doğrulama
            if verify:
                current = self.get_current_revision()
                if revision == "head":
                    head = self.get_head_revision()
                    return current == head
                else:
                    return current == revision
            
            return True
        except Exception as e:
            raise DatabaseMigrationError(
                message=f"Güvenli upgrade başarısız: {e}",
                operation="upgrade_safe",
                original_error=e
            )

