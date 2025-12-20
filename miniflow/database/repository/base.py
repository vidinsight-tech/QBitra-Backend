"""
Base Repository - Temel CRUD İşlemleri

Bu modül, tüm repository'ler için temel CRUD operasyonlarını sağlar.
SQLAlchemy exception'larını custom exception'lara dönüştürür.

Kullanım:
    >>> from miniflow.database.repository import BaseRepository
    >>> from miniflow.models.user_models.users import User
    >>> 
    >>> class UserRepository(BaseRepository[User]):
    ...     def __init__(self):
    ...         super().__init__(User)
    >>> 
    >>> user_repo = UserRepository()
"""

from typing import Any, Generic, List, Optional, TypeVar, cast, Union
from functools import wraps
from datetime import datetime, timezone

from sqlalchemy import select, exists, update
from sqlalchemy.orm import DeclarativeBase, Session
from sqlalchemy.sql import Select
from sqlalchemy.exc import (
    SQLAlchemyError,
    IntegrityError,
    OperationalError,
    DataError,
    ProgrammingError,
    InvalidRequestError,
    TimeoutError as SQLAlchemyTimeoutError
)

from miniflow.core.exceptions import (
    AppException,
    DatabaseQueryError,
    DatabaseConnectionError,
    DatabaseSessionError,
    ValidationError,
    ResourceNotFoundError,
)


ModelType = TypeVar("ModelType", bound=DeclarativeBase)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _safe_rollback_session(session: Optional[Session]) -> None:
    """
    Session'ı güvenli bir şekilde rollback eder (session poisoning önleme).
    
    SQLAlchemy hatalarından sonra session'ın failed state'de kalmasını önler.
    Bu sayede sonraki işlemler PendingRollbackError almaz.
    
    Args:
        session: Rollback edilecek session (None ise hiçbir şey yapılmaz)
    
    Note:
        - Session None ise sessizce geçer
        - Rollback hatası original exception'ı mask etmez (try/except içinde)
        - Session.is_active kontrolü yapar
    """
    if session is None:
        return
    
    try:
        # Only rollback if session is active and in a transaction
        if hasattr(session, 'is_active') and session.is_active:
            if hasattr(session, 'in_transaction') and session.in_transaction():
                session.rollback()
    except Exception:
        # Silently ignore rollback errors to avoid masking original exception
        # The session_context or outer transaction handler will handle cleanup
        pass


# ============================================================================
# EXCEPTION HANDLER DECORATOR
# ============================================================================

