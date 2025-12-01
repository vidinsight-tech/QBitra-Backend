"""
MiniFlow Enterprise - Main Entry Point

Terminal üzerinden sunucuyu yönetmek için iki mod:
- setup: İlk kurulum (dosya yapısı, veritabanı, seed, handler testleri)
- run: Uygulamayı başlat (FastAPI app, middleware, routes, server)
"""
# ============================================================================
# STANDARD LIBRARY IMPORTS
# ============================================================================
import os
import sys
import time
import traceback
import warnings
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

# ============================================================================
# THIRD-PARTY IMPORTS
# ============================================================================
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.pool import NullPool

# ============================================================================
# SEEDS
# ============================================================================
from seeds.agreement_seeds import AGREEMENT_SEEDS
from seeds.user_role_seeds import USER_ROLES_SEED
from seeds.workflow_plan_seeds import WORKSPACE_PLANS_SEED
from seeds.global_script_seeds import GLOBAL_SCRIPT_SEEDS

# ============================================================================
# CORE
# ============================================================================
from src.miniflow.core.exceptions import (
    InternalError,
    InvalidInputError,
    ResourceNotFoundError,
)

# ============================================================================
# DATABASE
# ============================================================================
from src.miniflow.database import (
    DatabaseManager,
    get_mysql_config,
    get_postgresql_config,
    get_sqlite_config,
)

# ============================================================================
# SERVICES
# ============================================================================
from src.miniflow.services.info_services.agreement_service import AgreementService
from src.miniflow.services.info_services.user_roles_service import UserRolesService
from src.miniflow.services.info_services.workspace_plans_service import (
    WorkspacePlansService,
)
from src.miniflow.services.script_services.global_script_service import GlobalScriptService

# ============================================================================
# UTILS
# ============================================================================
from src.miniflow.utils import ConfigurationHandler, EnvironmentHandler, RedisClient
from src.miniflow.utils.helpers.file_helper import create_resources_folder

# ============================================================================
# EARLY EXIT FOR HELP
# ============================================================================
if len(sys.argv) > 1 and sys.argv[1].lower() in ("help", "--help", "-h"):
    print("\n" + "=" * 70)
    print("MINIFLOW ENTERPRISE - Available Commands".center(70))
    print("=" * 70)
    print("\n  setup      Initial setup (database, seed data, tests)")
    print("  run        Start application (default)")
    print("  help       Show this help message")
    print("\nExamples:")
    print("  python -m src.miniflow setup")
    print("  python -m src.miniflow run")
    print("  python -m src.miniflow        # defaults to 'run'\n")
    sys.exit(0)


