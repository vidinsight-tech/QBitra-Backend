"""
Gerçek Senaryo: Blog Uygulaması

Bu script, database modülünün tüm özelliklerini gerçek bir senaryoda test eder:
1. Database yapılandırması ve başlatma
2. Migration oluşturma ve çalıştırma
3. Model kullanımı (mixin'lerle)
4. Session yönetimi ile CRUD işlemleri
5. Relationship'ler
6. Serialization
7. Soft delete
8. Audit tracking
"""

import sys
from pathlib import Path

# Proje root'unu path'e ekle
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from miniflow.database.models import Base
from example_models import User, Post, Comment # Bu dizinde oluşturuldu
from miniflow.database.engine import DatabaseManager
from miniflow.database.config import  get_sqlite_config
from miniflow.database.models.serialization import model_to_dict, models_to_list, model_to_json
from miniflow.database.engine.decorators import with_session, with_transaction_session, with_readonly_session


def setup_database():
    print("=" * 60)
    print("1. DATABASE YAPILANDIRMASI VE BAŞLATMA")
    print("=" * 60)

    # SQLite in-memory database kullan
    config = get_sqlite_config(database_name="blog_app")

    # DatabaseManager'ı başlat
    manager = DatabaseManager()
    manager.initialize(
        config=config,
        create_tables=Base.metadata  # Tabloları otomatik oluştur
    )

    print(f"Database başlatıldı: {config.db_type.value}")
    print(f"Database adı: {config.db_name}")
    print(f"Tablolar oluşturuldu\n")

    return DatabaseManager.get_instance()

def test_crud_operations():
    print("=" * 60)
    print("2. CRUD İŞLEMLERİ (Session Yönetimi ile)")
    print("=" * 60)

    manager = DatabaseManager.get_instance()
    engine = manager.engine

    # Önce mevcut verileri temizle 
    with engine.get_session() as session:
        session.query(Comment).delete()
        session.query(Post).delete()
        session.query(User).delete()
        session.commit()

    # CREATE - Kullanıcı oluştur
    with engine.get_session() as session:
        user1 = User(
            username="john_doe",
            email="john@example.com",
            full_name="John Doe",
            created_by="system",
            updated_by="system"
        )
        session.add(user1)
        session.commit()
        print(f"Kullanıcı oluşturuldu: {user1.username} (ID: {user1.id})")
        print(f"\t-created_at: {user1.created_at}")
        print(f"\t-created_by: {user1.created_by}")

    # READ - Kullanıcı oku
    with engine.get_session() as session:
        user = session.query(User).filter(User.username == "john_doe").first()
        print(f"Kullanıcı okundu: {user.username} (Email: {user.email})")
    
    # UPDATE - Kullanıcı güncelle
    with engine.get_session() as session:
        user = session.query(User).filter(User.username == "john_doe").first()
        user.full_name = "John Doe Updated"
        user.updated_by = "admin"
        session.commit()
        print(f"Kullanıcı güncellendi: {user.full_name}")
        print(f"\t- updated_at: {user.updated_at}")
        print(f"\t- updated_by: {user.updated_by}")
    
    # CREATE - Post oluştur
    with engine.get_session() as session:
        user = session.query(User).filter(User.username == "john_doe").first()
        post = Post(
            title="İlk Blog Yazısı",
            content="Bu bir test yazısıdır.",
            author_id=user.id,
            created_by="john_doe",
            updated_by="john_doe"
        )
        session.add(post)
        session.commit()
        print(f"Post oluşturuldu: {post.title} (ID: {post.id})")
    
    # CREATE - Comment oluştur
    with engine.get_session() as session:
        user = session.query(User).filter(User.username == "john_doe").first()
        post = session.query(Post).filter(Post.title == "İlk Blog Yazısı").first()
        comment = Comment(
            content="Harika bir yazı!",
            author_id=user.id,
            post_id=post.id
        )
        session.add(comment)
        session.commit()
        print(f"Yorum oluşturuldu: {comment.content[:30]}... (ID: {comment.id})")
    
    print()

def test_relationships():
    print("=" * 60)
    print("3. RELATIONSHIP'LER")
    print("=" * 60)

    manager = DatabaseManager.get_instance()
    engine = manager.engine
    
    with engine.get_session() as session:
        user = session.query(User).filter(User.username == "john_doe").first()
        
        # User'ın post'larını listele
        print(f"User '{user.username}' post sayısı: {len(user.posts)}")
        for post in user.posts:
            print(f"\t- Post: {post.title}")
        
        # Post'un yorumlarını listele
        if user.posts:
            post = user.posts[0]
            print(f"Post '{post.title}' yorum sayısı: {len(post.comments)}")
            for comment in post.comments:
                print(f"\t- Yorum: {comment.content[:30]}...")
    
    print()

