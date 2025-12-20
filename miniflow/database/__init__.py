"""
Database Module - Veritabanı Altyapısı

Bu modül, veritabanı işlemleri için tüm gerekli bileşenleri sağlar:

1. Engine: Bağlantı havuzu ve oturum yönetimi
   - DatabaseEngine: Temel veritabanı motoru
   - DatabaseManager: Singleton manager

2. Repository: 3 katmanlı repository yapısı
   - BaseRepository: Temel CRUD işlemleri
   - AdvancedRepository: Gelişmiş sorgulama + Eager Loading
   - BulkRepository: Toplu işlemler

3. Models: ORM model yapıları
   - Base: SQLAlchemy declarative base
   - Mixins: Timestamp, SoftDelete, Audit
   - Serialization: Model-to-dict/JSON dönüşüm

4. Config: Veritabanı konfigürasyonu
   - DatabaseConfig: Bağlantı ayarları
   - EngineConfig: Motor ayarları

5. Decorators: Oturum yönetimi
   - @with_session: Otomatik oturum
   - @with_transaction_session: Atomic transaction
   - @with_retry_session: Retry desteği

Örnek Kullanım:
    >>> from miniflow.database import (
    ...     DatabaseManager,
    ...     BulkRepository,
    ...     with_session,
    ...     model_to_dict
    ... )
    >>> 
    >>> # Repository tanımlama
    >>> class UserRepository(BulkRepository[User]):
    ...     def __init__(self):
    ...         super().__init__(User)
    >>> 
    >>> # Service layer'da kullanım
    >>> @with_session()
    >>> def get_user(session, user_id):
    ...     user = user_repo.get_with_relations(
    ...         session, user_id,
    ...         relations=["posts", "profile"]
    ...     )
    ...     return model_to_dict(user, include_relationships=True)
"""

# Engine
from miniflow.database.engine import (
    DatabaseEngine,
    DatabaseManager,
    get_database_manager,
    with_session,
    with_transaction_session,
    with_readonly_session,
    with_retry_session,
    inject_session,
)

# Repository
from miniflow.database.repository import (
    BaseRepository,
    AdvancedRepository,
    BulkRepository,
    handle_db_exceptions,
    EAGER_STRATEGIES,
)

# Models
from miniflow.database.models import (
    Base,
    TimestampMixin,
    SoftDeleteMixin,
    AuditMixin,
    model_to_dict,
    models_to_list,
    model_to_json,
)

# Config
from miniflow.database.config import (
    DatabaseConfig,
    DatabaseType,
    EngineConfig,
)

__all__ = [
    # Engine
    "DatabaseEngine",
    "DatabaseManager",
    "get_database_manager",
    
    # Decorators
    "with_session",
    "with_transaction_session",
    "with_readonly_session",
    "with_retry_session",
    "inject_session",
    
    # Repository
    "BaseRepository",
    "AdvancedRepository",
    "BulkRepository",
    "handle_db_exceptions",
    "EAGER_STRATEGIES",
    
    # Models - Base
    "Base",
    
    # Models - Mixins
    "TimestampMixin",
    "SoftDeleteMixin",
    "AuditMixin",
    
    # Models - Serialization
    "model_to_dict",
    "models_to_list",
    "model_to_json",
    
    # Config
    "DatabaseConfig",
    "DatabaseType",
    "EngineConfig",
]

