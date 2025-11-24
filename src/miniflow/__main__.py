import sys
from typing import Optional
from sqlalchemy import text, inspect

from seeds.workflow_plan_seeds import WORKSPACE_PLANS_SEED
from seeds.user_role_seeds import USER_ROLES_SEED
from seeds.agreement_seeds import AGREEMENT_SEEDS

from src.miniflow.utils import EnvironmentHandler, ConfigurationHandler, RedisClient
from src.miniflow.core.exceptions import InvalidInputError, ResourceNotFoundError, InternalError
from src.miniflow.database import get_sqlite_config, get_postgresql_config, get_mysql_config
from src.miniflow.database import DatabaseManager
from src.miniflow.utils.helpers.file_helper import create_resources_folder
from src.miniflow.services.info_services.user_roles_service import UserRolesService
from src.miniflow.services.info_services.workspace_plans_service import WorkspacePlansService
from src.miniflow.services.info_services.agreement_service import AgreementService


class MiniFlow:
    def __init__(self):
        # Ortam ve veritabanı tipi (henüz initialize edilmemiş)
        self._app_env: Optional[str] = None
        self._db_type: Optional[str] = None

        # Database Manager
        self._db_manager: Optional[DatabaseManager] = None

        # Çalışma Durumu
        self.is_running = False

        # Seed Services (lazy initialization)
        self._user_role_service: Optional[UserRolesService] = None
        self._workspace_plan_service: Optional[WorkspacePlansService] = None
        self._agreement_service: Optional[AgreementService] = None

        # Başlatma işlemleri
        self._startup_initialization()

    def _startup_initialization(self):
        """Uygulama başlatma işlemlerini yürütür"""
        # 1. Configuration'ları yükle
        self._setup_config()
        
        # 2. Ortam ve veritabanı tipini ayarla
        self._app_env = EnvironmentHandler.get("APP_ENV", "").lower()
        self._db_type = EnvironmentHandler.get("DB_TYPE", "").lower()
        
        if not self._app_env:
            raise InternalError(
                component_name="miniflow",
                message="APP_ENV environment variable is not set."
            )
        
        if not self._db_type:
            raise InternalError(
                component_name="miniflow",
                message="DB_TYPE environment variable is not set."
            )

    @property
    def _env(self):
        """EnvironmentHandler'a erişim için property"""
        return EnvironmentHandler

    @property
    def _config(self):
        """ConfigurationHandler'a erişim için property"""
        return ConfigurationHandler

    def _setup_config(self):
        """Initialize application configuration, environment, and external services."""
        print("\n" + "=" * 70)
        print("MINIFLOW STARTUP INITIALIZATION".center(70))
        print("=" * 70 + "\n")

        try:
            # 1. Load environment variables
            print("[1/4] Loading environment variables...", end=" ", flush=True)
            EnvironmentHandler.load_env()
            print("✓ OK")
            
            # 2. Load configuration files
            print("[2/4] Loading configuration files...", end=" ", flush=True)
            ConfigurationHandler.load_config()
            print("✓ OK")
            
            # 3. Initialize Redis connection
            print("[3/4] Initializing Redis connection...", end=" ", flush=True)
            RedisClient.initialize()
            print("✓ OK")

            # 4. Files
            print("[4/4] Initializing Redis connection...", end=" ", flush=True)
            create_resources_folder()
            print("✓ OK")

            
            print("\n" + "=" * 70)
            print("STARTUP INITIALIZATION COMPLETED SUCCESSFULLY".center(70))
            print("=" * 70 + "\n")
            
        except ResourceNotFoundError as e:
            self._print_error_header("RESOURCE NOT FOUND")
            print(f"Error: {e.error_message}")
            resource_info = f"{e.resource_name}"
            if e.resource_id:
                resource_info += f" (ID: {e.resource_id})"
            print(f"Resource: {resource_info}")
            if e.error_details:
                print(f"Details: {e.error_details}")
            print("\n" + "-" * 70)
            print("Troubleshooting:")
            print("  • Verify the resource path and file permissions")
            print("  • Check if the resource exists in the expected location")
            print("  • Ensure proper file/directory access rights")
            print("-" * 70)
            sys.exit(1)
        
        except InternalError as e:
            self._print_error_header("INITIALIZATION ERROR")
            print(f"Component: {e.component_name}")
            print(f"Error: {e.error_message}")
            
            if e.error_details:
                if isinstance(e.error_details, dict):
                    if 'host' in e.error_details and 'port' in e.error_details:
                        print(f"Redis Address: {e.error_details['host']}:{e.error_details['port']}")
                    elif 'original_error' in e.error_details:
                        print(f"Original Error: {e.error_details['original_error']}")
                    else:
                        print(f"Details: {e.error_details}")
                else:
                    print(f"Details: {e.error_details}")
            
            print("\n" + "-" * 70)
            print("Troubleshooting:")
            
            if e.component_name == "environment_handler":
                print("  • Verify environment variables are correctly set")
                print("  • Check .env file exists in the project root")
                print("  • Ensure TEST_KEY is set to 'ThisKeyIsForConfigTest'")
                print("  • Verify environment file path is correct")
            elif e.component_name == "configuration_handler":
                print("  • Verify configuration files exist in 'configurations/' directory")
                print("  • Check configuration file format (INI format)")
                print("  • Ensure [Test] section with value='ThisKeyIsForConfigTest' exists")
                print("  • Verify APP_ENV matches available config files (dev/prod/local/test)")
            elif e.component_name == "redis_client":
                print("  • Verify Redis server is running (redis-server)")
                print("  • Check Redis host and port settings in configuration")
                print("  • Ensure firewall allows Redis port access")
                print("  • Test connection: redis-cli ping")
            elif e.component_name == "database_manager":
                print("  • Verify database configuration settings")
                print("  • Check database server is running and accessible")
                print("  • Ensure database credentials are correct")
                print("  • Verify database connection string format")
            else:
                print("  • Review application logs for detailed error information")
                print("  • Contact system administrator if issue persists")
            
            print("-" * 70)
            sys.exit(1)
        
        except Exception as e:
            self._print_error_header("UNEXPECTED ERROR")
            print(f"Error Type: {type(e).__name__}")
            print(f"Error Message: {str(e)}")
            print("\n" + "-" * 70)
            print("An unexpected error occurred during startup initialization.")
            print("Please review the application logs and contact system administrator.")
            print("-" * 70)
            sys.exit(1)


    @property
    def is_development(self) -> bool:
        """Development ortamında mı?"""
        return 'dev' in self._app_env

    @property
    def is_production(self) -> bool:
        """Production ortamında mı?"""
        return 'prod' in self._app_env
    
    def _get_db_config(self):
        """Veritabanı yapılandırmasını oluştur"""
        if self._db_type == "sqlite":
            sqlite_path = self._config.get("Database", "db_path", "./miniflow.db")
            return get_sqlite_config(database_name=sqlite_path)
        
        elif self._db_type == "postgresql":
            params = {
                'database_name': self._config.get("Database", "db_name", "miniflow"),
                'host': self._config.get("Database", "db_host", "localhost"),
                'port': self._config.get_int("Database", "db_port", 5432),
                'username': self._config.get("Database", "db_user", "postgres"),
                'password': self._config.get("Database", "db_password", ""),
            }
            return get_postgresql_config(**params)
        
        elif self._db_type == "mysql":
            params = {
                'database_name': self._config.get("Database", "db_name", "miniflow"),
                'host': self._config.get("Database", "db_host", "localhost"),
                'port': self._config.get_int("Database", "db_port", 3306),
                'username': self._config.get("Database", "db_user", "root"),
                'password': self._config.get("Database", "db_password", ""),
            }
            return get_mysql_config(**params)
        else:
            raise InvalidInputError(field_name="DB_TYPE")
        
    def _get_or_start_db_manager(self) -> Optional[DatabaseManager]:
        """Initialize and return DatabaseManager instance."""
        manager = DatabaseManager()
        if manager.is_initialized:
            print("[DATABASE] Database Manager already initialized")
            return manager
        else:
            try:
                print("[DATABASE] Initializing Database Manager...", end=" ", flush=True)
                config = self._get_db_config()
                manager.initialize(config, auto_start=True, create_tables=True)
                if manager.is_initialized:
                    print("✓ OK")
                    return manager
                else:
                    raise InternalError(
                        component_name="database_manager",
                        message="Database Manager initialization failed. Manager is not initialized after initialize() call."
                    )
            except InternalError:
                raise
            except Exception as e:
                raise InternalError(
                    component_name="database_manager",
                    message=f"Failed to initialize Database Manager: {str(e)}",
                    error_details={"original_error": str(e), "error_type": type(e).__name__}
                )
            
    def _test_database_connection(self) -> bool:
        """Test database connection and verify tables exist."""
        if not self._db_manager or not self._db_manager.is_initialized:
            raise RuntimeError("Database Manager is not initialized. Call _get_or_start_db_manager() first.")
        
        engine = self._db_manager.engine._engine
        try: 
            print("[DATABASE] Testing connection...", end=" ", flush=True)
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
                inspector = inspect(engine)
                tables = inspector.get_table_names()
                table_count = len(tables)
                if table_count > 0:
                    print(f"✓ OK ({table_count} tables found)")
                    return True
                else:
                    print("⚠ WARNING (no tables found)")
                    return False
        except Exception as e:
            print(f"✗ FAILED")
            print(f"[DATABASE] Connection test error: {type(e).__name__}: {str(e)}")
            return False
    
    def _setup_database(self):
        """Initialize database manager and test connection."""
        print("\n" + "=" * 70)
        print("DATABASE INITIALIZATION".center(70))
        print("=" * 70 + "\n")

        try:
            # Initialize Database Manager
            self._db_manager = self._get_or_start_db_manager()
            
            # Test database connection
            connection_ok = self._test_database_connection()
            
            if connection_ok:
                print("\n" + "=" * 70)
                print("DATABASE INITIALIZATION COMPLETED SUCCESSFULLY".center(70))
                print("=" * 70 + "\n")
            else:
                print("\n" + "-" * 70)
                print("⚠ WARNING: Database connection test completed with warnings")
                print("-" * 70 + "\n")
                
        except InternalError as e:
            self._print_error_header("DATABASE INITIALIZATION ERROR")
            print(f"Component: {e.component_name}")
            print(f"Error: {e.error_message}")
            
            if e.error_details:
                if isinstance(e.error_details, dict):
                    if 'original_error' in e.error_details:
                        print(f"Original Error: {e.error_details['original_error']}")
                    if 'error_type' in e.error_details:
                        print(f"Error Type: {e.error_details['error_type']}")
                    if e.error_details:
                        print(f"Details: {e.error_details}")
            
            print("\n" + "-" * 70)
            print("Troubleshooting:")
            print("  • Verify database configuration settings")
            print("  • Check database server is running and accessible")
            print("  • Ensure database credentials are correct")
            print("  • Verify database connection string format")
            print("  • Check database file permissions (for SQLite)")
            print("-" * 70)
            raise
            
        except Exception as e:
            self._print_error_header("DATABASE ERROR")
            print(f"Error Type: {type(e).__name__}")
            print(f"Error Message: {str(e)}")
            print("\n" + "-" * 70)
            print("An unexpected error occurred during database initialization.")
            print("Please review the error details above and check database configuration.")
            print("-" * 70)
            raise

    def _print_error_header(self, error_type: str):
        """Print formatted error header."""
        print("\n" + "=" * 70)
        print(f"❌ {error_type}".center(70))
        print("=" * 70)

    def _initialize_seed_services(self):
        """Initialize seed services"""
        if not self._user_role_service:
            self._user_role_service = UserRolesService()
        if not self._workspace_plan_service:
            self._workspace_plan_service = WorkspacePlansService()
        if not self._agreement_service:
            self._agreement_service = AgreementService()

    def seed_initial_data(self):
        """Başlangıç verilerini ekle (roller, planlar ve sözleşmeler)"""
        if not self._db_manager or not self._db_manager.is_initialized:
            raise RuntimeError("Database Manager is not initialized. Call _setup_database() first.")
        
        print("[VERİ] Başlangıç verileri ekleniyor...")
        
        # Initialize services
        self._initialize_seed_services()
        
        # Kullanıcı rolleri
        role_stats = self._user_role_service.seed_role(roles_data=USER_ROLES_SEED)
        print(f"[VERİ] Kullanıcı rolleri: {role_stats['created']} eklendi, {role_stats['skipped']} atlandı")
        
        # Çalışma alanı planları
        plan_stats = self._workspace_plan_service.seed_plan(plans_data=WORKSPACE_PLANS_SEED)
        print(f"[VERİ] Çalışma planları: {plan_stats['created']} eklendi, {plan_stats['skipped']} atlandı")
        
        # Sözleşmeler (GDPR compliance)
        agreement_stats = self._agreement_service.seed_agreement(agreements_data=AGREEMENT_SEEDS)
        print(f"[VERİ] Sözleşmeler: {agreement_stats['created']} eklendi, {agreement_stats['updated']} güncellendi, {agreement_stats['skipped']} atlandı")


if __name__ == "__main__":
    """Main entry point for MiniFlow application."""
    try:
        print("=" * 70)
        print("MINIFLOW ENTERPRISE - STARTING".center(70))
        print("=" * 70)
        
        app = MiniFlow()
        
        # Initialize Database
        app._setup_database()
        
        # Seed initial data
        app.seed_initial_data()
        
        print("\n" + "=" * 70)
        print("MINIFLOW ENTERPRISE - READY".center(70))
        print("=" * 70)
        print(f"Environment: {app._app_env}")
        print(f"Database Type: {app._db_type}")
        print(f"Development Mode: {app.is_development}")
        print(f"Production Mode: {app.is_production}")
        print(f"Database Manager: {'Initialized' if app._db_manager and app._db_manager.is_initialized else 'Not Initialized'}")
        print("=" * 70 + "\n")
        
    except KeyboardInterrupt:
        print("\n\n[INFO] Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n[FATAL] Application failed to start: {type(e).__name__}: {str(e)}")
        sys.exit(1)