def test_soft_delete():
    print("=" * 60)
    print("4. SOFT DELETE")
    print("=" * 60)
    
    manager = DatabaseManager.get_instance()
    engine = manager.engine
    
    with engine.get_session() as session:
        comment = session.query(Comment).first()
        comment_id = comment.id
        
        # Soft delete
        comment.soft_delete()
        session.commit()
        print(f"Yorum soft-delete edildi (ID: {comment_id})")
        print(f"\t- is_deleted: {comment.is_deleted}")
        print(f"\t- deleted_at: {comment.deleted_at}")
        
        # Soft delete edilmiş kayıtları sorgula
        deleted_comments = session.query(Comment).filter(Comment.is_deleted == True).all()
        print(f"Soft-delete edilmiş yorum sayısı: {len(deleted_comments)}")
        
        # Restore
        comment.restore()
        session.commit()
        print(f"Yorum geri yüklendi (ID: {comment_id})")
        print(f"\t- is_deleted: {comment.is_deleted}")
        print(f"\t- deleted_at: {comment.deleted_at}")
    
    print()

def test_serialization():
    print("=" * 60)
    print("5. SERIALIZATION")
    print("=" * 60)
    
    manager = DatabaseManager.get_instance()
    engine = manager.engine
    
    with engine.get_session() as session:
        user = session.query(User).filter(User.username == "john_doe").first()
        
        # model_to_dict
        user_dict = model_to_dict(user)
        print("model_to_dict:")
        print(f"\t- ID: {user_dict['id']}")
        print(f"\t- Username: {user_dict['username']}")
        print(f"\t- Email: {user_dict['email']}")
        print(f"\t- created_at: {user_dict['created_at']}")
        print(f"\t- created_by: {user_dict['created_by']}")
        
        # model_to_dict with relationships
        user_dict_with_posts = model_to_dict(
            user,
            include_relationships=True,
            max_depth=2
        )
        print(f"model_to_dict (relationships ile):")
        print(f"\t- Post sayısı: {len(user_dict_with_posts.get('posts', []))}")
        
        # models_to_list
        all_users = session.query(User).all()
        users_list = models_to_list(all_users)
        print(f"models_to_list: {len(users_list)} kullanıcı serialize edildi")
        
        # model_to_json
        user_json = model_to_json(user, indent=2)
        print(f"model_to_json (ilk 200 karakter):")
        print(f"\t{user_json[:200]}...")
    
    print()


def test_decorators():
    """Decorator'ları test et."""
    print("=" * 60)
    print("6. DECORATOR'LAR (Session Yönetimi)")
    print("=" * 60)
    
    @with_session()
    def create_user_with_decorator(session, username, email):
        """Decorator ile kullanıcı oluştur."""
        user = User(
            username=username,
            email=email,
            full_name=f"{username} Full Name",
            created_by="decorator",
            updated_by="decorator"
        )
        session.add(user)
        session.commit()
        # Session içinde attribute'ları al
        return {"id": user.id, "username": user.username}
    
    @with_transaction_session()
    def create_post_with_transaction(session, title, content, author_id):
        """Transaction decorator ile post oluştur."""
        post = Post(
            title=title,
            content=content,
            author_id=author_id,
            created_by="decorator",
            updated_by="decorator"
        )
        session.add(post)
        # commit otomatik yapılır
        # Session içinde attribute'ları al
        return {"id": post.id, "title": post.title}
    
    @with_readonly_session()
    def read_user_with_readonly(session, user_id):
        """Read-only session ile kullanıcı oku."""
        user = session.query(User).filter(User.id == user_id).first()
        if user:
            return {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "post_count": len(user.posts) if user.posts else 0
            }
        return None
    
    @with_readonly_session()
    def list_all_users_readonly(session):
        """Read-only session ile tüm kullanıcıları listele."""
        users = session.query(User).filter(User.is_deleted == False).all()
        return [
            {
                "id": user.id,
                "username": user.username,
                "email": user.email
            }
            for user in users
        ]
    
    # Decorator ile kullanıcı oluştur
    user2_data = create_user_with_decorator("jane_doe", "jane@example.com")
    print(f"@with_session decorator ile kullanıcı oluşturuldu: {user2_data['username']} (ID: {user2_data['id']})")
    
    # Transaction decorator ile post oluştur
    post2_data = create_post_with_transaction(
        "Decorator ile Oluşturulan Post",
        "Bu post transaction decorator ile oluşturuldu.",
        user2_data['id']
    )
    print(f"@with_transaction_session decorator ile post oluşturuldu: {post2_data['title']} (ID: {post2_data['id']})")
    
    # Read-only session ile kullanıcı oku
    user_readonly = read_user_with_readonly(user2_data['id'])
    if user_readonly:
        print(f"@with_readonly_session decorator ile kullanıcı okundu: {user_readonly['username']} (Email: {user_readonly['email']}, Post sayısı: {user_readonly['post_count']})")
    
    # Read-only session ile tüm kullanıcıları listele
    all_users_readonly = list_all_users_readonly()
    print(f"@with_readonly_session decorator ile {len(all_users_readonly)} aktif kullanıcı listelendi")
    
    print()

