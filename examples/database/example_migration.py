"""
Migration Senaryosu - Basit ve Açıklamalı Örnek

Bu script, migration sisteminin temel kullanımını adım adım gösterir.
Her satır Türkçe açıklamalarla anlatılmıştır.
"""

# Sistem modüllerini import et
import sys
from pathlib import Path

# Proje root dizinini Python path'ine ekle
# Bu sayede miniflow modüllerini import edebiliriz
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Database yapılandırma modülünden SQLite config fonksiyonunu import et
from miniflow.database.config import get_sqlite_config

# Database engine yönetimi için DatabaseManager'ı import et
from miniflow.database.engine import DatabaseManager

# Model base sınıfını import et (migration için gerekli)
from miniflow.database.models import Base

# Migration fonksiyonlarını import et
from miniflow.database.migrations import (
    init_alembic_auto,      # Alembic'i otomatik başlat
    create_migration,       # Yeni migration oluştur
    run_migrations,         # Migration'ları uygula
    get_current_revision,   # Mevcut revision'ı al
    get_head_revision,      # En son revision'ı al
)

# Örnek modelleri import et (User, Post, Comment)
# Bu modeller migration oluştururken kullanılacak
try:
    from examples.database.example_models import User, Post, Comment
except ImportError:
    # Eğer import başarısız olursa, dosyadan doğrudan yükle
    import importlib.util
    example_models_path = Path(__file__).parent / "example_models.py"
    if example_models_path.exists():
        spec = importlib.util.spec_from_file_location("example_models", example_models_path)
        example_models = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(example_models)
        User = example_models.User
        Post = example_models.Post
        Comment = example_models.Comment
    else:
        raise ImportError("example_models.py bulunamadı")


def setup_database():
    """
    Veritabanını yapılandır ve başlat.
    
    Bu fonksiyon:
    1. SQLite veritabanı konfigürasyonu oluşturur
    2. DatabaseManager'ı başlatır
    3. Veritabanı bağlantısını hazırlar
    """
    print("=" * 70)
    print("1. VERITABANI YAPILANDIRMASI")
    print("=" * 70)
    
    # SQLite veritabanı için konfigürasyon oluştur
    # database_name parametresi veritabanı dosya adını belirler
    config = get_sqlite_config(database_name="migration_example")
    
    # DatabaseManager singleton instance'ını al
    # Singleton pattern sayesinde her zaman aynı instance döner
    manager = DatabaseManager()
    
    # DatabaseManager'ı verilen konfigürasyon ile başlat
    # Bu işlem veritabanı bağlantısını hazırlar ama henüz tablo oluşturmaz
    manager.initialize(config=config)
    
    print(f"Veritabani baslatildi: {config.db_type.value}")
    print(f"Veritabani adi: {config.db_name}")
    print(f"DatabaseManager hazir\n")
    
    # Manager instance'ını döndür (diğer fonksiyonlarda kullanmak için)
    return manager


def initialize_alembic(manager):
    """
    Alembic migration sistemini başlat.
    
    Bu fonksiyon sadece bir kez çalıştırılmalıdır.
    Alembic dizin yapısını ve konfigürasyon dosyalarını oluşturur.
    """
    print("=" * 70)
    print("2. ALEMBIC BASLATMA")
    print("=" * 70)
    
    # Migration dosyalarının saklanacağı dizin
    # Bu dizin proje root'unda oluşturulacak
    alembic_dir = Path("./alembic_migrations")
    
    try:
        # Alembic'i otomatik konfigürasyon ile başlat
        # Bu fonksiyon:
        # - alembic_migrations dizinini oluşturur
        # - env.py dosyasını yapılandırır
        # - DatabaseEngine bağlantı bilgilerini otomatik ayarlar
        init_alembic_auto(
            engine=manager.engine,                    # DatabaseEngine instance'ı
            base_metadata=Base.metadata,              # Tüm modellerin metadata'sı
            script_location=str(alembic_dir),         # Migration dizini
            models_import_path="examples.database.example_models"  # Modellerin import path'i
        )
        
        print(f"Alembic dizini olusturuldu: {alembic_dir}")
        print(f"env.py otomatik yapilandirildi")
        print(f"Migration dosyalari icin hazir\n")
        
    except Exception as e:
        # Eğer Alembic zaten başlatılmışsa, bu normal bir durumdur
        if "zaten mevcut" in str(e).lower() or "already exists" in str(e).lower():
            print(f"Uyari: Alembic zaten baslatilmis: {alembic_dir}")
            print(f"   (Bu normal - devam edebilirsiniz)\n")
        else:
            # Diğer hatalar için exception'ı yukarı fırlat
            print(f"Hata: Alembic baslatma hatasi: {e}\n")
            raise