def handle_db_exceptions(func):
    """
    Veritabanı hatalarını yakalayıp özel exception'lara dönüştüren dekoratör.
    
    SQLAlchemy exception'larını yakalayıp anlamlı, custom exception'lara dönüştürür.
    Model adını otomatik olarak self.model_name'den alır.
    
    Exception Dönüşümleri:
        - IntegrityError → ValidationError (constraint violations)
        - DataError → DatabaseQueryError (data type errors)
        - ProgrammingError → DatabaseQueryError (SQL errors)
        - OperationalError → DatabaseConnectionError (connection issues)
        - TimeoutError → DatabaseConnectionError (timeouts)
        - InvalidRequestError → DatabaseSessionError (session issues)
        - SQLAlchemyError → DatabaseQueryError (catch-all)
    
    Session Poisoning Prevention:
        - SQLAlchemy hatalarından sonra session'ı rollback eder
        - Session'ın failed state'de kalmasını önler
        - Sonraki işlemlerin PendingRollbackError almasını engeller
    
    Note:
        - AppException ve alt sınıfları re-raise edilir
        - Exception chaining korunur (from e)
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        # Extract session from arguments (typically first arg after self)
        session = None
        if args:
            # Check if first arg is a Session instance
            from sqlalchemy.orm import Session as SQLSession
            if isinstance(args[0], SQLSession):
                session = args[0]
        if session is None and 'session' in kwargs:
            session = kwargs.get('session')
        
        try:
            return func(self, *args, **kwargs)
        
        except IntegrityError as e:
            # Rollback session to prevent poisoning
            _safe_rollback_session(session)
            
            error_msg = str(e).lower()
            
            if "unique" in error_msg or "duplicate" in error_msg:
                constraint_type = "Unique constraint violation"
            elif "foreign key" in error_msg:
                constraint_type = "Foreign key constraint violation"
            elif "not null" in error_msg or "null value" in error_msg:
                constraint_type = "Not null constraint violation"
            elif "check constraint" in error_msg:
                constraint_type = "Check constraint violation"
            else:
                constraint_type = "Constraint violation"
            
            raise ValidationError(
                errors={"constraint": constraint_type},
                message=f"Failed to {func.__name__} {self.model_name}: {constraint_type}"
            ) from e
        
        except DataError as e:
            # Rollback session to prevent poisoning
            _safe_rollback_session(session)
            
            raise DatabaseQueryError(
                f"Data error for {self.model_name} during {func.__name__}"
            ) from e
        
        except ProgrammingError as e:
            # Rollback session to prevent poisoning
            _safe_rollback_session(session)
            
            raise DatabaseQueryError(
                f"SQL error for {self.model_name} during {func.__name__}"
            ) from e
        
        except OperationalError as e:
            # Rollback session to prevent poisoning
            _safe_rollback_session(session)
            
            raise DatabaseConnectionError(
                f"Database connection error for {self.model_name} during {func.__name__}"
            ) from e
        
        except SQLAlchemyTimeoutError as e:
            # Rollback session to prevent poisoning
            _safe_rollback_session(session)
            
            raise DatabaseConnectionError(
                f"Database timeout for {self.model_name} during {func.__name__}"
            ) from e
        
        except InvalidRequestError as e:
            # Rollback session to prevent poisoning
            _safe_rollback_session(session)
            
            raise DatabaseSessionError(
                f"Invalid session for {self.model_name} during {func.__name__}"
            ) from e
        
        except AppException:
            # Don't rollback for application exceptions (they're expected)
            raise
        
        except SQLAlchemyError as e:
            # Rollback session to prevent poisoning
            _safe_rollback_session(session)
            
            raise DatabaseQueryError(
                f"Database error for {self.model_name} during {func.__name__}"
            ) from e
        
        except Exception as e:
            # Rollback session for any unexpected database-related errors
            _safe_rollback_session(session)
            
            raise DatabaseQueryError(
                f"Unexpected error for {self.model_name} during {func.__name__}"
            ) from e
    
    return wrapper


# ============================================================================
# BASE REPOSITORY
# ============================================================================

class BaseRepository(Generic[ModelType]):
    """
    Temel CRUD işlemleri için base repository sınıfı.
    
    Tüm repository'ler bu sınıftan türetilmelidir. Temel CRUD operasyonlarını
    (Create, Read, Update, Delete) ve soft delete işlemlerini sağlar.
    
    Özellikler:
        - Exception handling (SQLAlchemy → custom exceptions)
        - Soft delete desteği
        - Audit field desteği (created_by, updated_by, deleted_by)
        - Transaction-agnostic (flush kullanır, commit kullanmaz)
    
    Kullanım:
        >>> class UserRepository(BaseRepository[User]):
        ...     def __init__(self):
        ...         super().__init__(User)
        >>> 
        >>> user_repo = UserRepository()
        >>> user = user_repo.create(session, email="test@test.com", name="John")
    """
    
    def __init__(self, model: ModelType):
        self.model = model
        self.model_name = model.__name__

    # ============================================================================
    # HELPER METHODS
    # ============================================================================

    def _raise_not_found(self, record_id: str) -> None:
        """Kayıt bulunamadığında ResourceNotFoundError fırlatır."""
        raise ResourceNotFoundError(
            resource_type=self.model_name,
            resource_path=record_id,
            message=f"{self.model_name} with id '{record_id}' not found"
        )

    def _apply_soft_delete_filter(self, query: Select, include_deleted: bool = False) -> Select:
        """Soft delete filtresini sorguya uygular. O(1)"""
        if not include_deleted and hasattr(self.model, 'is_deleted'):
            query = query.where(getattr(self.model, 'is_deleted').is_(False))
        return query

    # ============================================================================
    # CREATE
    # ============================================================================

    @handle_db_exceptions
    def create(
        self,
        session: Session,
        *,
        created_by: Optional[str] = None,
        **kwargs: Any
    ) -> ModelType:
        """
        Yeni bir kayıt oluşturur. O(1).
        
        Args:
            session: Database session
            created_by: Kaydı oluşturan kullanıcı ID'si
            **kwargs: Model alanları
        
        Returns:
            Oluşturulan model instance
        
        Raises:
            ValidationError: Veri boş veya constraint ihlali
        
        Example:
            >>> user = user_repo.create(session, email="test@test.com", name="John")
        """
        if not kwargs:
            raise ValidationError(
                errors={"data": "No data provided"},
                message="Cannot create record: no data provided"
            )
        
        if created_by and hasattr(self.model, 'created_by'):
            kwargs['created_by'] = created_by
        
        obj = cast(ModelType, self.model(**kwargs))
        session.add(obj)
        session.flush()
        return obj

    # ============================================================================
    # READ
    # ============================================================================

    @handle_db_exceptions
    def get_by_id(
        self,
        session: Session,
        record_id: str,
        *,
        raise_not_found: bool = True,
        include_deleted: bool = False
    ) -> Optional[ModelType]:
        """
        ID'ye göre kayıt getirir. O(1) - Primary key lookup.
        
        Args:
            session: Database session
            record_id: Kayıt ID'si
            raise_not_found: Bulunamazsa hata fırlat
            include_deleted: Silinmiş kayıtları dahil et
        
        Returns:
            Model instance veya None
        
        Example:
            >>> user = user_repo.get_by_id(session, "USR-123")
        """
        result = session.get(self.model, record_id)

        if result and not include_deleted and hasattr(self.model, 'is_deleted'):
            if getattr(result, 'is_deleted', False):
                if raise_not_found:
                    self._raise_not_found(record_id)
                return None

        if result is None and raise_not_found:
            self._raise_not_found(record_id)

        return result

    @handle_db_exceptions
    def get_by_ids(
        self,
        session: Session,
        record_ids: List[str],
        *,
        include_deleted: bool = False
    ) -> List[ModelType]:
        """
        Birden fazla ID ile kayıtları getirir. O(n) - Tek sorgu.
        
        N+1 problemini önler. Loop yerine bu metodu kullanın.
        
        Args:
            session: Database session
            record_ids: ID listesi
            include_deleted: Silinmiş kayıtları dahil et
        
        Returns:
            Model listesi
        
        Example:
            >>> users = user_repo.get_by_ids(session, ["USR-1", "USR-2", "USR-3"])
        """
        if not record_ids:
            return []

        query = select(self.model).where(self.model.id.in_(record_ids))
        query = self._apply_soft_delete_filter(query, include_deleted)
        return list(session.execute(query).scalars().all())

    @handle_db_exceptions
    def exists(
        self,
        session: Session,
        record_id: str,
        *,
        include_deleted: bool = False
    ) -> bool:
        """
        Kaydın var olup olmadığını kontrol eder. O(1).
        
        Args:
            session: Database session
            record_id: Kayıt ID'si
            include_deleted: Silinmiş kayıtları dahil et
        
        Returns:
            True/False
        
        Example:
            >>> if user_repo.exists(session, "USR-123"):
            ...     print("User exists")
        """
        if not include_deleted and hasattr(self.model, 'is_deleted'):
            query = exists().where(
                self.model.id == record_id,
                getattr(self.model, 'is_deleted').is_(False)
            )
        else:
            query = exists().where(self.model.id == record_id)
        
        return session.query(query).scalar()

    # ============================================================================
    # UPDATE
    # ============================================================================

    @handle_db_exceptions
    def update(
        self,
        session: Session,
        record_id: str,
        *,
        updated_by: Optional[str] = None,
        **kwargs: Any
    ) -> ModelType:
        """
        Kaydı günceller. O(1).
        
        Args:
            session: Database session
            record_id: Kayıt ID'si
            updated_by: Güncelleyen kullanıcı ID'si
            **kwargs: Güncellenecek alanlar
        
        Returns:
            Güncellenmiş model instance
        
        Example:
            >>> user = user_repo.update(session, "USR-123", name="Jane")
        """
        if not kwargs:
            raise ValidationError(
                errors={"data": "No data provided"},
                message="Cannot update record: no data provided"
            )
        
        obj = self.get_by_id(session, record_id, raise_not_found=True)

        if updated_by and hasattr(self.model, 'updated_by'):
            kwargs['updated_by'] = updated_by

        for key, value in kwargs.items():
            if hasattr(obj, key):
                setattr(obj, key, value)

        session.add(obj)
        session.flush()
        return obj

    @handle_db_exceptions
    def increment(
        self,
        session: Session,
        record_id: str,
        field: str,
        amount: Union[int, float] = 1,
        *,
        updated_by: Optional[str] = None
    ) -> ModelType:
        """
        Sayısal alanı artırır (database-level atomik). O(1).
        
        Database-level atomik işlem kullanır, race condition riski yok.
        
        Args:
            session: Database session
            record_id: Kayıt ID'si
            field: Alan adı
            amount: Artış miktarı (varsayılan: 1)
            updated_by: Güncelleyen kullanıcı ID'si
        
        Returns:
            Güncellenmiş model instance
        
        Example:
            >>> post = post_repo.increment(session, "PST-1", "view_count")
        """
        # Field varlık kontrolü
        if not hasattr(self.model, field):
            raise ValidationError(
                errors={"field": f"Field '{field}' does not exist"},
                message=f"Field '{field}' does not exist on {self.model_name}"
            )
        
        field_column = getattr(self.model, field)
        
        # Database-level atomik update
        update_values = {field: field_column + amount}
        
        # updated_by ekle (eğer model destekliyorsa)
        if updated_by and hasattr(self.model, 'updated_by'):
            update_values['updated_by'] = updated_by
        
        # updated_at otomatik güncellenir (TimestampMixin varsa)
        # Eğer manuel kontrol gerekiyorsa:
        if hasattr(self.model, 'updated_at'):
            update_values['updated_at'] = datetime.now(timezone.utc)
        
        # Atomik update statement
        stmt = (
            update(self.model)
            .where(self.model.id == record_id)
            .values(**update_values)
        )
        
        # Execute update
        result = session.execute(stmt)
        
        # Kayıt bulunamadıysa hata fırlat
        if result.rowcount == 0:
            self._raise_not_found(record_id)
        
        # Güncellenmiş objeyi geri yükle
        session.flush()
        obj = self.get_by_id(session, record_id, raise_not_found=True)
        
        return obj

    @handle_db_exceptions
    def decrement(
        self,
        session: Session,
        record_id: str,
        field: str,
        amount: Union[int, float] = 1,
        *,
        updated_by: Optional[str] = None,
        allow_negative: bool = False
    ) -> ModelType:
        """
        Sayısal alanı azaltır (database-level atomik). O(1).
        
        Database-level atomik işlem kullanır, race condition riski yok.
        allow_negative=False ise database-level WHERE kontrolü yapılır.
        
        Args:
            session: Database session
            record_id: Kayıt ID'si
            field: Alan adı
            amount: Azaltma miktarı (varsayılan: 1)
            updated_by: Güncelleyen kullanıcı ID'si
            allow_negative: Negatif değere izin ver
        
        Returns:
            Güncellenmiş model instance
        
        Example:
            >>> product = product_repo.decrement(session, "PRD-1", "stock", 5)
        """
        # Field varlık kontrolü
        if not hasattr(self.model, field):
            raise ValidationError(
                errors={"field": f"Field '{field}' does not exist"},
                message=f"Field '{field}' does not exist on {self.model_name}"
            )
        
        field_column = getattr(self.model, field)
        
        # Database-level atomik update
        update_values = {field: field_column - amount}
        
        # updated_by ekle
        if updated_by and hasattr(self.model, 'updated_by'):
            update_values['updated_by'] = updated_by
        
        # updated_at güncelle
        if hasattr(self.model, 'updated_at'):
            update_values['updated_at'] = datetime.now(timezone.utc)
        
        # Atomik update statement
        stmt = update(self.model).where(self.model.id == record_id)
        
        # allow_negative=False ise database-level kontrol (WHERE field >= amount)
        if not allow_negative:
            stmt = stmt.where(field_column >= amount)
        
        stmt = stmt.values(**update_values)
        
        # Execute update
        result = session.execute(stmt)
        
        # Kayıt bulunamadı veya yeterli değer yok
        if result.rowcount == 0:
            # Kaydın var olup olmadığını kontrol et
            obj = self.get_by_id(session, record_id, raise_not_found=False)
            if obj is None:
                self._raise_not_found(record_id)
            else:
                # Kayıt var ama yeterli değer yok
                current = getattr(obj, field) or 0
                raise ValidationError(
                    errors={"field": f"Insufficient value in '{field}'"},
                    message=f"Cannot decrement: {field} is {current}, need at least {amount}"
                )
        
        # Güncellenmiş objeyi geri yükle
        session.flush()
        obj = self.get_by_id(session, record_id, raise_not_found=True)
        
        return obj

    @handle_db_exceptions
    def refresh(
        self,
        session: Session,
        obj: ModelType
    ) -> ModelType:
        """
        Objeyi veritabanından yeniden yükler. O(1).
        
        Args:
            session: Database session
            obj: Yenilenecek model instance
        
        Returns:
            Yenilenen model instance
        
        Example:
            >>> user = user_repo.refresh(session, user)
        """
        session.refresh(obj)
        return obj

    # ============================================================================
    # DELETE
    # ============================================================================

    @handle_db_exceptions
    def delete(
        self,
        session: Session,
        record_id: str
    ) -> ModelType:
        """
        Kaydı kalıcı olarak siler (hard delete). O(1).
        
        ⚠️ Bu işlem geri alınamaz! Soft delete için soft_delete() kullanın.
        
        Args:
            session: Database session
            record_id: Kayıt ID'si
        
        Returns:
            Silinen model instance
        
        Example:
            >>> deleted = user_repo.delete(session, "USR-123")
        """
        obj = self.get_by_id(session, record_id, raise_not_found=True)
        session.delete(obj)
        session.flush()
        return obj

    @handle_db_exceptions
    def soft_delete(
        self,
        session: Session,
        record_id: str,
        *,
        deleted_by: Optional[str] = None
    ) -> ModelType:
        """
        Kaydı geçici olarak siler (soft delete). O(1).
        
        is_deleted=True ve deleted_at timestamp set edilir.
        restore() ile geri yüklenebilir.
        
        Args:
            session: Database session
            record_id: Kayıt ID'si
            deleted_by: Silen kullanıcı ID'si
        
        Returns:
            Soft delete edilmiş model instance
        
        Example:
            >>> user = user_repo.soft_delete(session, "USR-123", deleted_by="admin")
        """
        obj = self.get_by_id(session, record_id, raise_not_found=True, include_deleted=False)

        if not hasattr(self.model, 'is_deleted'):
            raise ValidationError(
                errors={"model": "Soft delete not supported"},
                message=f"{self.model_name} does not support soft delete"
            )

        setattr(obj, 'is_deleted', True)
        
        if hasattr(self.model, 'deleted_at'):
            setattr(obj, 'deleted_at', datetime.now(timezone.utc))

        if deleted_by and hasattr(self.model, 'deleted_by'):
            setattr(obj, 'deleted_by', deleted_by)

        session.add(obj)
        session.flush()
        return obj

    @handle_db_exceptions
    def restore(
        self,
        session: Session,
        record_id: str,
        *,
        restored_by: Optional[str] = None
    ) -> ModelType:
        """
        Soft delete edilmiş kaydı geri yükler. O(1).
        
        Args:
            session: Database session
            record_id: Kayıt ID'si
            restored_by: Geri yükleyen kullanıcı ID'si
        
        Returns:
            Geri yüklenmiş model instance
        
        Example:
            >>> user = user_repo.restore(session, "USR-123")
        """
        obj = self.get_by_id(session, record_id, raise_not_found=True, include_deleted=True)

        if not hasattr(self.model, 'is_deleted'):
            raise ValidationError(
                errors={"model": "Soft delete not supported"},
                message=f"{self.model_name} does not support restore"
            )

        if not getattr(obj, 'is_deleted', False):
            raise ValidationError(
                errors={"record": "Record is not deleted"},
                message=f"{self.model_name} with id '{record_id}' is not deleted"
            )

        setattr(obj, 'is_deleted', False)
        
        if hasattr(self.model, 'deleted_at'):
            setattr(obj, 'deleted_at', None)

        if hasattr(self.model, 'deleted_by'):
            setattr(obj, 'deleted_by', None)

        if restored_by and hasattr(self.model, 'restored_by'):
            setattr(obj, 'restored_by', restored_by)
            if hasattr(self.model, 'restored_at'):
                setattr(obj, 'restored_at', datetime.now(timezone.utc))

        session.add(obj)
        session.flush()
        return obj

