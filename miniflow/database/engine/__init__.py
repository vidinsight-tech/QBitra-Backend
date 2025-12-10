"""
Veritabanı Motoru Modülü - Üretim ortamına hazır veritabanı motoru ve oturum yönetimi.

Bu modül şunları sağlar:
    - DatabaseEngine: Bağlantı havuzu ile çalışan temel veritabanı motoru
    - DatabaseManager: Uygulama genelinde motor yönetimi için singleton deseni
    - Decorator'lar: Oturum ve transaction yönetimi için decorator'lar
    - Yardımcı Fonksiyonlar: Deadlock tespiti ve yeniden deneme mekanizmaları
"""

from miniflow.database.engine.engine import DatabaseEngine, _is_deadlock_error, with_retry
from miniflow.database.engine.manager import DatabaseManager, get_database_manager
from miniflow.database.engine.decorators import (
    with_session,
    with_transaction_session,
    with_readonly_session,
    with_retry_session,
    inject_session,
)

__all__ = [
    # Temel sınıflar
    'DatabaseEngine',
    'DatabaseManager',
    
    # Manager fonksiyonları
    'get_database_manager',
    
    # Decorator'lar
    'with_session',
    'with_transaction_session',
    'with_readonly_session',
    'with_retry_session',
    'inject_session',
    
    # Yardımcı fonksiyonlar
    'with_retry',
    '_is_deadlock_error',  # İç kullanım için yardımcı fonksiyon, ama yararlı olabilir
]

