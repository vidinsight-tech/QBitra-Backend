# Database Routes - Test Kılavuzu

## 📋 Genel Bilgiler

- **Base URL:** `{{base_url}}`
- **Prefix:** `/workspaces/{workspace_id}/databases`
- **Authentication:** Tüm endpoint'ler Bearer token gerektirir
- **Content-Type:** `application/json`
- **Workspace ID Format:** `WSP-[16 haneli hexadecimal]`

---

## 1. Get All Databases

### 📌 Endpoint Bilgileri

- **Method:** `GET`
- **Route:** `{{base_url}}/workspaces/{{workspace_id}}/databases`
- **Description:** Workspace'teki tüm database connection'ları pagination ile getirir

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

---

### 🌐 Route

```
GET {{base_url}}/workspaces/{{workspace_id}}/databases
```

---

### 📝 Path Variables

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `workspace_id` | string | ✅ Yes | Workspace ID'si (WSP- formatında) |

---

### 📝 Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `page` | integer | ❌ No | 1 | Sayfa numarası (min: 1) |
| `page_size` | integer | ❌ No | 100 | Sayfa başına kayıt sayısı (1-1000) |
| `order_by` | string | ❌ No | created_at | Sıralama alanı |
| `order_desc` | boolean | ❌ No | false | Azalan sıralama |
| `include_deleted` | boolean | ❌ No | false | Silinen database'leri dahil et |

---

### 📨 Request Body

Bu endpoint request body kullanmaz.

---

### ✅ Success Response (200 OK)

```json
{
  "status": "success",
  "code": 200,
  "message": "Databases retrieved successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "items": [
      {
        "id": "DB-1234567890ABCDEF",
        "name": "Production PostgreSQL",
        "database_type": "POSTGRESQL",
        "host": "db.example.com",
        "port": 5432,
        "database_name": "mydb",
        "username": "admin",
        "password": "decrypted_password",
        "connection_string": null,
        "ssl_enabled": true,
        "additional_params": {
          "pool_size": 10
        },
        "description": "Production database connection",
        "tags": ["production", "postgresql"],
        "is_active": true,
        "workspace_id": "WSP-1234567890ABCDEF",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "created_by": "USR-1234567890ABCDEF",
        "updated_by": null
      }
    ],
    "pagination": {
      "page": 1,
      "page_size": 100,
      "total": 1,
      "total_pages": 1
    }
  }
}
```

**Not:** Password otomatik olarak decrypt edilir ve düz metin olarak döner.

---

## 2. Get Database

### 📌 Endpoint Bilgileri

- **Method:** `GET`
- **Route:** `{{base_url}}/workspaces/{{workspace_id}}/databases/{{database_id}}`
- **Description:** Belirli bir database connection'ın detay bilgilerini getirir

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

---

### 🌐 Route

```
GET {{base_url}}/workspaces/{{workspace_id}}/databases/{{database_id}}
```

---

### 📝 Path Variables

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `workspace_id` | string | ✅ Yes | Workspace ID'si |
| `database_id` | string | ✅ Yes | Database ID'si |

---

### 📨 Request Body

Bu endpoint request body kullanmaz.

---

### ✅ Success Response (200 OK)

```json
{
  "status": "success",
  "code": 200,
  "message": "Database retrieved successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "id": "DB-1234567890ABCDEF",
    "name": "Production PostgreSQL",
    "database_type": "POSTGRESQL",
    "host": "db.example.com",
    "port": 5432,
    "database_name": "mydb",
    "username": "admin",
    "password": "decrypted_password",
    "connection_string": null,
    "ssl_enabled": true,
    "additional_params": {
      "pool_size": 10
    },
    "description": "Production database connection",
    "tags": ["production", "postgresql"],
    "is_active": true,
    "workspace_id": "WSP-1234567890ABCDEF",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "created_by": "USR-1234567890ABCDEF",
    "updated_by": null
  }
}
```

---

## 3. Create Database Connection

### 📌 Endpoint Bilgileri

- **Method:** `POST`
- **Route:** `{{base_url}}/workspaces/{{workspace_id}}/databases`
- **Description:** Workspace için yeni database connection oluşturur

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

---

### 🌐 Route

```
POST {{base_url}}/workspaces/{{workspace_id}}/databases
```

---

### 📝 Path Variables

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `workspace_id` | string | ✅ Yes | Workspace ID'si |

---

### 📨 Request Body

**Host/Port/Username/Password ile:**
```json
{
  "name": "Production PostgreSQL",
  "database_type": "POSTGRESQL",
  "host": "db.example.com",
  "port": 5432,
  "database_name": "mydb",
  "username": "admin",
  "password": "secret_password",
  "ssl_enabled": true,
  "additional_params": {
    "pool_size": 10
  },
  "description": "Production database connection",
  "tags": ["production", "postgresql"],
  "is_active": true
}
```

