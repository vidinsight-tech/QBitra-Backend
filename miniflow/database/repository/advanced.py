"""
Advanced Repository - Gelişmiş Filtreleme ve Sorgulama

Bu modül, gelişmiş filtreleme, pagination, search ve özel işlemler sağlar.
BaseRepository'den türetilir.

Kullanım:
    >>> from miniflow.database.repository import AdvancedRepository
    >>> from miniflow.models.user_models.users import User
    >>> 
    >>> class UserRepository(AdvancedRepository[User]):
    ...     def __init__(self):
    ...         super().__init__(User)
"""

import logging
from typing import Any, Dict, Generic, List, Optional, Tuple, TypeVar, Union

from sqlalchemy import select, func, or_, text, insert, update as sql_update
from sqlalchemy.orm import DeclarativeBase, Session, joinedload, selectinload, subqueryload
from sqlalchemy.sql import Select
from sqlalchemy.exc import IntegrityError

from miniflow.core.exceptions import ValidationError
from .base import BaseRepository, handle_db_exceptions, ModelType

logger = logging.getLogger(__name__)


# Eager loading stratejileri
EAGER_STRATEGIES = {
    "joined": joinedload,      # JOIN ile tek sorgu (1-to-1, many-to-1 için ideal)
    "select": selectinload,    # Ayrı SELECT sorgusu (1-to-many için ideal)
    "subquery": subqueryload,  # Subquery ile (büyük veri setleri için)
}


def _detect_db_type_from_session(session: Session) -> str:
    """
    Session'dan veritabanı tipini tespit eder.
    
    Args:
        session: SQLAlchemy session
        
    Returns:
        str: 'postgresql', 'mysql', 'sqlite', or 'unknown'
    """
    try:
        # Get database dialect from session bind
        if hasattr(session, 'bind') and session.bind is not None:
            dialect = session.bind.dialect
            dialect_name = dialect.name.lower()
            
            if dialect_name in ('postgresql', 'postgres'):
                return 'postgresql'
            elif dialect_name in ('mysql', 'mariadb'):
                return 'mysql'
            elif dialect_name == 'sqlite':
                return 'sqlite'
        
        # Fallback: Try to detect from connection string
        if hasattr(session, 'bind') and hasattr(session.bind, 'url'):
            url_str = str(session.bind.url).lower()
            if 'postgresql' in url_str or 'postgres' in url_str:
                return 'postgresql'
            elif 'mysql' in url_str or 'mariadb' in url_str:
                return 'mysql'
            elif 'sqlite' in url_str:
                return 'sqlite'
    except Exception:
        pass
    
    return 'unknown'