class MiniFlow:
    """MiniFlow Enterprise uygulama yöneticisi."""

    def __init__(self):
        """Temel initialization"""
        self._app_env: Optional[str] = None
        self._db_type: Optional[str] = None
        self._db_manager: Optional[DatabaseManager] = None
        self.is_running = False

        # Lazy initialization için seed services
        self._user_role_service: Optional[UserRolesService] = None
        self._workspace_plan_service: Optional[WorkspacePlansService] = None
        self._agreement_service: Optional[AgreementService] = None
        self._global_script_service: Optional[GlobalScriptService] = None

        self._initialize()

    # ========================================================================
    # INITIALIZATION
    # ========================================================================

    def _initialize(self):
        """Uygulama başlangıç ayarları"""
        self._print_header("MINIFLOW STARTUP INITIALIZATION")

        try:
            self._load_configurations()
            self._set_environment_vars()
            self._print_success("STARTUP INITIALIZATION COMPLETED")

        except (ResourceNotFoundError, InternalError) as e:
            self._handle_initialization_error(e)
        except Exception as e:
            self._handle_unexpected_error(e, "startup initialization")

    def _load_configurations(self):
        """Tüm konfigürasyonları yükle"""
        steps = [
            ("Loading environment variables", EnvironmentHandler.load_env),
            ("Loading configuration files", ConfigurationHandler.load_config),
            ("Initializing Redis connection", RedisClient.initialize),
            ("Creating resources folder", create_resources_folder),
        ]

        for i, (description, action) in enumerate(steps, 1):
            print(f"[{i}/{len(steps)}] {description}...", end=" ", flush=True)
            action()
            print("[OK]")

    def _set_environment_vars(self):
        """Ortam değişkenlerini ayarla ve doğrula"""
        self._app_env = EnvironmentHandler.get("APP_ENV", "").lower()
        self._db_type = EnvironmentHandler.get("DB_TYPE", "").lower()

        if not self._app_env:
            raise InternalError("miniflow", "APP_ENV environment variable is not set")
        if not self._db_type:
            raise InternalError("miniflow", "DB_TYPE environment variable is not set")

    # ========================================================================
    # SETUP MODE
    # ========================================================================

    def setup(self):
        """İlk kurulum ve sistem hazırlama"""
        self._print_header("MINIFLOW SETUP MODE")

        try:
            self._check_file_structure()
            self._setup_database()
            self._seed_initial_data()
            self._test_handlers()

            self._print_success("SETUP COMPLETED")
            print("Uygulamayı başlatmak için: python -m src.miniflow run\n")

        except Exception as e:
            self._print_error("SETUP ERROR", f"{type(e).__name__}: {str(e)}")
            print("\nSetup işlemi başarısız oldu. Lütfen yukarıdaki hataları kontrol edin.\n")
            raise
        finally:
            self._cleanup_database()

    def _check_file_structure(self):
        """Dosya yapısı kontrolü"""
        print("[1/4] Checking file structure...", end=" ", flush=True)

        create_resources_folder()

        required_paths = [Path("configurations"), Path("seeds")]
        missing = [p for p in required_paths if not p.exists()]

        if missing:
            raise ResourceNotFoundError(
                "required_directories",
                message=f"Missing: {', '.join(str(p) for p in missing)}"
            )

        if not Path(".env").exists():
            print("\n      [WARNING] .env file not found", end="")

        print(" [OK]")

    def _setup_database(self):
        """Veritabanı kurulumu"""
        print("[2/4] Setting up database...", end=" ", flush=True)

        db_config = self._get_db_config()
        self._db_manager = DatabaseManager()
        self._db_manager.initialize(db_config, auto_start=True, create_tables=True)

        if not self._test_db_connection():
            raise InternalError("database_manager", "Database connection test failed")

        print("[OK]")

    def _seed_initial_data(self):
        """Başlangıç verilerini ekle"""
        print("[3/4] Seeding initial data...", end=" ", flush=True)

        if not self._db_manager or not self._db_manager.is_initialized:
            raise RuntimeError("Database Manager not initialized")

        self._initialize_seed_services()

        role_stats = self._user_role_service.seed_role(roles_data=USER_ROLES_SEED)
        plan_stats = self._workspace_plan_service.seed_plan(plans_data=WORKSPACE_PLANS_SEED)
        agreement_stats = self._agreement_service.seed_agreement(agreements_data=AGREEMENT_SEEDS)
        script_stats = self._global_script_service.seed_script(scripts_data=GLOBAL_SCRIPT_SEEDS)

        print("[OK]")
        print(f"      • Roles: {role_stats['created']} created, {role_stats['skipped']} skipped")
        print(f"      • Plans: {plan_stats['created']} created, {plan_stats['skipped']} skipped")
        print(f"      • Agreements: {agreement_stats['created']} created, {agreement_stats['skipped']} skipped")
        print(f"      • Global Scripts: {script_stats['created']} created, {script_stats['skipped']} skipped")

    def _test_handlers(self):
        """Handler testleri"""
        print("[4/4] Testing handlers...", end=" ", flush=True)

        # Redis test
        try:
            RedisClient._client.ping()
            print("[OK] Redis", end=" ")
        except Exception as e:
            raise InternalError("redis_client", f"Redis test failed: {str(e)}")

        # Mail test (opsiyonel)
        try:
            from src.miniflow.utils.handlers.mailtrap_handler import MailTrapClient
            MailTrapClient.initialize()
            print("• Mail [OK]")
        except:
            print("• Mail [OPTIONAL]")

    # ========================================================================
    # RUN MODE
    # ========================================================================

    def run(self):
        """Uygulamayı başlat"""
        self._print_header("MINIFLOW RUN MODE")

        if not self._is_database_ready():
            self._print_error("DATABASE NOT READY",
                            "Please run setup first: python -m src.miniflow setup")
            sys.exit(1)

        app = self._create_fastapi_app()
        self._start_server(app)

    def _create_fastapi_app(self):
        """FastAPI uygulaması oluştur"""
        from fastapi import FastAPI

        app = FastAPI(
            title=self._config.get("Server", "title", "MiniFlow API"),
            description=self._config.get("Server", "description", "MiniFlow Application"),
            version=self._config.get("Server", "version", "1.0.0"),
            docs_url="/docs" if not self.is_production else None,
            redoc_url="/redoc" if not self.is_production else None,
            openapi_url="/openapi.json" if not self.is_production else None,
            lifespan=self._app_lifespan,
        )

        self._configure_middleware(app)
        self._configure_exception_handlers(app)
        self._configure_routes(app)

        return app

    @asynccontextmanager
    async def _app_lifespan(self, app):
        """App lifecycle yönetimi"""
        worker_pid = os.getpid()
        state = None

        try:
            state = self._worker_startup(worker_pid)
            yield
        except Exception as e:
            print(f"[WORKER-{worker_pid}] [ERROR] Startup failed: {e}")
            if state:
                self._worker_shutdown(worker_pid, state, force=True)
            raise
        finally:
            if state:
                self._worker_shutdown(worker_pid, state)

    def _worker_startup(self, pid: int) -> dict:
        """Worker servisleri başlat"""
        state = {}
        services = [
            ("Database", self._start_database),
            ("Engine", self._start_engine),
            ("Output Handler", self._start_output_handler),
            ("Input Handler", self._start_input_handler),
        ]

        try:
            for i, (name, starter) in enumerate(services, 1):
                print(f"[WORKER-{pid}] [{i}/{len(services)}] Starting {name}...")
                component = starter(state)
                if component:
                    state[name.lower().replace(" ", "_")] = component
                print(f"[WORKER-{pid}] [{i}/{len(services)}] [OK] {name} started")

            # Scheduler (opsiyonel)
            self._start_scheduler(pid, state)

            print(f"[WORKER-{pid}] [SUCCESS] All services started\n")
            return state

        except Exception as e:
            print(f"[WORKER-{pid}] [ERROR] Startup failed: {e}")
            self._worker_shutdown(pid, state, force=True)
            raise

    def _worker_shutdown(self, pid: int, state: dict, force: bool = False):
        """Worker servisleri kapat"""
        if not state:
            return

        prefix = "[FORCE] " if force else ""
        print(f"\n[WORKER-{pid}] {prefix}Stopping services...")

        # Ters sırada kapat
        shutdown_order = ['input_handler', 'output_handler', 'engine', 'database', 'scheduler']

        for i, service_key in enumerate(shutdown_order, 1):
            if service := state.get(service_key):
                service_name = service_key.replace("_", " ").title()
                print(f"[WORKER-{pid}] {prefix}[{i}/{len(shutdown_order)}] Stopping {service_name}...")

                try:
                    self._stop_service(service, service_key)
                    print(f"[WORKER-{pid}] {prefix}[{i}/{len(shutdown_order)}] [OK] {service_name} stopped")
                except Exception as e:
                    print(f"[WORKER-{pid}] {prefix}[{i}/{len(shutdown_order)}] [WARNING] {service_name}: {e}")

        print(f"[WORKER-{pid}] {prefix}[SUCCESS] Shutdown complete\n")

    def _start_server(self, app):
        """Uvicorn sunucu başlat"""
        import uvicorn

        host = self._config.get("Server", "host", "0.0.0.0")
        port = self._config.get_int("Server", "port", 8000)
        reload = self._config.get_bool("Server", "reload", False) and self.is_development
        workers = 1 if reload else self._config.get_int("Server", "workers", 1)

        self._print_server_info(host, port, reload, workers)
        self.is_running = True

        if reload:
            uvicorn.run("src.miniflow.app:app", host=host, port=port, reload=True)
        else:
            uvicorn.run(app, host=host, port=port, workers=workers)

    # ========================================================================
    # SERVICE STARTERS/STOPPERS
    # ========================================================================

    def _start_database(self, state: dict):
        """Database başlat"""
        db_manager = DatabaseManager()
        if not db_manager.is_initialized:
            db_manager.initialize(self._get_db_config(), auto_start=True, create_tables=False)
        state['db_manager'] = db_manager
        return db_manager

    def _start_engine(self, state: dict):
        """Engine başlat"""
        from src.miniflow.engine.manager.engine_manager import EngineManager
        engine = EngineManager()
        if not engine.started:
            engine.start()
        state['engine_manager'] = engine
        return engine

    def _start_output_handler(self, state: dict):
        """Output Handler başlat"""
        from src.miniflow.handlers.execution_output_handler import ExecutionOutputHandler
        ExecutionOutputHandler.start(state['engine_manager'])
        return ExecutionOutputHandler

    def _start_input_handler(self, state: dict):
        """Input Handler başlat"""
        from src.miniflow.handlers.execution_input_handler import ExecutionInputHandler
        ExecutionInputHandler.start(state['engine_manager'])
        return ExecutionInputHandler

    def _start_scheduler(self, pid: int, state: dict):
        """
        Scheduler başlat (opsiyonel)
        
        Note: Scheduler functionality is handled by SchedulerForInputHandler and
        SchedulerForOutputHandler which are used internally by the handlers.
        This method is kept for compatibility but does nothing.
        """
        # Scheduler is handled internally by ExecutionInputHandler and ExecutionOutputHandler
        # No separate scheduler service to start
        pass

    def _stop_service(self, service, service_key: str):
        """Servisi durdur"""
        if service_key == 'database':
            time.sleep(0.5)  # Transaction'ların bitmesini bekle
            if service.is_started:
                if active := service.engine.get_active_session_count():
                    service.engine.close_all_sessions()
                service.engine.stop()
        elif hasattr(service, 'shutdown'):
            service.shutdown()
        elif hasattr(service, 'stop'):
            service.stop()

    # ========================================================================
    # MIDDLEWARE & ROUTES
    # ========================================================================

    def _configure_middleware(self, app):
        """Middleware yapılandırması"""
        from fastapi.middleware.cors import CORSMiddleware
        from src.miniflow.server.middleware.request_id_handler import RequestIdMiddleware
        from src.miniflow.server.middleware.rate_limit_handler import RateLimitMiddleware

        # CORS
        origins = self._config.get_list("Server", "allowed_origins", "*")
        app.add_middleware(
            CORSMiddleware,
            allow_origins=origins if isinstance(origins, list) else [origins],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Request ID & Rate Limit
        app.add_middleware(RequestIdMiddleware)
        app.add_middleware(RateLimitMiddleware)

    def _configure_exception_handlers(self, app):
        """Exception handler yapılandırması"""
        warnings.filterwarnings("ignore", category=DeprecationWarning,
                              message=".*HTTP_422_UNPROCESSABLE_ENTITY.*")

        from fastapi.exceptions import RequestValidationError
        from starlette.exceptions import HTTPException as StarletteHTTPException
        from src.miniflow.core.exceptions import AppException
        from src.miniflow.server.middleware.exception_handler import (
            app_exception_handler,
            validation_exception_handler,
            http_exception_handler,
            generic_exception_handler,
        )

        app.add_exception_handler(AppException, app_exception_handler)
        app.add_exception_handler(RequestValidationError, validation_exception_handler)
        app.add_exception_handler(StarletteHTTPException, http_exception_handler)
        app.add_exception_handler(Exception, generic_exception_handler)

    def _configure_routes(self, app):
        """Route yapılandırması"""
        # Health endpoints
        @app.get("/", tags=["General"])
        async def root():
            return {
                "app": "MiniFlow",
                "status": "running",
                "environment": self._app_env,
                "docs": "/docs" if not self.is_production else None
            }

        @app.get("/health", tags=["Health"])
        async def health():
            return {
                "status": "healthy",
                "environment": self._app_env,
                "database_type": self._db_type
            }

        # API routers
        from src.miniflow.server.routes import (
            auth_routes, user_routes, agreement_routes, workspace_plans_routes,
            workspace_routes, workspace_member_routes, workspace_invitation_routes,
            api_key_routes, variable_routes, database_routes, file_routes,
            credential_routes, global_script_routes, custom_script_routes,
            workflow_routes, trigger_routes, node_routes, edge_routes,
            execution_routes
        )

        for route in [
            auth_routes, user_routes, agreement_routes, workspace_plans_routes,
            workspace_routes, workspace_member_routes, workspace_invitation_routes,
            api_key_routes, variable_routes, database_routes, file_routes,
            credential_routes, global_script_routes, custom_script_routes,
            workflow_routes, trigger_routes, node_routes, edge_routes,
            execution_routes
        ]:
            app.include_router(route.router)

    # ========================================================================
    # HELPERS
    # ========================================================================

    def _get_db_config(self):
        """Veritabanı konfigürasyonu"""
        configs = {
            "sqlite": lambda: get_sqlite_config(
                self._config.get("Database", "db_path", "./miniflow.db")
            ),
            "postgresql": lambda: get_postgresql_config(
                database_name=self._config.get("Database", "db_name", "miniflow"),
                host=self._config.get("Database", "db_host", "localhost"),
                port=self._config.get_int("Database", "db_port", 5432),
                username=self._config.get("Database", "db_user", "postgres"),
                password=self._config.get("Database", "db_password", ""),
            ),
            "mysql": lambda: get_mysql_config(
                database_name=self._config.get("Database", "db_name", "miniflow"),
                host=self._config.get("Database", "db_host", "localhost"),
                port=self._config.get_int("Database", "db_port", 3306),
                username=self._config.get("Database", "db_user", "root"),
                password=self._config.get("Database", "db_password", ""),
            ),
        }

        if self._db_type not in configs:
            raise InvalidInputError(field_name="DB_TYPE")

        return configs[self._db_type]()

    def _test_db_connection(self) -> bool:
        """Veritabanı bağlantı testi"""
        if not self._db_manager or not self._db_manager.is_initialized:
            return False

        try:
            engine = self._db_manager.engine._engine
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                return len(inspect(engine).get_table_names()) > 0
        except:
            return False

    def _is_database_ready(self) -> bool:
        """Veritabanı hazır mı kontrolü"""
        try:
            db_url = self._get_db_config().get_connection_string()
            engine = create_engine(db_url, echo=False, poolclass=NullPool)

            try:
                with engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                    return len(inspect(engine).get_table_names()) > 0
            finally:
                engine.dispose()
        except:
            return False

    def _initialize_seed_services(self):
        """Seed service'leri başlat"""
        self._user_role_service = self._user_role_service or UserRolesService()
        self._workspace_plan_service = self._workspace_plan_service or WorkspacePlansService()
        self._agreement_service = self._agreement_service or AgreementService()
        self._global_script_service = self._global_script_service or GlobalScriptService()

    def _cleanup_database(self):
        """Veritabanı temizleme"""
        if self._db_manager and self._db_manager.is_started:
            self._db_manager.engine.stop()

    # ========================================================================
    # PROPERTIES
    # ========================================================================

    @property
    def _config(self):
        return ConfigurationHandler

    @property
    def is_development(self) -> bool:
        return 'dev' in self._app_env

    @property
    def is_production(self) -> bool:
        return 'prod' in self._app_env

    # ========================================================================
    # OUTPUT HELPERS
    # ========================================================================

    def _print_header(self, title: str):
        """Başlık yazdır"""
        print("\n" + "=" * 70)
        print(title.center(70))
        print("=" * 70 + "\n")

    def _print_success(self, title: str):
        """Başarı mesajı"""
        print("\n" + "=" * 70)
        print(f"[SUCCESS] {title}".center(70))
        print("=" * 70 + "\n")

    def _print_error(self, title: str, message: str):
        """Hata mesajı"""
        print("\n" + "=" * 70)
        print(f"[ERROR] {title}".center(70))
        print("=" * 70)
        print(f"\n{message}\n")
        print("-" * 70 + "\n")

    def _print_server_info(self, host: str, port: int, reload: bool, workers: int):
        """Sunucu bilgileri"""
        print("-" * 70)
        print("WEB SERVER STARTING".center(70))
        print("-" * 70)
        print(f"Environment       : {self._app_env.upper()}")
        print(f"Database Type     : {self._db_type.upper()}")
        print(f"Address           : http://{host}:{port}")
        if not self.is_production:
            print(f"Documentation     : http://{host}:{port}/docs")
        print(f"Reload            : {'[ACTIVE]' if reload else '[DISABLED]'}")
        print(f"Workers           : {workers}")
        print("-" * 70 + "\n")

    def _handle_initialization_error(self, e):
        """Initialization hata yönetimi"""
        self._print_error(
            "INITIALIZATION ERROR" if isinstance(e, InternalError) else "RESOURCE NOT FOUND",
            str(e.error_message if hasattr(e, 'error_message') else e)
        )

        troubleshooting = {
            "environment_handler": [
                "Verify .env file exists in project root",
                "Check TEST_KEY='ThisKeyIsForConfigTest'",
            ],
            "configuration_handler": [
                "Verify config files in 'configurations/' directory",
                "Check INI format with [Test] section",
            ],
            "redis_client": [
                "Verify Redis server is running",
                "Test connection: redis-cli ping",
            ],
        }

        component = getattr(e, 'component_name', None)
        if component and component in troubleshooting:
            print("Troubleshooting:")
            for tip in troubleshooting[component]:
                print(f"  • {tip}")
            print("-" * 70 + "\n")

        sys.exit(1)

    def _handle_unexpected_error(self, e, context: str = ""):
        """Beklenmeyen hata yönetimi"""
        self._print_error(
            "UNEXPECTED ERROR",
            f"{type(e).__name__}: {str(e)}\n\nContext: {context}" if context else str(e)
        )
        sys.exit(1)


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    """Main entry point for MiniFlow application."""
    miniflow = None

    try:
        command = sys.argv[1].lower() if len(sys.argv) > 1 else "run"
        miniflow = MiniFlow()

        if command == "setup":
            miniflow.setup()
        elif command == "run":
            miniflow.run()
        else:
            print(f"\nUnknown command: {command}")
            print("Use 'python -m src.miniflow help' for available commands\n")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n[INFO] Application interrupted by user\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n[FATAL] {type(e).__name__}: {str(e)}")
        if miniflow and miniflow.is_development:
            traceback.print_exc()
        sys.exit(1)
