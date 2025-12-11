import pytest
from miniflow.database.config.database_type import DatabaseType


@pytest.mark.unit
@pytest.mark.config
@pytest.mark.database
class TestDatabaseType:
    """DatabaseType enum için testler."""

    # --- Enum Değer Testleri ---
    def test_enum_values_match_expected_strings(self):
        """Enum değerlerinin beklenen string temsilleriyle eşleştiğini test eder."""
        assert DatabaseType.SQLITE.value == "sqlite"
        assert DatabaseType.MYSQL.value == "mysql"
        assert DatabaseType.POSTGRESQL.value == "postgresql"

    # --- Metod Testleri ---
    def test_default_port_returns_correct_port_for_each_database_type(self):
        """default_port metodunun her veritabanı türü için doğru port numarası döndürdüğünü test eder."""
        assert DatabaseType.SQLITE.default_port() == 0
        assert DatabaseType.MYSQL.default_port() == 3306
        assert DatabaseType.POSTGRESQL.default_port() == 5432

    def test_requires_credentials_returns_true_for_mysql_and_postgresql_false_for_sqlite(self):
        """requires_credentials metodunun MySQL/PostgreSQL için True, SQLite için False döndürdüğünü test eder."""
        assert DatabaseType.SQLITE.requires_credentials() is False
        assert DatabaseType.MYSQL.requires_credentials() is True
        assert DatabaseType.POSTGRESQL.requires_credentials() is True

    def test_supports_jsonb_returns_true_only_for_postgresql(self):
        """supports_jsonb metodunun sadece PostgreSQL için True döndürdüğünü test eder."""
        assert DatabaseType.SQLITE.supports_jsonb() is False
        assert DatabaseType.MYSQL.supports_jsonb() is False
        assert DatabaseType.POSTGRESQL.supports_jsonb() is True

    def test_supports_native_enum_returns_true_for_mysql_and_postgresql(self):
        """supports_native_enum metodunun MySQL ve PostgreSQL için True, SQLite için False döndürdüğünü test eder."""
        assert DatabaseType.SQLITE.supports_native_enum() is False
        assert DatabaseType.MYSQL.supports_native_enum() is True
        assert DatabaseType.POSTGRESQL.supports_native_enum() is True

    # --- Özellik Testleri ---
    def test_display_name_returns_human_readable_name(self):
        """display_name özelliğinin okunabilir veritabanı adı döndürdüğünü test eder."""
        assert DatabaseType.SQLITE.display_name == "SQLite"
        assert DatabaseType.MYSQL.display_name == "MySQL"
        assert DatabaseType.POSTGRESQL.display_name == "PostgreSQL"

    def test_driver_name_returns_sqlalchemy_driver_string(self):
        """driver_name özelliğinin SQLAlchemy uyumlu driver string döndürdüğünü test eder."""
        assert DatabaseType.SQLITE.driver_name == "sqlite"
        assert DatabaseType.POSTGRESQL.driver_name == "postgresql"
        assert DatabaseType.MYSQL.driver_name == "mysql+pymysql"

