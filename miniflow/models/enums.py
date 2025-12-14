from enum import Enum


class TicketTypes(str, Enum):
    CRASH = "crash"
    BUG = "bug"
    FEEDBACK = "feedback"
    REQUEST = "request"

class TicketStatus(str, Enum):
    OPEN = "open"
    IN_REVIEW = "in_review"
    RESOLVED = "resolved"
    CLOSED = "closed"

class ExecutionStatuses(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"

class AuditActionTypes(str, Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    EXECUTE = "execute"
    CANCEL = "cancel"
    RETRY = "retry"
    UPLOAD = "upload"
    DOWNLOAD = "download"
    EXPORT = "export"
    IMPORT = "import"
    INVITE = "invite"
    JOIN = "join"
    LEAVE = "leave"
    REMOVE = "remove"
    CHANGE_ROLE = "change_role"
    TEST_CONNECTION = "test_connection"

class CrashSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class CrashStatus(str, Enum):
    NEW = "new"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    IGNORED = "ignored"
    DUPLICATE = "duplicate"

class AgreementType(str, Enum):
    TERMS_OF_SERVICE = "terms_of_service"
    PRIVACY_POLICY = "privacy_policy"
    COOKIE_POLICY = "cookie_policy"
    DATA_PROCESSING_AGREEMENT = "data_processing_agreement"
    USER_AGREEMENT = "user_agreement"
    CUSTOM = "custom"

class AgreementStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"
    DEPRECATED = "deprecated"

class LoginStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    LOCKED = "locked"
    SUSPENDED = "suspended"

class LoginMethod(str, Enum):
    PASSWORD = "password"
    GOOGLE = "google"
    OTHER = "other"

class TriggerTypes(str, Enum):
    API = "api"
    WEBHOOK = "webhook"
    SCHEDULED = "scheduled"

class ScriptApprovalStatus(str, Enum):
    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    CHANGES_REQUESTED = "changes_requested"
    RESUBMITTED = "resubmitted"

class ScriptTestStatus(str, Enum):
    UNTESTED = "untested"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"

class CredentialType(str, Enum):
    API_KEY = "api_key"
    OAUTH2 = "oauth2"
    BASIC_AUTH = "basic_auth"
    BEARER_TOKEN = "bearer_token"
    SSH_KEY = "ssh_key"
    AWS_CREDENTIALS = "aws_credentials"
    AZURE_CREDENTIALS = "azure_credentials"
    GCP_CREDENTIALS = "gcp_credentials"
    CUSTOM = "custom"

class VariableType(str, Enum):
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    JSON = "json"
    LIST = "list"
    DICT = "dict"

class DatabaseCategory(str, Enum):
    SQL = "sql"
    NOSQL = "nosql"
    VECTOR = "vector"
    SEARCH = "search"
    TIME_SERIES = "time_series"
    GRAPH = "graph"
    CUSTOM = "custom"

class InvitationStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

class DatabaseType(str, Enum):
    # SQL Databases
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MARIADB = "mariadb"
    SQLSERVER = "sqlserver"
    ORACLE = "oracle"
    # NoSQL Databases
    MONGODB = "mongodb"
    REDIS = "redis"
    CASSANDRA = "cassandra"
    DYNAMODB = "dynamodb"
    COUCHDB = "couchdb"
    # Search & Analytics
    ELASTICSEARCH = "elasticsearch"
    OPENSEARCH = "opensearch"
    # Vector Databases
    PINECONE = "pinecone"
    WEAVIATE = "weaviate"
    QDRANT = "qdrant"
    CHROMADB = "chromadb"
    MILVUS = "milvus"
    VECTARA = "vectara"
    PG_VECTOR = "pgvector"  # PostgreSQL extension
    # Time Series
    INFLUXDB = "influxdb"
    TIMESCALEDB = "timescaledb"
    # Graph Databases
    NEO4J = "neo4j"
    # Custom
    CUSTOM = "custom"

__all__ = [
    "TicketTypes",
    "TicketStatus",
    "ExecutionStatuses",
    "AuditActionTypes",
    "CrashSeverity",
    "CrashStatus",
    "AgreementType",
    "AgreementStatus",
    "LoginStatus",
    "LoginMethod",
    "TriggerTypes",
    "ScriptApprovalStatus",
    "ScriptTestStatus",
    "CredentialType",
    "VariableType",
    "DatabaseCategory",
    "DatabaseType",
    "InvitationStatus",
]