**Connection String ile:**
```json
{
  "name": "Production PostgreSQL",
  "database_type": "POSTGRESQL",
  "connection_string": "postgresql://admin:secret_password@db.example.com:5432/mydb?sslmode=require",
  "ssl_enabled": true,
  "description": "Production database connection",
  "tags": ["production", "postgresql"],
  "is_active": true
}
```

**Body Parametreleri:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | ✅ Yes | Database connection adı (workspace içinde benzersiz olmalı) |
| `database_type` | string | ✅ Yes | Database tipi (aşağıdaki listeden) |
| `host` | string | ❌ No* | Database host (connection_string yoksa gerekli) |
| `port` | integer | ❌ No | Database port |
| `database_name` | string | ❌ No | Database adı |
| `username` | string | ❌ No | Database kullanıcı adı |
| `password` | string | ❌ No | Database şifresi (encrypt edilir) |
| `connection_string` | string | ❌ No* | Tam connection string (host yoksa gerekli) |
| `ssl_enabled` | boolean | ❌ No | SSL aktif mi? (default: false) |
| `additional_params` | object | ❌ No | Ek connection parametreleri |
| `description` | string | ❌ No | Database açıklaması |
| `tags` | array | ❌ No | Etiketler |
| `is_active` | boolean | ❌ No | Aktif/pasif durumu (default: true) |

**Not:** `host` veya `connection_string`'den en az biri sağlanmalıdır.

**Database Type Değerleri:**
- `POSTGRESQL` - PostgreSQL
- `MYSQL` - MySQL
- `MONGODB` - MongoDB
- `REDIS` - Redis
- `MSSQL` - Microsoft SQL Server
- `ORACLE` - Oracle Database
- `SQLITE` - SQLite
- `CASSANDRA` - Apache Cassandra
- `ELASTICSEARCH` - Elasticsearch
- `DYNAMODB` - Amazon DynamoDB
- `BIGQUERY` - Google BigQuery
- `SNOWFLAKE` - Snowflake
- `REDSHIFT` - Amazon Redshift

---

### ✅ Success Response (201 Created)

```json
{
  "status": "success",
  "code": 201,
  "message": "Database connection created successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "id": "DB-1234567890ABCDEF",
    "name": "Production PostgreSQL",
    "database_type": "POSTGRESQL",
    "host": "db.example.com",
    "port": 5432,
    "database_name": "mydb",
    "username": "admin",
    "password": "secret_password",
    "connection_string": null,
    "ssl_enabled": true,
    "additional_params": {
      "pool_size": 10
    },
    "description": "Production database connection",
    "tags": ["production", "postgresql"],
    "is_active": true,
    "workspace_id": "WSP-1234567890ABCDEF",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "created_by": "USR-1234567890ABCDEF",
    "updated_by": null
  }
}
```

**Not:** Password otomatik olarak encrypt edilir ve veritabanında şifreli olarak saklanır.

---

## 4. Update Database Connection

### 📌 Endpoint Bilgileri

- **Method:** `PUT`
- **Route:** `{{base_url}}/workspaces/{{workspace_id}}/databases/{{database_id}}`
- **Description:** Mevcut database connection'ı günceller

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

---

### 🌐 Route

```
PUT {{base_url}}/workspaces/{{workspace_id}}/databases/{{database_id}}
```

---

### 📝 Path Variables

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `workspace_id` | string | ✅ Yes | Workspace ID'si |
| `database_id` | string | ✅ Yes | Database ID'si |

---

### 📨 Request Body

```json
{
  "name": "Updated Database Name",
  "host": "new-db.example.com",
  "port": 5433,
  "password": "new_password",
  "ssl_enabled": false,
  "description": "Updated description",
  "tags": ["updated", "database"]
}
```

**Body Parametreleri (Tümü Opsiyonel):**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | ❌ No | Database connection adı (workspace içinde benzersiz olmalı) |
| `host` | string | ❌ No | Database host |
| `port` | integer | ❌ No | Database port |
| `database_name` | string | ❌ No | Database adı |
| `username` | string | ❌ No | Database kullanıcı adı |
| `password` | string | ❌ No | Database şifresi (encrypt edilir) |
| `connection_string` | string | ❌ No | Tam connection string |
| `ssl_enabled` | boolean | ❌ No | SSL aktif mi? |
| `additional_params` | object | ❌ No | Ek connection parametreleri |
| `description` | string | ❌ No | Database açıklaması |
| `tags` | array | ❌ No | Etiketler |
| `is_active` | boolean | ❌ No | Aktif/pasif durumu |

---

### ✅ Success Response (200 OK)

```json
{
  "status": "success",
  "code": 200,
  "message": "Database connection updated successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "id": "DB-1234567890ABCDEF",
    "name": "Updated Database Name",
    "host": "new-db.example.com",
    "port": 5433,
    "password": "new_password",
    "ssl_enabled": false,
    "description": "Updated description",
    "tags": ["updated", "database"],
    "updated_at": "2024-01-01T00:00:00Z",
    "updated_by": "USR-1234567890ABCDEF"
  }
}
```