def test_complex_scenario():
    """Karmaşık senaryo: Tüm özellikleri bir arada kullan."""
    print("=" * 60)
    print("7. KARMAŞIK SENARYO (Tüm Özellikler)")
    print("=" * 60)
    
    manager = DatabaseManager.get_instance()
    engine = manager.engine
    
    with engine.get_session() as session:
        # Birden fazla kullanıcı oluştur
        users_data = [
            ("alice", "alice@example.com", "Alice Smith"),
            ("bob", "bob@example.com", "Bob Johnson"),
            ("charlie", "charlie@example.com", "Charlie Brown"),
        ]
        
        created_users = []
        for username, email, full_name in users_data:
            user = User(
                username=username,
                email=email,
                full_name=full_name,
                created_by="system",
                updated_by="system"
            )
            session.add(user)
            created_users.append(user)
        
        session.commit()
        print(f"{len(created_users)} kullanıcı oluşturuldu")
        
        # Her kullanıcı için post oluştur
        for user in created_users:
            post = Post(
                title=f"{user.username}'in İlk Yazısı",
                content=f"Bu {user.full_name} tarafından yazılmış bir yazıdır.",
                author_id=user.id,
                created_by=user.username,
                updated_by=user.username
            )
            session.add(post)
        
        session.commit()
        print(f"Her kullanıcı için post oluşturuldu")
        
        # Tüm kullanıcıları serialize et
        all_users = session.query(User).all()
        user_dict = model_to_dict(
            all_users[0],  # İlk kullanıcıyı örnek olarak
            include_relationships=True,
            max_depth=2
        )
        users_json = model_to_json(
            all_users[0],  # İlk kullanıcıyı örnek olarak
            include_relationships=True,
            indent=2
        )
        print(f"Kullanıcı serialize edildi (JSON uzunluğu: {len(users_json)} karakter)")
        
        # Soft delete testi
        user_to_delete = created_users[0]
        user_to_delete.soft_delete()
        session.commit()
        print(f"Kullanıcı soft-delete edildi: {user_to_delete.username}")
        
        # Aktif kullanıcıları listele
        active_users = session.query(User).filter(User.is_deleted == False).all()
        print(f"Aktif kullanıcı sayısı: {len(active_users)}")
    
    print()


def cleanup():
    """Temizlik işlemleri."""
    print("=" * 60)
    print("8. TEMİZLİK")
    print("=" * 60)
    
    try:
        manager = DatabaseManager.get_instance()
        if manager.is_initialized:
            manager.stop()
            print("Database kapatıldı")
    except Exception as e:
        print(f"Temizlik hatası: {e}")
    
    print()


def main():
    """Ana fonksiyon."""
    print("\n" + "=" * 60)
    print("GERÇEK SENARYO: BLOG UYGULAMASI")
    print("Database Modülü - Tüm Özellikler Testi")
    print("=" * 60 + "\n")
    
    try:
        # 1. Database setup
        setup_database()
        print("\nSıradaki İşlem: CRUD Operasyonları")
        input("Devam etmek için bir enter yapın . . .")
        print()
        
        # 2. CRUD işlemleri
        test_crud_operations()
        print("\nSıradaki İşlem: Tablolar Arası İlişkiler")
        input("Devam etmek için bir enter yapın . . .")
        print()

        # 3. Relationship'ler
        test_relationships()
        print("\nSıradaki İşlem: Soft Delete Operasyonları")
        input("Devam etmek için bir enter yapın . . .")
        print()

        # 4. Soft delete
        test_soft_delete()
        print("\nSıradaki İşlem: Serilization Operasyonları")
        input("Devam etmek için bir enter yapın . . .")
        print()
        
        # 5. Serialization
        test_serialization()
        print("\nSıradaki İşlem: Dekoratör Operasyonları")
        input("Devam etmek için bir enter yapın . . .")
        print()

        # 6. Decorator'lar
        test_decorators()
        print("\nSıradaki İşlem: Kompleks Senrayo")
        input("Devam etmek için bir enter yapın . . .")
        print()
        
        # 7. Karmaşık senaryo
        test_complex_scenario()
        print("\nSıradaki İşlem: Veritabanının temizlenmesi")
        input("Devam etmek için bir enter yapın . . .")
        print()
        
        # 8. Temizlik
        cleanup()
        
        print("=" * 60)
        print("TÜM TESTLER BAŞARIYLA TAMAMLANDI!")
        print("=" * 60)
        return 0
        
    except Exception as e:
        print(f"\nHATA: {e}")
        import traceback
        traceback.print_exc()
        cleanup()
        return 1


if __name__ == "__main__":
    exit(main())