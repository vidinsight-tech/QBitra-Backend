from datetime import datetime, timezone
from typing import Dict, List, Tuple, Optional
from sqlalchemy import Column, String, Integer, Text, Boolean, DateTime, ForeignKey, JSON, Enum, UniqueConstraint, Index
from sqlalchemy.orm import relationship

from miniflow.database.models import Base
from miniflow.database.models.mixins import SoftDeleteMixin, TimestampMixin
from miniflow.models.enums import DatabaseType, DatabaseCategory


class Database(Base, SoftDeleteMixin, TimestampMixin):
    """Veritabanı bağlantıları - Workspace içinde kullanılan veritabanı bağlantılarını yönetir"""
    __prefix__ = "DBS"
    __tablename__ = 'databases'
    
    # ---- Table Args ---- #
    __table_args__ = (
        UniqueConstraint('workspace_id', 'name', name='uq_database_workspace_name'),
        Index('idx_databases_workspace_type_active', 'workspace_id', 'database_type', 'is_active'),
        Index('idx_databases_owner_active', 'owner_id', 'is_active'),
        Index('idx_databases_softdelete', 'is_deleted', 'created_at'),
    )

    # ---- Relationships ---- #
    workspace_id = Column(String(20), ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=False, index=True,
    comment="Hangi workspace'de")
    owner_id = Column(String(20), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True,
    comment="Veritabanı bağlantısını oluşturan kullanıcı")

    # ---- Basic Information ---- #
    name = Column(String(100), nullable=False, index=True,
    comment="Bağlantı adı (workspace içinde benzersiz)")
    db_category = Column(Enum(DatabaseCategory), nullable=False, index=True,
    comment="Veritabanı kategorisi (SQL, NOSQL, VECTOR, SEARCH, TIME_SERIES, GRAPH, CUSTOM)")
    database_type = Column(Enum(DatabaseType), nullable=False, index=True,
    comment="Veritabanı tipi (POSTGRESQL, MYSQL, MONGODB, REDIS, PINECONE, vb.)")
    description = Column(Text, nullable=True,
    comment="Bağlantı açıklaması")

    # ---- Connection Configuration - Flexible JSON structure for all DB types ---- #
    connection_config = Column(JSON, nullable=False, default=lambda: {},
    comment="Bağlantı yapılandırması (JSON - DB türüne göre özelleştirilebilir)")
    
    # ---- Connection String - Alternative to connection_config for all DB types ---- #
    connection_string = Column(Text, nullable=True,
    comment="Connection string (opsiyonel - connection_config yerine kullanılabilir)")

    # ---- Status ---- #
    is_active = Column(Boolean, default=True, nullable=False, index=True,
    comment="Bağlantı aktif mi?")
    last_tested_at = Column(DateTime(timezone=True), nullable=True,
    comment="Son test zamanı")
    last_test_status = Column(String(20), nullable=True,
    comment="Son test durumu (SUCCESS, FAILED)")

    # ---- Metadata ---- #
    tags = Column(JSON, default=lambda: [], nullable=True,
    comment="Etiketler (JSON array)")

    # ---- Relationships ---- #
    workspace = relationship("Workspace", back_populates="databases")
    owner = relationship("User", foreign_keys=[owner_id], back_populates="databases")
    
    # ---- Helper Methods ---- #
    @staticmethod
    def get_category_from_type(database_type: DatabaseType) -> DatabaseCategory:
        """Database type'dan otomatik olarak category belirler"""
        sql_types = {
            DatabaseType.POSTGRESQL, DatabaseType.MYSQL, DatabaseType.MARIADB,
            DatabaseType.SQLSERVER, DatabaseType.ORACLE
        }
        nosql_types = {
            DatabaseType.MONGODB, DatabaseType.REDIS, DatabaseType.CASSANDRA,
            DatabaseType.DYNAMODB, DatabaseType.COUCHDB
        }
        vector_types = {
            DatabaseType.PINECONE, DatabaseType.WEAVIATE, DatabaseType.QDRANT,
            DatabaseType.CHROMADB, DatabaseType.MILVUS, DatabaseType.VECTARA,
            DatabaseType.PG_VECTOR
        }
        search_types = {
            DatabaseType.ELASTICSEARCH, DatabaseType.OPENSEARCH
        }
        time_series_types = {
            DatabaseType.INFLUXDB, DatabaseType.TIMESCALEDB
        }
        graph_types = {
            DatabaseType.NEO4J
        }
        
        if database_type in sql_types:
            return DatabaseCategory.SQL
        elif database_type in nosql_types:
            return DatabaseCategory.NOSQL
        elif database_type in vector_types:
            return DatabaseCategory.VECTOR
        elif database_type in search_types:
            return DatabaseCategory.SEARCH
        elif database_type in time_series_types:
            return DatabaseCategory.TIME_SERIES
        elif database_type in graph_types:
            return DatabaseCategory.GRAPH
        else:
            return DatabaseCategory.CUSTOM
    
    # ---- Validation Methods (Kategorilere göre ortak fonksiyonlar) ---- #
    
    @staticmethod
    def _validate_sql(connection_config: Dict, database_type: DatabaseType) -> List[str]:
        """SQL veritabanları için ortak validation (PostgreSQL, MySQL, MariaDB, SQL Server, Oracle, PG_VECTOR, TimescaleDB)"""
        errors = []
        
        # Standart SQL veritabanları için host, database, port zorunlu
        required_fields = ["host", "database", "port"]
        for field in required_fields:
            if field not in connection_config or not connection_config.get(field):
                errors.append(f"{database_type.value} için '{field}' alanı zorunludur")
        
        return errors
    
    @staticmethod
    def _validate_nosql(connection_config: Dict, database_type: DatabaseType) -> List[str]:
        """NoSQL veritabanları için ortak validation (MongoDB, Redis, Cassandra, DynamoDB, CouchDB)"""
        errors = []
        
        # MongoDB özel durum - connection_string veya host+database
        if database_type == DatabaseType.MONGODB:
            if "connection_string" not in connection_config:
                required_fields = ["host", "database"]
                for field in required_fields:
                    if field not in connection_config or not connection_config[field]:
                        errors.append(f"MongoDB için '{field}' alanı zorunludur (connection_string yoksa)")
            return errors
        
        # Redis özel durum - sadece host zorunlu
        if database_type == DatabaseType.REDIS:
            if "host" not in connection_config or not connection_config.get("host"):
                errors.append("Redis için 'host' alanı zorunludur")
            return errors
        
        # Diğer NoSQL DB'ler - connection_string veya host
        if "connection_string" not in connection_config:
            if "host" not in connection_config or not connection_config.get("host"):
                errors.append(f"{database_type.value} için 'host' veya 'connection_string' alanı zorunludur")
        
        return errors
    
    @staticmethod
    def _validate_vector(connection_config: Dict, database_type: DatabaseType) -> List[str]:
        """Vector veritabanları için ortak validation (Pinecone, Weaviate, Qdrant, ChromaDB, Milvus, Vectara, PG_VECTOR)"""
        errors = []
        
        # Pinecone özel durum - api_key + api_url/environment
        if database_type == DatabaseType.PINECONE:
            if "api_key" not in connection_config or not connection_config.get("api_key"):
                errors.append("Pinecone için 'api_key' alanı zorunludur")
            if "api_url" not in connection_config and "environment" not in connection_config:
                errors.append("Pinecone için 'api_url' veya 'environment' alanı zorunludur")
            return errors
        
        # Weaviate özel durum - sadece api_url
        if database_type == DatabaseType.WEAVIATE:
            if "api_url" not in connection_config or not connection_config.get("api_url"):
                errors.append("Weaviate için 'api_url' alanı zorunludur")
            return errors
        
        # Qdrant özel durum - api_url veya host
        if database_type == DatabaseType.QDRANT:
            if "api_url" not in connection_config:
                if "host" not in connection_config or not connection_config.get("host"):
                    errors.append("Qdrant için 'api_url' veya 'host' alanı zorunludur")
            return errors
        
        # PG_VECTOR SQL kategorisinde, buraya gelmemeli ama yine de kontrol
        if database_type == DatabaseType.PG_VECTOR:
            required_fields = ["host", "database"]
            for field in required_fields:
                if field not in connection_config or not connection_config[field]:
                    errors.append(f"PG_VECTOR için '{field}' alanı zorunludur")
            return errors
        
        # Diğer vector DB'ler - host veya api_url
        if "host" not in connection_config and "api_url" not in connection_config:
            errors.append(f"{database_type.value} için 'host' veya 'api_url' alanı zorunludur")
        
        return errors
    
    @staticmethod
    def _validate_search(connection_config: Dict, database_type: DatabaseType) -> List[str]:
        """Search veritabanları için ortak validation (Elasticsearch, OpenSearch)"""
        errors = []
        if "host" not in connection_config or not connection_config.get("host"):
            errors.append(f"{database_type.value} için 'host' alanı zorunludur")
        return errors
    
    @staticmethod
    def _validate_time_series(connection_config: Dict, database_type: DatabaseType) -> List[str]:
        """Time Series veritabanları için ortak validation (InfluxDB, TimescaleDB)"""
        errors = []
        
        # TimescaleDB SQL kategorisinde, buraya gelmemeli ama yine de kontrol
        if database_type == DatabaseType.TIMESCALEDB:
            required_fields = ["host", "database"]
            for field in required_fields:
                if field not in connection_config or not connection_config[field]:
                    errors.append(f"TimescaleDB için '{field}' alanı zorunludur")
            return errors
        
        # InfluxDB - host ve database zorunlu
        required_fields = ["host", "database"]
        for field in required_fields:
            if field not in connection_config or not connection_config[field]:
                errors.append(f"{database_type.value} için '{field}' alanı zorunludur")
        
        return errors
    
    @staticmethod
    def _validate_graph(connection_config: Dict, database_type: DatabaseType) -> List[str]:
        """Graph veritabanları için ortak validation (Neo4j)"""
        errors = []
        if "host" not in connection_config or not connection_config.get("host"):
            errors.append(f"{database_type.value} için 'host' alanı zorunludur")
        return errors
    
    @staticmethod
    def _validate_custom(connection_config: Dict, database_type: DatabaseType) -> List[str]:
        """Custom database için validation (validation yok)"""
        return []
    
    @staticmethod
    def validate_connection_config(database_type: DatabaseType, connection_config: Dict, connection_string: Optional[str] = None) -> Tuple[bool, List[str]]:
        """
        Database type'a göre connection_config'i validate eder.
        Kategorilere göre ortak validation fonksiyonları çağrılır.
        
        Args:
            database_type: Database tipi
            connection_config: Connection yapılandırması (JSON dict)
            connection_string: Connection string (opsiyonel)
        
        Returns:
            Tuple[bool, List[str]]: (geçerli_mi, hata_listesi)
        """
        # Connection string varsa, config kontrolü yapmaya gerek yok
        if connection_string:
            return True, []
        
        if not connection_config:
            return False, ["connection_config boş olamaz"]
        
        # Kategoriye göre validation fonksiyonunu belirle
        category = Database.get_category_from_type(database_type)
        
        if category == DatabaseCategory.SQL:
            errors = Database._validate_sql(connection_config, database_type)
        elif category == DatabaseCategory.NOSQL:
            errors = Database._validate_nosql(connection_config, database_type)
        elif category == DatabaseCategory.VECTOR:
            errors = Database._validate_vector(connection_config, database_type)
        elif category == DatabaseCategory.SEARCH:
            errors = Database._validate_search(connection_config, database_type)
        elif category == DatabaseCategory.TIME_SERIES:
            errors = Database._validate_time_series(connection_config, database_type)
        elif category == DatabaseCategory.GRAPH:
            errors = Database._validate_graph(connection_config, database_type)
        elif category == DatabaseCategory.CUSTOM:
            errors = Database._validate_custom(connection_config, database_type)
        else:
            errors = [f"Bilinmeyen database kategorisi: {category}"]
        
        return len(errors) == 0, errors
    
    def validate(self) -> Tuple[bool, List[str]]:
        """
        Mevcut database instance'ını validate eder.
        
        Returns:
            Tuple[bool, List[str]]: (geçerli_mi, hata_listesi)
        """
        return self.validate_connection_config(
            self.database_type,
            self.connection_config or {},
            self.connection_string
        )
