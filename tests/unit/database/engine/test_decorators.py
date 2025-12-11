"""
Database decorator'ları için testler.
"""

import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session

from miniflow.database.engine.decorators import (
    with_session,
    with_transaction_session,
    with_readonly_session,
    with_retry_session,
    inject_session
)
from miniflow.database.engine.manager import DatabaseManager
from miniflow.core.exceptions import (
    DatabaseDecoratorManagerError,
    DatabaseDecoratorSignatureError
)


@pytest.mark.unit
@pytest.mark.database
@pytest.mark.engine
class TestWithSession:
    """with_session decorator için testler."""

    # --- Temel Kullanım Testleri ---
    def test_with_session_injects_session(self, database_manager_initialized):
        """with_session decorator session parametresini inject eder."""
        @with_session()
        def test_function(session: Session):
            assert isinstance(session, Session)
            return "success"
        
        result = test_function()
        assert result == "success"

    def test_with_session_auto_commits_on_success(self, database_manager_initialized):
        """with_session decorator başarılı işlemde otomatik commit yapar."""
        @with_session(auto_commit=True)
        def test_function(session: Session):
            return "success"
        
        result = test_function()
        assert result == "success"

    def test_with_session_respects_auto_commit_false(self, database_manager_initialized):
        """with_session decorator auto_commit=False olduğunda commit yapmaz."""
        @with_session(auto_commit=False)
        def test_function(session: Session):
            return "success"
        
        result = test_function()
        assert result == "success"

    def test_with_session_rolls_back_on_error(self, database_manager_initialized):
        """with_session decorator hata durumunda rollback yapar."""
        @with_session()
        def test_function(session: Session):
            raise ValueError("Test error")
        
        with pytest.raises(ValueError):
            test_function()

    def test_with_session_raises_error_when_manager_not_initialized(self):
        """with_session decorator manager başlatılmamışsa hata fırlatır."""
        # Singleton'ı sıfırla
        DatabaseManager._instance = None
        
        @with_session()
        def test_function(session: Session):
            return "success"
        
        from miniflow.core.exceptions import DatabaseManagerNotInitializedError
        with pytest.raises((DatabaseDecoratorManagerError, DatabaseManagerNotInitializedError)):
            test_function()

    def test_with_session_raises_error_when_no_session_parameter(self, database_manager_initialized):
        """with_session decorator session parametresi yoksa hata fırlatır."""
        with pytest.raises(DatabaseDecoratorSignatureError):
            @with_session()
            def test_function_without_session():
                return "success"

    def test_with_session_uses_custom_manager(self, sqlite_config_memory):
        """with_session decorator özel manager kullanır."""
        custom_manager = DatabaseManager()
        custom_manager.initialize(sqlite_config_memory, auto_start=True)
        
        @with_session(manager=custom_manager)
        def test_function(session: Session):
            assert isinstance(session, Session)
            return "success"
        
        result = test_function()
        assert result == "success"
        
        custom_manager.reset(full_reset=True)


@pytest.mark.unit
@pytest.mark.database
@pytest.mark.engine
class TestWithTransactionSession:
    """with_transaction_session decorator için testler."""

    # --- Temel Kullanım Testleri ---
    def test_with_transaction_injects_session(self, database_manager_initialized):
        """with_transaction_session decorator session parametresini inject eder."""
        @with_transaction_session()
        def test_function(session: Session):
            assert isinstance(session, Session)
            return "success"
        
        result = test_function()
        assert result == "success"

    def test_with_transaction_auto_commits(self, database_manager_initialized):
        """with_transaction_session decorator otomatik commit yapar."""
        @with_transaction_session()
        def test_function(session: Session):
            return "success"
        
        result = test_function()
        assert result == "success"

    def test_with_transaction_rolls_back_on_error(self, database_manager_initialized):
        """with_transaction_session decorator hata durumunda rollback yapar."""
        @with_transaction_session()
        def test_function(session: Session):
            raise ValueError("Test error")
        
        with pytest.raises(ValueError):
            test_function()

    def test_with_transaction_raises_error_when_no_session_parameter(self, database_manager_initialized):
        """with_transaction_session decorator session parametresi yoksa hata fırlatır."""
        with pytest.raises(DatabaseDecoratorSignatureError):
            @with_transaction_session()
            def test_function_without_session():
                return "success"