def create_first_migration(manager):
    """
    İlk migration dosyasını oluştur.
    
    Bu fonksiyon mevcut modellerden (User, Post, Comment) otomatik olarak
    migration dosyası oluşturur. Autogenerate=True olduğu için SQLAlchemy
    modellerindeki değişiklikleri algılar ve migration'a dönüştürür.
    
    Not: Yeni migration oluşturmadan önce veritabanının güncel olduğundan
    emin olunmalıdır. Eğer uygulanmamış migration varsa önce onlar uygulanmalıdır.
    """
    print("=" * 70)
    print("3. ILK MIGRATION OLUSTURMA")
    print("=" * 70)
    
    alembic_dir = Path("./alembic_migrations")
    
    # Önce veritabanı durumunu kontrol et
    try:
        current = get_current_revision(manager, script_location=str(alembic_dir))
        head = get_head_revision(manager, script_location=str(alembic_dir))
        
        # Eğer uygulanmamış migration varsa, önce onları uygula
        if current != head and head is not None:
            print(f"Uyari: Uygulanmamis migration'lar var")
            print(f"   Mevcut: {current or 'Yok'}")
            print(f"   Head: {head}")
            print(f"   Once mevcut migration'lar uygulaniyor...\n")
            
            # Mevcut migration'ları uygula
            run_migrations(
                engine_or_manager=manager,
                revision="head",
                script_location=str(alembic_dir)
            )
            print("Mevcut migration'lar uygulandi\n")
    except Exception as e:
        # Durum kontrolü başarısız olabilir (henüz migration yoksa)
        print(f"Durum kontrolu: {e}")
        print("Devam ediliyor...\n")
    
    try:
        # Yeni bir migration dosyası oluştur
        # message: Migration dosyasının açıklaması (dosya adında kullanılır)
        # autogenerate: True ise modellerden otomatik migration oluştur
        migration_path = create_migration(
            engine_or_manager=manager,                # DatabaseManager veya DatabaseEngine
            message="initial_schema",                 # Migration açıklaması
            autogenerate=True,                        # Otomatik migration oluştur
            script_location=str(alembic_dir)          # Migration dizini
        )
        
        print(f"Migration olusturuldu: {migration_path}")
        
        # Oluşturulan migration dosyasını kontrol et
        versions_dir = alembic_dir / "versions"
        if versions_dir.exists():
            # versions dizinindeki tüm .py dosyalarını bul
            migration_files = list(versions_dir.glob("*.py"))
            if migration_files:
                # En son oluşturulan dosyayı bul (modification time'a göre)
                latest = max(migration_files, key=lambda p: p.stat().st_mtime)
                print(f"Migration dosyasi: {latest.name}")
                print(f"   Konum: {latest}\n")
                
    except Exception as e:
        # Eğer migration zaten varsa veya değişiklik yoksa, bu normal olabilir
        error_msg = str(e).lower()
        if "already exists" in error_msg or "zaten mevcut" in error_msg:
            print(f"Uyari: Migration zaten mevcut (bu normal olabilir)")
            print(f"   Devam ediliyor...\n")
        elif "not up to date" in error_msg or "guncel degil" in error_msg:
            print(f"Uyari: Veritabani guncel degil")
            print(f"   Once mevcut migration'lar uygulanmali")
            print(f"   Bu islem otomatik olarak yapilacak...\n")
            # Tekrar migration uygula ve sonra dene
            try:
                run_migrations(manager, revision="head", script_location=str(alembic_dir))
                print("Migration'lar uygulandi, tekrar deneniyor...\n")
                # Tekrar migration oluşturmayı dene
                migration_path = create_migration(
                    engine_or_manager=manager,
                    message="initial_schema",
                    autogenerate=True,
                    script_location=str(alembic_dir)
                )
                print(f"Migration olusturuldu: {migration_path}\n")
            except Exception as e2:
                print(f"Hata: Migration olusturma hatasi: {e2}\n")
                # Bu durumda devam et, çünkü migration zaten olabilir
        elif "no changes" in error_msg or "degisiklik" in error_msg:
            print(f"Bilgi: Model degisikligi algilanmadi")
            print(f"   Yeni migration olusturulmadi (bu normal)\n")
        else:
            print(f"Uyari: Migration olusturma hatasi: {e}")
            print(f"   Devam ediliyor...\n")


