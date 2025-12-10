"""
Database Migration Modülü

Bu modül, Alembic tabanlı veritabanı migration işlemleri için yardımcı fonksiyonlar sağlar.
"""

from miniflow.database.migrations.utils import init_alembic, init_alembic_auto
from miniflow.database.migrations.commands import (
    run_migrations,
    create_migration,
    get_current_revision,
    get_head_revision,
    upgrade_dry_run,
    upgrade_safe,
)

# MigrationManager'ı export et
try:
    from miniflow.database.migrations.manager import MigrationManager
except ImportError:
    MigrationManager = None

__all__ = [
    # Alembic başlatma
    'init_alembic',
    'init_alembic_auto',
    
    # Migration komutları
    'run_migrations',
    'create_migration',
    'get_current_revision',
    'get_head_revision',
    'upgrade_dry_run',
    'upgrade_safe',
    
    # MigrationManager
    'MigrationManager',
]

