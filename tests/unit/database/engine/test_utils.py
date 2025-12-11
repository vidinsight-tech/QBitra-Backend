"""
Database Engine yardımcı fonksiyonları için testler.
"""

import pytest
import time
from unittest.mock import Mock, patch
from sqlalchemy.exc import OperationalError, DBAPIError

from miniflow.database.engine.engine import _is_deadlock_error, with_retry


@pytest.mark.unit
@pytest.mark.database
@pytest.mark.engine
class TestIsDeadlockError:
    """_is_deadlock_error fonksiyonu için testler."""

    # --- PostgreSQL Error Code Testleri ---
    def test_detects_postgresql_deadlock_via_pgcode(self):
        """PostgreSQL deadlock hatasını pgcode attribute ile tespit eder."""
        error = Mock()
        error.pgcode = '40P01'
        assert _is_deadlock_error(error) is True

    def test_detects_postgresql_serialization_failure_via_pgcode(self):
        """PostgreSQL serialization failure hatasını pgcode attribute ile tespit eder."""
        error = Mock()
        error.pgcode = '40001'
        assert _is_deadlock_error(error) is True

    def test_detects_postgresql_deadlock_via_sqlstate(self):
        """PostgreSQL deadlock hatasını sqlstate attribute ile tespit eder."""
        error = Mock()
        error.sqlstate = '40P01'
        assert _is_deadlock_error(error) is True

    # --- SQLite Error Code Testleri ---
    def test_detects_sqlite_busy_via_sqlite_errno(self):
        """SQLite busy hatasını sqlite_errno attribute ile tespit eder."""
        error = Mock()
        error.sqlite_errno = 5
        assert _is_deadlock_error(error) is True

    def test_detects_sqlite_locked_via_sqlite_errno(self):
        """SQLite locked hatasını sqlite_errno attribute ile tespit eder."""
        error = Mock()
        error.sqlite_errno = 6
        assert _is_deadlock_error(error) is True

    # --- MySQL/MariaDB Error Code Testleri ---
    def test_detects_mysql_deadlock_via_errno(self):
        """MySQL deadlock hatasını errno attribute ile tespit eder."""
        error = Mock()
        error.errno = 1213
        assert _is_deadlock_error(error) is True

    def test_detects_mysql_lock_wait_timeout_via_errno(self):
        """MySQL lock wait timeout hatasını errno attribute ile tespit eder."""
        error = Mock()
        error.errno = 1205
        assert _is_deadlock_error(error) is True

    # --- SQL Server Error Code Testleri ---
    def test_detects_sql_server_deadlock_via_errno(self):
        """SQL Server deadlock hatasını errno attribute ile tespit eder."""
        error = Mock()
        error.errno = 1205
        assert _is_deadlock_error(error) is True

    def test_detects_sql_server_lock_timeout_via_errno(self):
        """SQL Server lock timeout hatasını errno attribute ile tespit eder."""
        error = Mock()
        error.errno = 1222
        assert _is_deadlock_error(error) is True

    # --- String-Based Detection Testleri ---
    def test_detects_deadlock_via_string_matching(self):
        """Deadlock kelimesi içeren hataları string eşleştirme ile tespit eder."""
        error = Exception("Deadlock detected when trying to get lock")
        assert _is_deadlock_error(error) is True

    def test_detects_lock_timeout_via_string_matching(self):
        """Lock timeout içeren hataları string eşleştirme ile tespit eder."""
        error = Exception("Lock timeout exceeded")
        assert _is_deadlock_error(error) is True

    def test_detects_serialization_failure_via_string_matching(self):
        """Serialization failure içeren hataları string eşleştirme ile tespit eder."""
        error = Exception("Serialization failure detected")
        assert _is_deadlock_error(error) is True

    def test_detects_database_locked_via_string_matching(self):
        """Database locked içeren hataları string eşleştirme ile tespit eder."""
        error = Exception("Database is locked")
        assert _is_deadlock_error(error) is True

    def test_detects_mysql_error_code_via_string_matching(self):
        """MySQL error code'larını string eşleştirme ile tespit eder."""
        error = Exception("Error 1213: Deadlock found")
        assert _is_deadlock_error(error) is True

    def test_detects_postgresql_error_code_via_string_matching(self):
        """PostgreSQL error code'larını string eşleştirme ile tespit eder."""
        error = Exception("Error 40P01: deadlock_detected")
        assert _is_deadlock_error(error) is True

    def test_detects_oracle_error_code_via_string_matching(self):
        """Oracle error code'larını string eşleştirme ile tespit eder."""
        error = Exception("ORA-00060: deadlock detected")
        assert _is_deadlock_error(error) is True

    # --- Recursive Detection Testleri ---
    def test_detects_deadlock_via_orig_attribute(self):
        """SQLAlchemy wrapped exception'lardaki orig attribute ile deadlock tespit eder."""
        original_error = Mock()
        original_error.errno = 1213
        
        wrapped_error = Mock()
        wrapped_error.orig = original_error
        
        assert _is_deadlock_error(wrapped_error) is True

    def test_detects_deadlock_via_args(self):
        """Exception args içindeki error code'ları ile deadlock tespit eder."""
        error = Exception("Some error", "1213")
        assert _is_deadlock_error(error) is True

    # --- Negative Test Cases ---
    def test_returns_false_for_non_deadlock_error(self):
        """Deadlock olmayan hatalar için False döndürür."""
        error = Exception("Connection refused")
        assert _is_deadlock_error(error) is False

    def test_returns_false_for_regular_exception(self):
        """Normal exception'lar için False döndürür."""
        error = ValueError("Invalid value")
        assert _is_deadlock_error(error) is False

    def test_handles_missing_attributes_gracefully(self):
        """Eksik attribute'lara sahip exception'ları hatasız işler."""
        error = Exception("Some error")
        # Should not raise exception
        result = _is_deadlock_error(error)
        assert isinstance(result, bool)