class AdvancedRepository(BaseRepository[ModelType], Generic[ModelType]):
    """
    Gelişmiş filtreleme, pagination ve özel işlemler için repository.
    
    BaseRepository'den türetilir ve ek olarak şu özellikleri sağlar:
        - Gelişmiş filtreleme (operatörler: >, <, LIKE, IN vb.)
        - Pagination (sayfalama)
        - Search (çoklu alanda arama)
        - Eager Loading (N+1 problemi çözümü)
        - get_or_create pattern
        - upsert operasyonu
        - Count ve sıralama
    
    Eager Loading Stratejileri:
        - "joined": JOIN ile tek sorgu (1-to-1, many-to-1 için ideal)
        - "select": Ayrı SELECT sorgusu (1-to-many için ideal, büyük listelerde)
        - "subquery": Subquery ile (büyük veri setleri için)
    
    Kullanım:
        >>> class UserRepository(AdvancedRepository[User]):
        ...     def __init__(self):
        ...         super().__init__(User)
        >>> 
        >>> user_repo = UserRepository()
        >>> users = user_repo.get_all(session, is_active=True, order_by="name")
        >>> 
        >>> # Eager loading ile (N+1 problemi yok)
        >>> user = user_repo.get_with_relations(
        ...     session, "USR-123",
        ...     relations=["posts", "profile"]
        ... )
    """

    # ============================================================================
    # FILTER HELPERS
    # ============================================================================

    def _apply_filters(self, query: Select, **filters: Any) -> Select:
        """
        Basit eşitlik filtrelerini uygular. O(n) - n = filter sayısı.
        
        Args:
            query: SQLAlchemy select query
            **filters: field=value formatında filtreler
        
        Returns:
            Filtrelenmiş query
        """
        for key, value in filters.items():
            if hasattr(self.model, key):
                query = query.where(getattr(self.model, key) == value)
        return query

    def _apply_ordering(
        self, 
        query: Select, 
        order_by: Optional[str] = None, 
        order_desc: bool = False
    ) -> Select:
        """
        Sıralama uygular. O(1).
        
        Args:
            query: SQLAlchemy select query
            order_by: Sıralama alanı
            order_desc: Azalan sıralama
        
        Returns:
            Sıralanmış query
        """
        if order_by and hasattr(self.model, order_by):
            col = getattr(self.model, order_by)
            query = query.order_by(col.desc() if order_desc else col.asc())
        return query

    def _apply_search(
        self, 
        query: Select, 
        search: Optional[str] = None, 
        search_fields: Optional[List[str]] = None
    ) -> Select:
        """
        Arama filtresi uygular (ILIKE). O(m) - m = search field sayısı.
        
        Args:
            query: SQLAlchemy select query
            search: Arama terimi
            search_fields: Aranacak alanlar
        
        Returns:
            Filtrelenmiş query
        """
        if not search or not search_fields:
            return query
        
        # SQL LIKE özel karakterlerini escape et (% ve _)
        escaped_search = search.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')
        
        conditions = []
        for field_name in search_fields:
            if hasattr(self.model, field_name):
                field = getattr(self.model, field_name)
                conditions.append(field.ilike(f"%{escaped_search}%", escape='\\'))
        
        if conditions:
            query = query.where(or_(*conditions))
        
        return query

    def _apply_eager_loading(
        self,
        query: Select,
        relations: Optional[List[Union[str, Dict[str, Any]]]] = None,
        strategy: str = "select"
    ) -> Select:
        """
        Eager loading uygular (N+1 problemi çözümü). O(1).
        
        Args:
            query: SQLAlchemy select query
            relations: Yüklenecek ilişkiler
                - str: İlişki adı (varsayılan strateji kullanılır)
                - Dict: {"name": "posts", "strategy": "joined"} formatında
            strategy: Varsayılan strateji ("joined", "select", "subquery")
        
        Returns:
            Eager loading eklenmiş query
        
        Stratejiler:
            - "joined": JOIN ile tek sorgu
                * 1-to-1 ve many-to-1 için ideal
                * Tek sorgu, ama büyük listelerde Cartesian product riski
            - "select": Ayrı SELECT sorgusu (varsayılan)
                * 1-to-many için ideal
                * 2 sorgu ama daha az veri transferi
            - "subquery": Subquery ile
                * Büyük veri setleri için
                * Daha optimize execution plan
        
        Example:
            >>> # Basit kullanım
            >>> query = self._apply_eager_loading(query, ["posts", "profile"])
            >>> 
            >>> # Strateji belirtme
            >>> query = self._apply_eager_loading(query, [
            ...     {"name": "profile", "strategy": "joined"},
            ...     {"name": "posts", "strategy": "select"}
            ... ])
        """
        if not relations:
            return query
        
        for relation in relations:
            if isinstance(relation, str):
                # Basit string: varsayılan strateji
                relation_name = relation
                rel_strategy = strategy
            elif isinstance(relation, dict):
                # Dict formatı: {"name": "posts", "strategy": "joined"}
                relation_name = relation.get("name", "")
                rel_strategy = relation.get("strategy", strategy)
            else:
                continue
            
            # İlişki model'de var mı kontrol et
            if not hasattr(self.model, relation_name):
                continue
            
            # Strateji fonksiyonunu al
            loader_func = EAGER_STRATEGIES.get(rel_strategy, selectinload)
            
            # Eager loading uygula
            query = query.options(loader_func(getattr(self.model, relation_name)))
        
        return query

    # ============================================================================
    # EAGER LOADING OPERATIONS
    # ============================================================================

    @handle_db_exceptions
    def get_with_relations(
        self,
        session: Session,
        record_id: str,
        *,
        relations: List[Union[str, Dict[str, Any]]],
        strategy: str = "select",
        include_deleted: bool = False,
        raise_not_found: bool = True
    ) -> Optional[ModelType]:
        """
        İlişkili verilerle birlikte tek kayıt getirir. N+1 problemini önler.
        
        Bu metod, ilişkili verileri tek sorguda (veya minimum sorgu ile) yükler.
        Lazy loading yerine eager loading kullanır, böylece N+1 problemi oluşmaz.
        
        Performans:
            - "joined": 1 sorgu (JOIN)
            - "select": 2 sorgu (ana + ilişki)
            - "subquery": 2 sorgu (ana + subquery)
        
        Args:
            session: Database session
            record_id: Kayıt ID'si
            relations: Yüklenecek ilişkiler
                - str: İlişki adı ["posts", "profile"]
                - Dict: [{"name": "posts", "strategy": "joined"}]
            strategy: Varsayılan eager loading stratejisi
                - "joined": JOIN ile tek sorgu (1-to-1, many-to-1 için)
                - "select": Ayrı SELECT (1-to-many için, varsayılan)
                - "subquery": Subquery ile (büyük veri setleri)
            include_deleted: Silinmiş kayıtları dahil et
            raise_not_found: Bulunamazsa hata fırlat
        
        Returns:
            Model instance (ilişkili verilerle birlikte) veya None
        
        Example:
            >>> # Kullanıcıyı posts ve profile ile getir
            >>> user = user_repo.get_with_relations(
            ...     session,
            ...     "USR-123",
            ...     relations=["posts", "profile"]
            ... )
            >>> print(len(user.posts))  # Lazy load yok, zaten yüklü
            >>> print(user.profile.bio)  # Lazy load yok
            
            >>> # Strateji belirtme (performans optimizasyonu)
            >>> user = user_repo.get_with_relations(
            ...     session,
            ...     "USR-123",
            ...     relations=[
            ...         {"name": "profile", "strategy": "joined"},  # 1-to-1
            ...         {"name": "posts", "strategy": "select"}     # 1-to-many
            ...     ]
            ... )
        
        Strateji Seçimi:
            ┌─────────────────┬──────────────┬──────────────────────────────┐
            │ İlişki Tipi     │ Önerilen     │ Neden                        │
            ├─────────────────┼──────────────┼──────────────────────────────┤
            │ 1-to-1          │ "joined"     │ Tek sorgu, az veri           │
            │ many-to-1       │ "joined"     │ Tek sorgu, az veri           │
            │ 1-to-many       │ "select"     │ Cartesian product önlenir    │
            │ many-to-many    │ "select"     │ Cartesian product önlenir    │
            │ Büyük veri      │ "subquery"   │ Optimize execution plan      │
            └─────────────────┴──────────────┴──────────────────────────────┘
        """
        query = select(self.model).where(self.model.id == record_id)
        query = self._apply_soft_delete_filter(query, include_deleted)
        query = self._apply_eager_loading(query, relations, strategy)
        
        result = session.execute(query).scalar_one_or_none()
        
        if result is None and raise_not_found:
            self._raise_not_found(record_id)
        
        return result

    @handle_db_exceptions
    def get_all_with_relations(
        self,
        session: Session,
        *,
        relations: List[Union[str, Dict[str, Any]]],
        strategy: str = "select",
        skip: int = 0,
        limit: Optional[int] = None,
        order_by: Optional[str] = None,
        order_desc: bool = False,
        include_deleted: bool = False,
        **filters: Any
    ) -> List[ModelType]:
        """
        İlişkili verilerle birlikte tüm kayıtları getirir. N+1 problemini önler.
        
        Bu metod, filtreleme ve sıralama ile birlikte ilişkili verileri
        eager loading ile yükler.
        
        ⚠️ DİKKAT: "joined" stratejisi ile 1-to-many ilişkilerde Cartesian
        product oluşabilir. Bu durumda "select" veya "subquery" kullanın.
        
        Performans:
            - N+1 problemi yok
            - "select" stratejisi genelde en güvenli
            - Büyük listeler için "subquery" daha performanslı
        
        Args:
            session: Database session
            relations: Yüklenecek ilişkiler (bkz: get_with_relations)
            strategy: Varsayılan strateji ("joined", "select", "subquery")
            skip: Atlanacak kayıt sayısı
            limit: Maksimum kayıt sayısı
            order_by: Sıralama alanı
            order_desc: Azalan sıralama
            include_deleted: Silinmiş kayıtları dahil et
            **filters: Filtreler
        
        Returns:
            Model listesi (ilişkili verilerle birlikte)
        
        Example:
            >>> # Tüm aktif kullanıcıları posts ile getir
            >>> users = user_repo.get_all_with_relations(
            ...     session,
            ...     relations=["posts"],
            ...     is_active=True,
            ...     order_by="created_at",
            ...     order_desc=True,
            ...     limit=10
            ... )
            >>> for user in users:
            ...     print(f"{user.name}: {len(user.posts)} posts")
            
            >>> # Composite strateji
            >>> orders = order_repo.get_all_with_relations(
            ...     session,
            ...     relations=[
            ...         {"name": "user", "strategy": "joined"},      # many-to-1
            ...         {"name": "items", "strategy": "select"},     # 1-to-many
            ...         {"name": "shipping", "strategy": "joined"}   # 1-to-1
            ...     ],
            ...     status="pending"
            ... )
        """
        query = select(self.model)
        query = self._apply_soft_delete_filter(query, include_deleted)
        query = self._apply_filters(query, **filters)
        query = self._apply_ordering(query, order_by, order_desc)
        query = self._apply_eager_loading(query, relations, strategy)
        
        if skip > 0:
            query = query.offset(skip)
        if limit is not None:
            query = query.limit(limit)
        
        result = session.execute(query).scalars().unique().all()
        return list(result)

    @handle_db_exceptions
    def paginate_with_relations(
        self,
        session: Session,
        *,
        relations: List[Union[str, Dict[str, Any]]],
        strategy: str = "select",
        page: int = 1,
        page_size: int = 20,
        include_total: bool = False,
        order_by: Optional[str] = None,
        order_desc: bool = False,
        include_deleted: bool = False,
        **filters: Any
    ) -> Dict[str, Any]:
        """
        İlişkili verilerle birlikte sayfalama yapar. N+1 problemini önler.
        
        paginate() metodunun eager loading destekli versiyonu.
        
        ⚠️ ÖNEMLİ: 1-to-many ilişkilerde "joined" stratejisi kullanmayın!
        Cartesian product nedeniyle sayfalama yanlış sonuç verebilir.
        Bu durumda "select" veya "subquery" kullanın.
        
        Args:
            session: Database session
            relations: Yüklenecek ilişkiler
            strategy: Varsayılan strateji (varsayılan: "select")
            page: Sayfa numarası (1'den başlar)
            page_size: Sayfa başına kayıt
            include_total: Toplam sayıyı hesapla
            order_by: Sıralama alanı
            order_desc: Azalan sıralama
            include_deleted: Silinmiş kayıtları dahil et
            **filters: Filtreler
        
        Returns:
            Pagination sonucu (paginate() ile aynı format)
        
        Example:
            >>> # Sayfalı kullanıcı listesi (posts ile)
            >>> result = user_repo.paginate_with_relations(
            ...     session,
            ...     relations=["posts", "profile"],
            ...     page=1,
            ...     page_size=10,
            ...     is_active=True
            ... )
            >>> for user in result["items"]:
            ...     print(f"{user.name}: {len(user.posts)} posts")
        """
        # Input validation
        if page < 1:
            page = 1
        if page_size < 1:
            page_size = 20
        
        skip = (page - 1) * page_size
        
        if include_total:
            total = self.count(session, include_deleted=include_deleted, **filters)
            total_pages = (total + page_size - 1) // page_size if total > 0 else 0
            
            items = self.get_all_with_relations(
                session,
                relations=relations,
                strategy=strategy,
                skip=skip,
                limit=page_size,
                order_by=order_by,
                order_desc=order_desc,
                include_deleted=include_deleted,
                **filters
            )
            
            has_next = page < total_pages
            has_prev = page > 1
            
            return {
                "items": items,
                "total": total,
                "pages": total_pages,
                "current_page": page,
                "page_size": page_size,
                "has_next": has_next,
                "has_prev": has_prev,
                "next_page": page + 1 if has_next else None,
                "prev_page": page - 1 if has_prev else None,
                "first_item": skip + 1 if items else None,
                "last_item": skip + len(items) if items else None
            }
        else:
            # COUNT olmadan - LIMIT+1 ile has_next kontrolü
            query = select(self.model)
            query = self._apply_soft_delete_filter(query, include_deleted)
            query = self._apply_filters(query, **filters)
            query = self._apply_ordering(query, order_by, order_desc)
            query = self._apply_eager_loading(query, relations, strategy)
            query = query.offset(skip).limit(page_size + 1)
            
            all_items = list(session.execute(query).scalars().unique().all())
            has_next = len(all_items) > page_size
            items = all_items[:page_size]
            
            has_prev = page > 1
            
            return {
                "items": items,
                "total": None,
                "pages": None,
                "current_page": page,
                "page_size": page_size,
                "has_next": has_next,
                "has_prev": has_prev,
                "next_page": page + 1 if has_next else None,
                "prev_page": page - 1 if has_prev else None,
                "first_item": skip + 1 if items else None,
                "last_item": skip + len(items) if items else None
            }

    # ============================================================================
    # READ OPERATIONS
    # ============================================================================

    @handle_db_exceptions
    def count(
        self,
        session: Session,
        *,
        include_deleted: bool = False,
        **filters: Any
    ) -> int:
        """
        Kayıt sayısını döndürür. O(n) - Tek sorgu.
        
        Args:
            session: Database session
            include_deleted: Silinmiş kayıtları dahil et
            **filters: Filtreler
        
        Returns:
            Kayıt sayısı
        
        Example:
            >>> active_count = user_repo.count(session, is_active=True)
        """
        query = select(func.count(self.model.id))
        query = self._apply_soft_delete_filter(query, include_deleted)
        query = self._apply_filters(query, **filters)
        return session.execute(query).scalar() or 0

    @handle_db_exceptions
    def get_all(
        self,
        session: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        order_by: Optional[str] = None,
        order_desc: bool = False,
        include_deleted: bool = False,
        **filters: Any
    ) -> List[ModelType]:
        """
        Tüm kayıtları getirir. O(n) - n = dönen kayıt sayısı.
        
        Args:
            session: Database session
            skip: Atlanacak kayıt sayısı
            limit: Maksimum kayıt sayısı
            order_by: Sıralama alanı
            order_desc: Azalan sıralama
            include_deleted: Silinmiş kayıtları dahil et
            **filters: Filtreler
        
        Returns:
            Model listesi
        
        Example:
            >>> users = user_repo.get_all(session, is_active=True, limit=50)
        """
        query = select(self.model)
        query = self._apply_soft_delete_filter(query, include_deleted)
        query = self._apply_filters(query, **filters)
        query = self._apply_ordering(query, order_by, order_desc)
        query = query.offset(skip).limit(limit)
        return list(session.execute(query).scalars().all())

    @handle_db_exceptions
    def search(
        self,
        session: Session,
        search_term: str,
        search_fields: List[str],
        *,
        skip: int = 0,
        limit: int = 100,
        order_by: Optional[str] = None,
        order_desc: bool = False,
        include_deleted: bool = False,
        **filters: Any
    ) -> List[ModelType]:
        """
        Çoklu alanda arama yapar. O(n) - Tek sorgu.
        
        Args:
            session: Database session
            search_term: Arama terimi
            search_fields: Aranacak alanlar
            skip: Atlanacak kayıt sayısı
            limit: Maksimum kayıt sayısı
            order_by: Sıralama alanı
            order_desc: Azalan sıralama
            include_deleted: Silinmiş kayıtları dahil et
            **filters: Ek filtreler
        
        Returns:
            Model listesi
        
        Example:
            >>> users = user_repo.search(session, "john", ["name", "email"])
        """
        query = select(self.model)
        query = self._apply_soft_delete_filter(query, include_deleted)
        query = self._apply_filters(query, **filters)
        query = self._apply_search(query, search_term, search_fields)
        query = self._apply_ordering(query, order_by, order_desc)
        query = query.offset(skip).limit(limit)
        return list(session.execute(query).scalars().all())

    @handle_db_exceptions
    def get_first(
        self,
        session: Session,
        *,
        order_by: Optional[str] = None,
        order_desc: bool = False,
        include_deleted: bool = False,
        **filters: Any
    ) -> Optional[ModelType]:
        """
        İlk kaydı getirir. O(1) - LIMIT 1.
        
        Args:
            session: Database session
            order_by: Sıralama alanı
            order_desc: Azalan sıralama
            include_deleted: Silinmiş kayıtları dahil et
            **filters: Filtreler
        
        Returns:
            Model instance veya None
        
        Example:
            >>> oldest = user_repo.get_first(session, order_by="created_at")
        """
        results = self.get_all(
            session,
            skip=0,
            limit=1,
            order_by=order_by,
            order_desc=order_desc,
            include_deleted=include_deleted,
            **filters
        )
        return results[0] if results else None

    @handle_db_exceptions
    def get_last(
        self,
        session: Session,
        *,
        order_by: Optional[str] = None,
        order_desc: bool = False,
        include_deleted: bool = False,
        **filters: Any
    ) -> Optional[ModelType]:
        """
        Son kaydı getirir. O(1) - LIMIT 1.
        
        Args:
            session: Database session
            order_by: Sıralama alanı
            order_desc: Azalan sıralama (tersine çevrilir)
            include_deleted: Silinmiş kayıtları dahil et
            **filters: Filtreler
        
        Returns:
            Model instance veya None
        
        Example:
            >>> newest = user_repo.get_last(session, order_by="created_at")
        """
        return self.get_first(
            session,
            order_by=order_by,
            order_desc=not order_desc,
            include_deleted=include_deleted,
            **filters
        )

    @handle_db_exceptions
    def paginate(
        self,
        session: Session,
        *,
        page: int = 1,
        page_size: int = 20,
        include_total: bool = False,
        order_by: Optional[str] = None,
        order_desc: bool = False,
        include_deleted: bool = False,
        **filters: Any
    ) -> Dict[str, Any]:
        """
        Sayfalama ile kayıtları getirir.
        
        Performans:
            - include_total=False (varsayılan): O(n) - 1 sorgu (%50-70 daha hızlı)
            - include_total=True: O(n) - 2 sorgu (count + data)
        
        ⚠️ Performans Uyarıları:
            - Sayfa 50+ için offset-based pagination yavaş olabilir
            - Sayfa 100+ için paginate_cursor() kullanın (10-100x daha hızlı)
            - Büyük offset'lerde (>10000) performans düşer
        
        Args:
            session: Database session
            page: Sayfa numarası (1'den başlar)
            page_size: Sayfa başına kayıt (önerilen: 20-100)
            include_total: Toplam kayıt sayısını hesapla mı? (False = daha hızlı)
            order_by: Sıralama alanı (index'li alan önerilir)
            order_desc: Azalan sıralama
            include_deleted: Silinmiş kayıtları dahil et
            **filters: Filtreler
        
        Returns:
            Dict with pagination metadata:
                - items: List[ModelType] - Mevcut sayfadaki kayıtlar
                - total: Optional[int] - Toplam kayıt sayısı (include_total=False ise None)
                - pages: Optional[int] - Toplam sayfa sayısı (include_total=False ise None)
                - current_page: int - Mevcut sayfa numarası
                - page_size: int - Sayfa başına kayıt sayısı
                - has_next: bool - Sonraki sayfa var mı?
                - has_prev: bool - Önceki sayfa var mı?
                - next_page: Optional[int] - Sonraki sayfa numarası (yoksa None)
                - prev_page: Optional[int] - Önceki sayfa numarası (yoksa None)
                - first_item: Optional[int] - Sayfadaki ilk item'ın sıra numarası (1-based)
                - last_item: Optional[int] - Sayfadaki son item'ın sıra numarası (1-based)
        
        Example:
            >>> # Varsayılan (hızlı, COUNT yok)
            >>> result = user_repo.paginate(session, page=2, page_size=10)
            >>> print(result["has_next"])  # Sadece has_next/prev mevcut
            
            >>> # COUNT ile (tam metadata, daha yavaş)
            >>> result = user_repo.paginate(session, page=2, page_size=10, include_total=True)
            >>> print(result["total"], result["pages"])
            
            >>> # Büyük sayfa numaraları için cursor-based kullanın
            >>> result = user_repo.paginate_cursor(session, page_size=20)
        """
        # Input validation
        if page < 1:
            page = 1
        if page_size < 1:
            page_size = 20
        
        skip = (page - 1) * page_size
        
        # Performans uyarısı: Büyük offset'lerde cursor-based öner
        if skip > 10000:
            # Büyük offset tespit edildi - cursor-based öner
            # Logging yoksa print kullan (opsiyonel)
            pass  # Uyarı verilmez (production'da logging ile yapılabilir)
        
        # include_total=False ise COUNT sorgusunu atla ve has_next kontrolü için LIMIT+1 kullan
        if include_total:
            total = self.count(session, include_deleted=include_deleted, **filters)
            total_pages = (total + page_size - 1) // page_size if total > 0 else 0
            
            items = self.get_all(
                session,
                skip=skip,
                limit=page_size,
                order_by=order_by,
                order_desc=order_desc,
                include_deleted=include_deleted,
                **filters
            )
            
            # Pagination metadata hesaplamaları
            has_next = page < total_pages
            has_prev = page > 1
            next_page = page + 1 if has_next else None
            prev_page = page - 1 if has_prev else None
            
            # Item range hesaplamaları
            first_item = None
            last_item = None
            
            if items:
                first_item = skip + 1  # 1-based index
                last_item = skip + len(items)
            elif total > 0:
                # Items yok ama total > 0 ise (geçersiz sayfa)
                first_item = None
                last_item = None
            
            return {
                "items": items,
                "total": total,
                "pages": total_pages,
                "current_page": page,
                "page_size": page_size,
                "has_next": has_next,
                "has_prev": has_prev,
                "next_page": next_page,
                "prev_page": prev_page,
                "first_item": first_item,
                "last_item": last_item
            }
        else:
            # COUNT olmadan - LIMIT+1 ile has_next kontrolü
            # Bir fazla kayıt getir, eğer page_size+1 kayıt gelirse has_next=True
            query = select(self.model)
            query = self._apply_soft_delete_filter(query, include_deleted)
            query = self._apply_filters(query, **filters)
            query = self._apply_ordering(query, order_by, order_desc)
            query = query.offset(skip).limit(page_size + 1)
            
            all_items = list(session.execute(query).scalars().all())
            has_next = len(all_items) > page_size
            items = all_items[:page_size]  # Sonuncuyu çıkar
            
            # Pagination metadata (total olmadan)
            has_prev = page > 1
            next_page = page + 1 if has_next else None
            prev_page = page - 1 if has_prev else None
            
            # Item range hesaplamaları
            first_item = None
            last_item = None
            
            if items:
                first_item = skip + 1  # 1-based index
                last_item = skip + len(items)
            
            return {
                "items": items,
                "total": None,
                "pages": None,
                "current_page": page,
                "page_size": page_size,
                "has_next": has_next,
                "has_prev": has_prev,
                "next_page": next_page,
                "prev_page": prev_page,
                "first_item": first_item,
                "last_item": last_item
            }

    # ============================================================================
    # CURSOR-BASED PAGINATION (Büyük veri setleri için)
    # ============================================================================

    @handle_db_exceptions
    def paginate_cursor(
        self,
        session: Session,
        *,
        cursor: Optional[str] = None,
        page_size: int = 20,
        order_by: str = "id",
        order_desc: bool = True,
        include_deleted: bool = False,
        **filters: Any
    ) -> Dict[str, Any]:
        """
        Cursor-based pagination - offset-based'den çok daha hızlı.
        
        Performans:
            - O(1) - Tek sorgu, index kullanır
            - Büyük offset'lerde 10-100x daha hızlı
            - COUNT sorgusu yok
        
        Avantajlar:
            - Büyük veri setleri için ideal
            - Real-time data için uygun
            - Offset-based'den çok daha hızlı (sayfa 100+)
        
        Dezavantajlar:
            - Sayfa numarası yok
            - Geri gitmek zor (sadece ileri)
            - Sıralama alanı değişemez
        
        Args:
            session: Database session
            cursor: Son kaydın ID'si (ilk sayfa için None)
            page_size: Sayfa başına kayıt sayısı
            order_by: Sıralama alanı (varsayılan: "id", unique olmalı)
            order_desc: Azalan sıralama (varsayılan: True)
            include_deleted: Silinmiş kayıtları dahil et
            **filters: Filtreler
        
        Returns:
            Dict with cursor pagination metadata:
                - items: List[ModelType] - Mevcut sayfadaki kayıtlar
                - next_cursor: Optional[str] - Sonraki sayfa için cursor (yoksa None)
                - has_next: bool - Sonraki sayfa var mı?
                - page_size: int - Sayfa başına kayıt sayısı
        
        Example:
            >>> # İlk sayfa
            >>> result = user_repo.paginate_cursor(session, page_size=20)
            >>> print(f"Items: {len(result['items'])}")
            >>> print(f"Next cursor: {result['next_cursor']}")
            
            >>> # Sonraki sayfa
            >>> result = user_repo.paginate_cursor(session, cursor=result['next_cursor'])
            >>> print(f"Items: {len(result['items'])}")
        
        Note:
            - order_by alanı unique olmalı (genellikle "id")
            - Sadece ileri yönde pagination (geri gitmek için cursor saklanmalı)
            - Real-time data için ideal (yeni kayıtlar eklenirken tutarlı)
        """
        # Input validation
        if page_size < 1:
            page_size = 20
        
        # Field kontrolü
        if not hasattr(self.model, order_by):
            raise ValidationError(
                errors={"order_by": f"Field '{order_by}' does not exist"},
                message=f"Field '{order_by}' does not exist on {self.model_name}"
            )
        
        cursor_field = getattr(self.model, order_by)
        
        # Query oluştur
        query = select(self.model)
        query = self._apply_soft_delete_filter(query, include_deleted)
        query = self._apply_filters(query, **filters)
        
        # Cursor filtresi (WHERE id > cursor veya WHERE id < cursor)
        if cursor:
            if order_desc:
                # Azalan sıralama: WHERE id < cursor
                query = query.where(cursor_field < cursor)
            else:
                # Artan sıralama: WHERE id > cursor
                query = query.where(cursor_field > cursor)
        
        # Sıralama
        query = self._apply_ordering(query, order_by, order_desc)
        
        # LIMIT+1 ile has_next kontrolü
        query = query.limit(page_size + 1)
        
        # Execute
        all_items = list(session.execute(query).scalars().all())
        has_next = len(all_items) > page_size
        
        # Sonuncuyu çıkar (has_next kontrolü için getirildi)
        items = all_items[:page_size]
        
        # Next cursor (son item'ın order_by alanı)
        next_cursor = None
        if items:
            last_item = items[-1]
            next_cursor = getattr(last_item, order_by)
        
        return {
            "items": items,
            "next_cursor": next_cursor if has_next else None,
            "has_next": has_next,
            "page_size": page_size
        }

    # ============================================================================
    # SPECIAL OPERATIONS
    # ============================================================================

    @handle_db_exceptions
    def get_or_create(
        self,
        session: Session,
        defaults: Optional[Dict[str, Any]] = None,
        *,
        created_by: Optional[str] = None,
        **lookup: Any
    ) -> Tuple[ModelType, bool]:
        """
        Varsa getirir, yoksa oluşturur (atomic operation). O(1) veya O(1) + insert.
        
        This method uses database-specific atomic upsert patterns to prevent race conditions:
        - PostgreSQL: INSERT ... ON CONFLICT DO NOTHING
        - MySQL: INSERT ... ON DUPLICATE KEY UPDATE (id=id)
        - SQLite: INSERT OR IGNORE
        - Fallback: SELECT-then-INSERT with retry
        
        Args:
            session: Database session
            defaults: Oluşturma için ek alanlar (lookup'ta değil)
            created_by: Oluşturan kullanıcı ID'si
            **lookup: Arama kriterleri (unique olmalı)
        
        Returns:
            Tuple[instance, created] - created=True ise yeni oluşturuldu
        
        Example:
            >>> user, created = user_repo.get_or_create(
            ...     session,
            ...     defaults={"name": "John"},
            ...     email="john@test.com"
            ... )
        """
        if not lookup:
            raise ValidationError(
                errors={"lookup": "No lookup criteria provided"},
                message="get_or_create requires lookup criteria"
            )

        # Prepare data
        create_data = {**lookup}
        if defaults:
            create_data.update(defaults)
        
        if created_by and hasattr(self.model, 'created_by'):
            create_data['created_by'] = created_by
        
        # Detect database type
        db_type = _detect_db_type_from_session(session)
        
        # Try atomic upsert first (database-specific)
        if db_type == 'postgresql':
            return self._get_or_create_postgresql(session, lookup, create_data)
        elif db_type == 'mysql':
            return self._get_or_create_mysql(session, lookup, create_data)
        elif db_type == 'sqlite':
            return self._get_or_create_sqlite(session, lookup, create_data)
        else:
            # Fallback to SELECT-then-INSERT with retry
            logger.warning(
                f"get_or_create: Database type '{db_type}' not supported for atomic operations, "
                f"falling back to non-atomic method for {self.model_name}"
            )
            return self._get_or_create_fallback(session, lookup, create_data)
    
    def _get_or_create_postgresql(
        self,
        session: Session,
        lookup: Dict[str, Any],
        create_data: Dict[str, Any]
    ) -> Tuple[ModelType, bool]:
        """PostgreSQL atomic get_or_create using ON CONFLICT."""
        # Get table
        table = self.model.__table__
        
        # Build conflict target columns from lookup keys
        conflict_columns = [table.c[col] for col in lookup.keys() if hasattr(table.c, col)]
        
        if not conflict_columns:
            # Fallback if columns not found
            logger.warning(
                f"PostgreSQL get_or_create: Conflict columns not found for {self.model_name}, "
                f"falling back to non-atomic method. Lookup keys: {list(lookup.keys())}"
            )
            return self._get_or_create_fallback(session, lookup, create_data)
        
        # Build INSERT statement with ON CONFLICT DO NOTHING
        stmt = insert(table).values(**create_data)
        
        # ON CONFLICT clause (works for both single and multiple columns)
        stmt = stmt.on_conflict_do_nothing(index_elements=conflict_columns)
        
        # Execute insert
        result = session.execute(stmt)
        session.flush()
        
        # Check if row was inserted (rowcount > 0) or already existed (rowcount == 0)
        if result.rowcount > 0:
            # New row inserted - fetch it
            obj = self.get_first(session, include_deleted=False, **lookup)
            return obj, True
        else:
            # Row already exists - fetch it
            obj = self.get_first(session, include_deleted=False, **lookup)
            return obj, False
    
    def _get_or_create_mysql(
        self,
        session: Session,
        lookup: Dict[str, Any],
        create_data: Dict[str, Any]
    ) -> Tuple[ModelType, bool]:
        """MySQL atomic get_or_create using ON DUPLICATE KEY UPDATE."""
        table = self.model.__table__
        
        # Build INSERT with ON DUPLICATE KEY UPDATE
        stmt = insert(table).values(**create_data)
        
        # Get primary key column name
        pk_columns = list(table.primary_key.columns)
        if not pk_columns:
            # Fallback if no primary key
            logger.warning(
                f"MySQL get_or_create: No primary key found for {self.model_name}, "
                "falling back to non-atomic method"
            )
            return self._get_or_create_fallback(session, lookup, create_data)
        
        pk_column = pk_columns[0]
        
        # ON DUPLICATE KEY UPDATE - set primary key to itself (no actual update)
        # This prevents actual update but allows us to detect if insert happened
        update_dict = {pk_column.name: pk_column}
        stmt = stmt.on_duplicate_key_update(**update_dict)
        
        # Execute
        result = session.execute(stmt)
        session.flush()
        
        # MySQL returns different rowcount for insert vs update
        # Insert: 1, Update: 2 (1 insert + 1 update)
        if result.rowcount == 1:
            # New row inserted
            obj = self.get_first(session, include_deleted=False, **lookup)
            return obj, True
        else:
            # Row already existed (was updated)
            obj = self.get_first(session, include_deleted=False, **lookup)
            return obj, False
    
    def _get_or_create_sqlite(
        self,
        session: Session,
        lookup: Dict[str, Any],
        create_data: Dict[str, Any]
    ) -> Tuple[ModelType, bool]:
        """SQLite atomic get_or_create using INSERT OR IGNORE."""
        table = self.model.__table__
        
        # SQLite: INSERT OR IGNORE
        stmt = insert(table).values(**create_data).prefix_with('OR IGNORE')
        
        # Execute
        result = session.execute(stmt)
        session.flush()
        
        # Check if row was inserted
        if result.rowcount > 0:
            # New row inserted
            obj = self.get_first(session, include_deleted=False, **lookup)
            return obj, True
        else:
            # Row already exists
            obj = self.get_first(session, include_deleted=False, **lookup)
            return obj, False
    
    def _get_or_create_fallback(
        self,
        session: Session,
        lookup: Dict[str, Any],
        create_data: Dict[str, Any]
    ) -> Tuple[ModelType, bool]:
        """Fallback get_or_create using SELECT-then-INSERT with retry."""
        # Try to find existing
        existing = self.get_first(session, include_deleted=False, **lookup)
        if existing:
            return existing, False
        
        # Create new
        try:
            obj = self.create(session, **create_data)
            return obj, True
        except ValidationError as e:
            # Race condition: someone else created it
            if e.__cause__ and isinstance(e.__cause__, IntegrityError):
                existing = self.get_first(session, include_deleted=False, **lookup)
                if existing:
                    return existing, False
            raise

    @handle_db_exceptions
    def upsert(
        self,
        session: Session,
        unique_fields: List[str],
        *,
        created_by: Optional[str] = None,
        updated_by: Optional[str] = None,
        **data: Any
    ) -> Tuple[ModelType, bool]:
        """
        Varsa günceller, yoksa oluşturur (atomic operation). O(1) + update/insert.
        
        This method uses database-specific atomic upsert patterns to prevent race conditions:
        - PostgreSQL: INSERT ... ON CONFLICT DO UPDATE
        - MySQL: INSERT ... ON DUPLICATE KEY UPDATE
        - SQLite: INSERT OR REPLACE (or INSERT ... ON CONFLICT DO UPDATE)
        - Fallback: SELECT-then-UPDATE/INSERT with retry
        
        Args:
            session: Database session
            unique_fields: Benzersizlik kontrolü için alanlar
            created_by: Oluşturan kullanıcı ID'si
            updated_by: Güncelleyen kullanıcı ID'si
            **data: Tüm veriler (unique_fields dahil)
        
        Returns:
            Tuple[instance, created] - created=True ise yeni oluşturuldu
        
        Example:
            >>> user, created = user_repo.upsert(
            ...     session,
            ...     unique_fields=["email"],
            ...     email="john@test.com",
            ...     name="John Doe"
            ... )
        """
        if not unique_fields:
            raise ValidationError(
                errors={"unique_fields": "No unique fields provided"},
                message="upsert requires unique_fields"
            )
        
        if not data:
            raise ValidationError(
                errors={"data": "No data provided"},
                message="upsert requires data"
            )
        
        # Check unique fields in data
        missing = [f for f in unique_fields if f not in data]
        if missing:
            raise ValidationError(
                errors={"unique_fields": f"Missing: {missing}"},
                message=f"upsert missing unique fields: {missing}"
            )
        
        # Prepare data
        if created_by and hasattr(self.model, 'created_by'):
            data['created_by'] = created_by
        
        # Build lookup
        lookup = {f: data[f] for f in unique_fields}
        
        # Detect database type
        db_type = _detect_db_type_from_session(session)
        
        # Try atomic upsert first (database-specific)
        if db_type == 'postgresql':
            return self._upsert_postgresql(session, unique_fields, lookup, data, updated_by)
        elif db_type == 'mysql':
            return self._upsert_mysql(session, unique_fields, lookup, data, updated_by)
        elif db_type == 'sqlite':
            return self._upsert_sqlite(session, unique_fields, lookup, data, updated_by)
        else:
            # Fallback to SELECT-then-UPDATE/INSERT with retry
            logger.warning(
                f"upsert: Database type '{db_type}' not supported for atomic operations, "
                f"falling back to non-atomic method for {self.model_name}"
            )
            return self._upsert_fallback(session, unique_fields, lookup, data, created_by, updated_by)
    
    def _upsert_postgresql(
        self,
        session: Session,
        unique_fields: List[str],
        lookup: Dict[str, Any],
        data: Dict[str, Any],
        updated_by: Optional[str]
    ) -> Tuple[ModelType, bool]:
        """PostgreSQL atomic upsert using ON CONFLICT DO UPDATE."""
        table = self.model.__table__
        
        # Build conflict target columns
        conflict_columns = [table.c[col] for col in unique_fields if hasattr(table.c, col)]
        
        if not conflict_columns:
            return self._upsert_fallback(session, unique_fields, lookup, data, None, updated_by)
        
        # Prepare update data (exclude unique fields and created_by)
        update_data = {k: v for k, v in data.items() if k not in unique_fields and k != 'created_by'}
        if updated_by and hasattr(self.model, 'updated_by'):
            update_data['updated_by'] = updated_by
        
        # Build INSERT with ON CONFLICT DO UPDATE
        stmt = insert(table).values(**data)
        
        # ON CONFLICT DO UPDATE
        if len(conflict_columns) == 1:
            stmt = stmt.on_conflict_do_update(
                index_elements=conflict_columns,
                set_=update_data
            )
        else:
            stmt = stmt.on_conflict_do_update(
                index_elements=conflict_columns,
                set_=update_data
            )
        
        # Check if record exists before insert (to determine if it's created or updated)
        existing_before = self.get_first(session, include_deleted=False, **lookup)
        was_created = existing_before is None
        
        # Execute
        result = session.execute(stmt)
        session.flush()
        
        # Fetch the record (inserted or updated)
        obj = self.get_first(session, include_deleted=False, **lookup)
        
        return obj, was_created
    
    def _upsert_mysql(
        self,
        session: Session,
        unique_fields: List[str],
        lookup: Dict[str, Any],
        data: Dict[str, Any],
        updated_by: Optional[str]
    ) -> Tuple[ModelType, bool]:
        """MySQL atomic upsert using ON DUPLICATE KEY UPDATE."""
        table = self.model.__table__
        
        # Prepare update data
        update_data = {k: v for k, v in data.items() if k not in unique_fields and k != 'created_by'}
        if updated_by and hasattr(self.model, 'updated_by'):
            update_data['updated_by'] = updated_by
        
        # Build INSERT with ON DUPLICATE KEY UPDATE
        stmt = insert(table).values(**data)
        
        # ON DUPLICATE KEY UPDATE
        stmt = stmt.on_duplicate_key_update(**update_data)
        
        # Execute
        result = session.execute(stmt)
        session.flush()
        
        # Fetch the record
        obj = self.get_first(session, include_deleted=False, **lookup)
        
        # MySQL: rowcount = 1 for insert, 2 for update (1 insert + 1 update)
        created = result.rowcount == 1
        
        return obj, created
    
    def _upsert_sqlite(
        self,
        session: Session,
        unique_fields: List[str],
        lookup: Dict[str, Any],
        data: Dict[str, Any],
        updated_by: Optional[str]
    ) -> Tuple[ModelType, bool]:
        """SQLite atomic upsert using INSERT OR REPLACE or ON CONFLICT DO UPDATE."""
        table = self.model.__table__
        
        # SQLite: Use INSERT OR REPLACE (simpler) or ON CONFLICT DO UPDATE
        # INSERT OR REPLACE deletes and reinserts, so we lose created_at
        # Better to use ON CONFLICT DO UPDATE if available
        
        # Prepare update data
        update_data = {k: v for k, v in data.items() if k not in unique_fields and k != 'created_by'}
        if updated_by and hasattr(self.model, 'updated_by'):
            update_data['updated_by'] = updated_by
        
        # Build conflict target
        conflict_columns = [table.c[col] for col in unique_fields if hasattr(table.c, col)]
        
        if not conflict_columns:
            logger.warning(
                f"PostgreSQL upsert: Conflict columns not found for {self.model_name}, "
                f"falling back to non-atomic method. Unique fields: {unique_fields}"
            )
            return self._upsert_fallback(session, unique_fields, lookup, data, None, updated_by)
        
        # Build INSERT with ON CONFLICT DO UPDATE (SQLite 3.24+)
        stmt = insert(table).values(**data)
        stmt = stmt.on_conflict_do_update(
            index_elements=conflict_columns,
            set_=update_data
        )
        
        # Execute
        result = session.execute(stmt)
        session.flush()
        
        # Fetch the record
        obj = self.get_first(session, include_deleted=False, **lookup)
        
        # Check if record existed before insert
        existing_before = self.get_first(session, include_deleted=False, **lookup)
        was_created = existing_before is None
        
        # Re-fetch after upsert (in case it was updated)
        obj = self.get_first(session, include_deleted=False, **lookup)
        
        return obj, was_created
    
    def _upsert_fallback(
        self,
        session: Session,
        unique_fields: List[str],
        lookup: Dict[str, Any],
        data: Dict[str, Any],
        created_by: Optional[str],
        updated_by: Optional[str]
    ) -> Tuple[ModelType, bool]:
        """Fallback upsert using SELECT-then-UPDATE/INSERT with retry."""
        # Try to find existing
        existing = self.get_first(session, include_deleted=False, **lookup)
        
        if existing:
            # Update
            update_data = {k: v for k, v in data.items() if k not in unique_fields}
            if update_data:
                for key, value in update_data.items():
                    if hasattr(existing, key):
                        setattr(existing, key, value)
                
                if updated_by and hasattr(self.model, 'updated_by'):
                    setattr(existing, 'updated_by', updated_by)
                
                session.add(existing)
                session.flush()
            return existing, False
        
        # Create
        try:
            obj = self.create(session, created_by=created_by, **data)
            return obj, True
        except ValidationError as e:
            if e.__cause__ and isinstance(e.__cause__, IntegrityError):
                existing = self.get_first(session, include_deleted=False, **lookup)
                if existing:
                    # Update
                    update_data = {k: v for k, v in data.items() if k not in unique_fields}
                    if update_data:
                        for key, value in update_data.items():
                            if hasattr(existing, key):
                                setattr(existing, key, value)
                        if updated_by and hasattr(self.model, 'updated_by'):
                            setattr(existing, 'updated_by', updated_by)
                        session.add(existing)
                        session.flush()
                    return existing, False
            raise

