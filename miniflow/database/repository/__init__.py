"""
Repository Module - Veritabanı İşlemleri için Base Sınıflar

Bu modül, 3 katmanlı repository yapısı sağlar:

1. BaseRepository: Temel CRUD işlemleri
   - create, get_by_id, update, delete
   - soft_delete, restore
   - exists, get_by_ids
   - increment, decrement (database-level atomic)

2. AdvancedRepository: Gelişmiş sorgulama (BaseRepository'den türer)
   - get_all, count, search
   - get_first, get_last
   - paginate, paginate_cursor
   - get_or_create, upsert
   - Eager Loading (N+1 çözümü):
     * get_with_relations
     * get_all_with_relations
     * paginate_with_relations

3. BulkRepository: Toplu işlemler (AdvancedRepository'den türer)
   - bulk_create, bulk_update, bulk_update_where
   - bulk_delete, bulk_soft_delete
   - bulk_restore

Eager Loading Stratejileri:
    - "joined": JOIN ile tek sorgu (1-to-1, many-to-1 için ideal)
    - "select": Ayrı SELECT sorgusu (1-to-many için ideal, varsayılan)
    - "subquery": Subquery ile (büyük veri setleri için)

Kullanım:
    >>> from miniflow.database.repository import BaseRepository
    >>> from miniflow.models.user_models.users import User
    >>> 
    >>> class UserRepository(BaseRepository[User]):
    ...     def __init__(self):
    ...         super().__init__(User)
    >>> 
    >>> # Gelişmiş özellikler + Eager Loading için:
    >>> from miniflow.database.repository import AdvancedRepository
    >>> 
    >>> class UserRepository(AdvancedRepository[User]):
    ...     def __init__(self):
    ...         super().__init__(User)
    >>> 
    >>> # Eager loading ile kullanım:
    >>> user = user_repo.get_with_relations(
    ...     session, "USR-123",
    ...     relations=["posts", "profile"]
    ... )
    >>> 
    >>> # Toplu işlemler için:
    >>> from miniflow.database.repository import BulkRepository
    >>> 
    >>> class UserRepository(BulkRepository[User]):
    ...     def __init__(self):
    ...         super().__init__(User)
"""

from .base import BaseRepository, handle_db_exceptions
from .advanced import AdvancedRepository, EAGER_STRATEGIES
from .bulk import BulkRepository

__all__ = [
    # Repositories
    "BaseRepository",
    "AdvancedRepository",
    "BulkRepository",
    # Decorator
    "handle_db_exceptions",
    # Eager Loading Strategies
    "EAGER_STRATEGIES",
]