@pytest.mark.unit
@pytest.mark.database
@pytest.mark.engine
class TestWithRetry:
    """with_retry decorator için testler."""

    # --- Başarılı İşlem Testleri ---
    def test_with_retry_returns_result_on_success(self):
        """Başarılı işlemde sonucu direkt döndürür."""
        @with_retry(max_attempts=3)
        def successful_operation():
            return "success"
        
        result = successful_operation()
        assert result == "success"

    def test_with_retry_does_not_retry_on_success(self):
        """Başarılı işlemde yeniden deneme yapmaz."""
        call_count = 0
        
        @with_retry(max_attempts=3)
        def successful_operation():
            nonlocal call_count
            call_count += 1
            return "success"
        
        successful_operation()
        assert call_count == 1

    # --- Deadlock Retry Testleri ---
    def test_with_retry_retries_on_deadlock_error(self):
        """Deadlock hatasında yeniden deneme yapar."""
        call_count = 0
        
        @with_retry(max_attempts=3, delay=0.01)
        def operation_with_deadlock():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                error = OperationalError("Deadlock detected", None, None)
                error.errno = 1213
                raise error
            return "success"
        
        result = operation_with_deadlock()
        assert result == "success"
        assert call_count == 2

    def test_with_retry_respects_max_attempts(self):
        """Maksimum deneme sayısına uyar."""
        call_count = 0
        
        @with_retry(max_attempts=2, delay=0.01)
        def always_failing_operation():
            nonlocal call_count
            call_count += 1
            error = OperationalError("Deadlock detected", None, None)
            error.errno = 1213
            raise error
        
        with pytest.raises(OperationalError):
            always_failing_operation()
        
        assert call_count == 2

    # --- Exponential Backoff Testleri ---
    def test_with_retry_uses_exponential_backoff(self):
        """Exponential backoff stratejisi kullanır."""
        wait_times = []
        
        @with_retry(max_attempts=3, delay=0.1, backoff=2.0)
        def operation_with_delays():
            if len(wait_times) < 2:
                wait_times.append(time.time())
                error = OperationalError("Deadlock detected", None, None)
                error.errno = 1213
                raise error
            return "success"
        
        start_time = time.time()
        operation_with_delays()
        
        # İlk deneme: 0.1 saniye bekleme
        # İkinci deneme: 0.2 saniye bekleme
        # Toplam bekleme süresi yaklaşık 0.3 saniye olmalı
        elapsed = time.time() - start_time
        assert elapsed >= 0.2  # En az 0.2 saniye geçmeli

    # --- Retry On Deadlock Only Testleri ---
    def test_with_retry_only_retries_deadlock_when_flag_is_true(self):
        """retry_on_deadlock_only=True olduğunda sadece deadlock hatalarında retry yapar."""
        call_count = 0
        
        @with_retry(max_attempts=3, retry_on_deadlock_only=True, delay=0.01)
        def operation_with_non_deadlock_error():
            nonlocal call_count
            call_count += 1
            raise OperationalError("Connection refused", None, None)
        
        with pytest.raises(OperationalError):
            operation_with_non_deadlock_error()
        
        assert call_count == 1  # Retry yapılmamalı

    def test_with_retry_retries_all_errors_when_flag_is_false(self):
        """retry_on_deadlock_only=False olduğunda tüm hatalarda retry yapar."""
        call_count = 0
        
        @with_retry(max_attempts=3, retry_on_deadlock_only=False, delay=0.01)
        def operation_with_non_deadlock_error():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise OperationalError("Connection refused", None, None)
            return "success"
        
        result = operation_with_non_deadlock_error()
        assert result == "success"
        assert call_count == 2

    # --- Exception Type Testleri ---
    def test_with_retry_only_retries_specified_exceptions(self):
        """Sadece belirtilen exception tiplerinde retry yapar."""
        call_count = 0
        
        @with_retry(max_attempts=3, retry_exceptions=(ValueError,), delay=0.01)
        def operation_with_different_error():
            nonlocal call_count
            call_count += 1
            raise OperationalError("Error", None, None)
        
        with pytest.raises(OperationalError):
            operation_with_different_error()
        
        assert call_count == 1  # Retry yapılmamalı

    def test_with_retry_raises_non_retry_exceptions_immediately(self):
        """Retry exception listesinde olmayan hataları direkt fırlatır."""
        call_count = 0
        
        @with_retry(max_attempts=3, retry_exceptions=(OperationalError,), delay=0.01)
        def operation_with_value_error():
            nonlocal call_count
            call_count += 1
            raise ValueError("Invalid value")
        
        with pytest.raises(ValueError):
            operation_with_value_error()
        
        assert call_count == 1  # Retry yapılmamalı