def apply_migrations(manager):
    """
    Oluşturulan migration'ları veritabanına uygula.
    
    Bu fonksiyon migration dosyalarını okuyup veritabanı şemasını günceller.
    revision="head" parametresi en son migration'a kadar uygular.
    """
    print("=" * 70)
    print("4. MIGRATION'LARI UYGULAMA")
    print("=" * 70)
    
    alembic_dir = Path("./alembic_migrations")
    
    try:
        # Migration'ları uygula
        # revision="head" en son migration'a kadar uygular
        run_migrations(
            engine_or_manager=manager,                # DatabaseManager instance'ı
            revision="head",                          # Hedef revision (head = en son)
            script_location=str(alembic_dir)          # Migration dizini
        )
        
        print("Migration'lar basariyla uygulandi")
        print("Veritabani semasi guncellendi\n")
        
    except Exception as e:
        # Eğer migration'lar zaten uygulanmışsa, bu normaldir
        if "already at" in str(e).lower() or "zaten" in str(e).lower():
            print(f"Uyari: Migration'lar zaten uygulanmis (bu normal)")
            print(f"   Devam ediliyor...\n")
        else:
            print(f"Hata: Migration uygulama hatasi: {e}\n")
            raise


def check_migration_status(manager):
    """
    Migration durumunu kontrol et.
    
    Bu fonksiyon:
    - Veritabanındaki mevcut revision'ı gösterir
    - En son (head) revision'ı gösterir
    - İkisini karşılaştırarak durum analizi yapar
    """
    print("=" * 70)
    print("5. MIGRATION DURUMU KONTROLU")
    print("=" * 70)
    
    alembic_dir = Path("./alembic_migrations")
    
    try:
        # Veritabanındaki mevcut revision'ı al
        # Bu, veritabanına uygulanmış son migration'ın ID'sidir
        current = get_current_revision(
            engine_or_manager=manager,
            script_location=str(alembic_dir)
        )
        
        print(f"Mevcut veritabani revision: {current or 'Migration uygulanmamis'}")
        
        # Head (en son) revision'ı al
        # Bu, migration dosyalarındaki en son migration'ın ID'sidir
        head = get_head_revision(
            engine_or_manager=manager,
            script_location=str(alembic_dir)
        )
        
        print(f"Head (en son) revision: {head or 'Migration yok'}")
        
        # Durum analizi yap
        if current == head:
            # Mevcut ve head aynıysa, veritabanı günceldir
            print("Durum: Veritabani guncel - tum migration'lar uygulanmis")
        elif current is None:
            # Mevcut None ise, hiç migration uygulanmamıştır
            print("Durum: Veritabani migration uygulanmamis")
        else:
            # Mevcut ve head farklıysa, upgrade gerekir
            print(f"Durum: Veritabani guncel degil - {head} revision'ina upgrade gerekli")
        
        print()
        
    except Exception as e:
        print(f"Hata: Durum kontrolu hatasi: {e}\n")
        raise