---

## 5. Delete Database Connection

### 📌 Endpoint Bilgileri

- **Method:** `DELETE`
- **Route:** `{{base_url}}/workspaces/{{workspace_id}}/databases/{{database_id}}`
- **Description:** Database connection'ı siler

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

**⚠️ UYARI:** Bu işlem geri alınamaz! Database connection kalıcı olarak silinir.

---

### 🌐 Route

```
DELETE {{base_url}}/workspaces/{{workspace_id}}/databases/{{database_id}}
```

---

### 📝 Path Variables

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `workspace_id` | string | ✅ Yes | Workspace ID'si |
| `database_id` | string | ✅ Yes | Database ID'si |

---

### 📨 Request Body

Bu endpoint request body kullanmaz.

---

### ✅ Success Response (200 OK)

```json
{
  "status": "success",
  "code": 200,
  "message": "Database connection deleted successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "database_id": "DB-1234567890ABCDEF",
    "deleted_at": "2024-01-01T00:00:00Z"
  }
}
```

---

## 🧪 Test Senaryoları

### Senaryo 1: PostgreSQL Connection Oluşturma

1. **PostgreSQL connection oluştur:**
   ```
   POST {{base_url}}/workspaces/{{workspace_id}}/databases
   Headers: Authorization: Bearer {{access_token}}
   Body: {
     "name": "Production PostgreSQL",
     "database_type": "POSTGRESQL",
     "host": "db.example.com",
     "port": 5432,
     "database_name": "mydb",
     "username": "admin",
     "password": "secret_password",
     "ssl_enabled": true,
     "description": "Production database",
     "tags": ["production", "postgresql"]
   }
   ```

2. **Connection'ı kontrol et:**
   ```
   GET {{base_url}}/workspaces/{{workspace_id}}/databases/{{database_id}}
   ```
   - Password decrypt edilmiş olarak dönmeli

---

### Senaryo 2: Connection String ile Oluşturma

1. **Connection string ile oluştur:**
   ```
   POST {{base_url}}/workspaces/{{workspace_id}}/databases
   Body: {
     "name": "MySQL Connection",
     "database_type": "MYSQL",
     "connection_string": "mysql://user:password@host:3306/database",
     "ssl_enabled": false
   }
   ```

---

### Senaryo 3: Database Connection Güncelleme

1. **Password güncelle:**
   ```
   PUT {{base_url}}/workspaces/{{workspace_id}}/databases/{{database_id}}
   Body: {
     "password": "new_password"
   }
   ```

2. **Host ve port güncelle:**
   ```
   PUT {{base_url}}/workspaces/{{workspace_id}}/databases/{{database_id}}
   Body: {
     "host": "new-host.example.com",
     "port": 5433
   }
   ```

---

## 📝 Postman/Bruno Collection Örneği

### Environment Variables

```json
{
  "base_url": "http://localhost:8000",
  "access_token": "",
  "workspace_id": "",
  "database_id": ""
}
```

---

## 🔗 İlgili Endpoint'ler

- **GET /workspaces/{{workspace_id}}** - Workspace bilgilerini almak için
- **POST /workspaces/{{workspace_id}}/workflows/{{workflow_id}}/nodes** - Node oluştururken database connection kullanmak için

---

## 📌 Notlar

1. **Password Encryption:**
   - Tüm password'ler otomatik olarak encrypt edilir
   - Veritabanında şifreli olarak saklanır
   - API response'larında otomatik olarak decrypt edilir ve düz metin olarak döner

2. **Connection Methods:**
   - **Host/Port/Username/Password:** Ayrı ayrı parametreler ile
   - **Connection String:** Tam connection string ile
   - İkisinden biri sağlanmalıdır

3. **Database Types:**
   - 14 farklı database tipi desteklenir
   - Her tip için uygun connection parametreleri kullanılmalıdır

4. **Database Name:**
   - Workspace içinde benzersiz olmalıdır
   - Aynı workspace'te aynı isimde iki connection olamaz

5. **SSL Support:**
   - `ssl_enabled: true` ile SSL bağlantısı aktif edilir
   - Database tipine göre SSL parametreleri ayarlanır

6. **Additional Params:**
   - Database tipine özel ek parametreler için kullanılır
   - Örnek: connection pool size, timeout değerleri, vb.

7. **Active Status:**
   - `is_active: false` olan connection'lar kullanılamaz
   - Pasif connection'lar listede görünür ama workflow execution'da kullanılamaz

8. **Database Usage:**
   - Database connection'lar workflow node'larında kullanılabilir
   - Node execution sırasında connection bilgileri kullanılır
   - Script'ler database connection'ları kullanarak query çalıştırabilir

9. **Security:**
   - Password'ler asla log'larda görünmez
   - Sadece workspace üyeleri database connection'ları görebilir
   - Connection'lar workspace bazlı izole edilir

---

**Son Güncelleme:** 2024  
**Versiyon:** 1.0