@pytest.mark.unit
@pytest.mark.database
@pytest.mark.engine
class TestWithReadonlySession:
    """with_readonly_session decorator için testler."""

    # --- Temel Kullanım Testleri ---
    def test_with_readonly_injects_session(self, database_manager_initialized):
        """with_readonly_session decorator session parametresini inject eder."""
        @with_readonly_session()
        def test_function(session: Session):
            assert isinstance(session, Session)
            return "success"
        
        result = test_function()
        assert result == "success"

    def test_with_readonly_does_not_commit(self, database_manager_initialized):
        """with_readonly_session decorator commit yapmaz."""
        @with_readonly_session()
        def test_function(session: Session):
            return "success"
        
        result = test_function()
        assert result == "success"

    def test_with_readonly_raises_error_when_no_session_parameter(self, database_manager_initialized):
        """with_readonly_session decorator session parametresi yoksa hata fırlatır."""
        with pytest.raises(DatabaseDecoratorSignatureError):
            @with_readonly_session()
            def test_function_without_session():
                return "success"


@pytest.mark.unit
@pytest.mark.database
@pytest.mark.engine
class TestWithRetrySession:
    """with_retry_session decorator için testler."""

    # --- Temel Kullanım Testleri ---
    def test_with_retry_injects_session(self, database_manager_initialized):
        """with_retry_session decorator session parametresini inject eder."""
        @with_retry_session(max_attempts=3, delay=0.01)
        def test_function(session: Session):
            assert isinstance(session, Session)
            return "success"
        
        result = test_function()
        assert result == "success"

    def test_with_retry_retries_on_deadlock(self, database_manager_initialized):
        """with_retry_session decorator deadlock hatasında retry yapar."""
        call_count = 0
        
        @with_retry_session(max_attempts=3, delay=0.01)
        def test_function(session: Session):
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                from sqlalchemy.exc import OperationalError
                error = OperationalError("Deadlock detected", None, None)
                error.errno = 1213
                raise error
            return "success"
        
        result = test_function()
        assert result == "success"
        assert call_count == 2

    def test_with_retry_respects_max_attempts(self, database_manager_initialized):
        """with_retry_session decorator maksimum deneme sayısına uyar."""
        call_count = 0
        
        @with_retry_session(max_attempts=2, delay=0.01)
        def test_function(session: Session):
            nonlocal call_count
            call_count += 1
            from sqlalchemy.exc import OperationalError
            error = OperationalError("Deadlock detected", None, None)
            error.errno = 1213
            raise error
        
        from miniflow.core.exceptions import DatabaseQueryError
        with pytest.raises(DatabaseQueryError):
            test_function()
        
        assert call_count == 2

    def test_with_retry_validates_max_attempts(self):
        """with_retry_session decorator geçersiz max_attempts için ValueError fırlatır."""
        with pytest.raises(ValueError):
            @with_retry_session(max_attempts=0)
            def test_function(session: Session):
                return "success"

    def test_with_retry_validates_delay(self):
        """with_retry_session decorator geçersiz delay için ValueError fırlatır."""
        with pytest.raises(ValueError):
            @with_retry_session(delay=-1)
            def test_function(session: Session):
                return "success"

    def test_with_retry_validates_backoff(self):
        """with_retry_session decorator geçersiz backoff için ValueError fırlatır."""
        with pytest.raises(ValueError):
            @with_retry_session(backoff=0)
            def test_function(session: Session):
                return "success"


@pytest.mark.unit
@pytest.mark.database
@pytest.mark.engine
class TestInjectSession:
    """inject_session decorator için testler."""

    # --- Temel Kullanım Testleri ---
    def test_inject_session_injects_as_keyword_argument(self, database_manager_initialized):
        """inject_session decorator session'ı keyword argument olarak inject eder."""
        @inject_session()
        def test_function(user_id: str, session: Session = None):
            assert isinstance(session, Session)
            return "success"
        
        result = test_function("user123")
        assert result == "success"

    def test_inject_session_respects_manual_session(self, database_manager_initialized):
        """inject_session decorator manuel session geçildiğinde onu kullanır."""
        @inject_session()
        def test_function(user_id: str, session: Session = None):
            return session
        
        manual_session = database_manager_initialized.engine.get_session()
        result = test_function("user123", session=manual_session)
        
        assert result is manual_session
        manual_session.close()

    def test_inject_session_uses_custom_parameter_name(self, database_manager_initialized):
        """inject_session decorator özel parametre adı kullanır."""
        @inject_session(parameter_name='db_session')
        def test_function(user_id: str, db_session: Session = None):
            assert isinstance(db_session, Session)
            return "success"
        
        result = test_function("user123")
        assert result == "success"

    def test_inject_session_raises_error_when_manager_not_initialized(self):
        """inject_session decorator manager başlatılmamışsa hata fırlatır."""
        # Singleton'ı sıfırla
        DatabaseManager._instance = None
        
        @inject_session()
        def test_function(user_id: str, session: Session = None):
            return "success"
        
        from miniflow.core.exceptions import DatabaseManagerNotInitializedError
        with pytest.raises((DatabaseDecoratorManagerError, DatabaseManagerNotInitializedError)):
            test_function("user123")