def cleanup(manager):
    """
    Temizlik işlemleri.
    
    Bu fonksiyon:
    - Database bağlantısını kapatır
    - Test dosyalarını temizler (isteğe bağlı)
    """
    print("=" * 70)
    print("6. TEMIZLIK")
    print("=" * 70)
    
    try:
        # Eğer DatabaseManager başlatılmışsa, durdur
        if manager.is_initialized:
            manager.stop()
            print("Veritabani kapatildi")
        
        # Test veritabanı dosyasını sil (isteğe bağlı)
        import os
        db_file = Path("./migration_example")
        if db_file.exists():
            # SQLite dosyası varsa sil
            for ext in ['', '.db', '.sqlite', '.sqlite3']:
                db_path = Path(f"./migration_example{ext}")
                if db_path.exists():
                    db_path.unlink()
                    print(f"Test veritabani dosyasi silindi: {db_path}")
        
        print()
        
    except Exception as e:
        print(f"Uyari: Temizlik hatasi: {e}\n")


def main():
    """
    Ana fonksiyon - Tüm migration işlemlerini sırayla çalıştır.
    
    Bu fonksiyon migration sisteminin temel kullanımını gösterir:
    1. Veritabanı yapılandırması
    2. Alembic başlatma
    3. İlk migration oluşturma
    4. Migration'ları uygulama
    5. Durum kontrolü
    6. Temizlik
    """
    print("\n" + "=" * 70)
    print("MIGRATION SISTEMI - BASIT ORNEK")
    print("=" * 70 + "\n")
    
    # Manager değişkenini None olarak başlat (hata durumunda cleanup için)
    manager = None
    
    try:
        # 1. Veritabanını yapılandır ve başlat
        manager = setup_database()
        
        # 2. Alembic migration sistemini başlat
        # Not: Bu işlem sadece bir kez yapılmalıdır
        initialize_alembic(manager)
        
        # 3. Mevcut migration durumunu kontrol et
        # Eğer uygulanmamış migration varsa önce onları uygula
        check_migration_status(manager)
        
        # 4. İlk migration dosyasını oluştur
        # Bu işlem mevcut modellerden (User, Post, Comment) migration oluşturur
        # Not: create_first_migration içinde gerekirse önce mevcut migration'lar uygulanır
        create_first_migration(manager)
        
        # 5. Oluşturulan migration'ları veritabanına uygula
        # Bu işlem veritabanı şemasını günceller (tablolar oluşturulur)
        apply_migrations(manager)
        
        # 6. Migration durumunu tekrar kontrol et
        # Mevcut ve head revision'ları karşılaştır (güncel durumu görmek için)
        check_migration_status(manager)
        
        # 7. Temizlik işlemleri
        cleanup(manager)
        
        print("=" * 70)
        print("TUM MIGRATION ORNEKLERI BASARIYLA TAMAMLANDI!")
        print("=" * 70)
        print("\nOgrenilenler:")
        print("   - Alembic baslatma (init_alembic_auto)")
        print("   - Migration olusturma (create_migration)")
        print("   - Migration uygulama (run_migrations)")
        print("   - Durum kontrolu (get_current_revision, get_head_revision)")
        print()
        
        return 0
        
    except Exception as e:
        # Hata durumunda detaylı bilgi göster
        print(f"\nHATA: {e}")
        import traceback
        traceback.print_exc()
        
        # Hata olsa bile temizlik yap
        if manager:
            cleanup(manager)
        
        return 1


# Script doğrudan çalıştırıldığında main fonksiyonunu çağır
if __name__ == "__main__":
    exit(main())
