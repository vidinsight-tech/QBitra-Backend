# API Key Routes - Test Kılavuzu

## 📋 Genel Bilgiler

- **Base URL:** `{{base_url}}`
- **Prefix:** `/workspaces/{workspace_id}/api-keys`
- **Authentication:** Tüm endpoint'ler Bearer token gerektirir
- **Content-Type:** `application/json`
- **Workspace ID Format:** `WSP-[16 haneli hexadecimal]`

---

## 1. Get All API Keys

### 📌 Endpoint Bilgileri

- **Method:** `GET`
- **Route:** `{{base_url}}/workspaces/{{workspace_id}}/api-keys`
- **Description:** Workspace'teki tüm API key'leri pagination ile getirir (masked)

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

---

### 🌐 Route

```
GET {{base_url}}/workspaces/{{workspace_id}}/api-keys
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
| `include_deleted` | boolean | ❌ No | false | Silinen API key'leri dahil et |

---

### 📨 Request Body

Bu endpoint request body kullanmaz.

---

### ✅ Success Response (200 OK)

```json
{
  "status": "success",
  "code": 200,
  "message": "API keys retrieved successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "items": [
      {
        "id": "AKY-1234567890ABCDEF",
        "name": "Production API Key",
        "key_prefix": "sk_live_",
        "masked_key": "sk_live_****1234",
        "description": "API key for production environment",
        "is_active": true,
        "expires_at": null,
        "tags": ["production"],
        "allowed_ips": null,
        "workspace_id": "WSP-1234567890ABCDEF",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "created_by": "USR-1234567890ABCDEF"
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

**Not:** API key'ler güvenlik nedeniyle masked (maskelenmiş) olarak döner. Sadece prefix ve son birkaç karakter gösterilir.

---

## 2. Get API Key

### 📌 Endpoint Bilgileri

- **Method:** `GET`
- **Route:** `{{base_url}}/workspaces/{{workspace_id}}/api-keys/{{api_key_id}}`
- **Description:** Belirli bir API key'in detay bilgilerini getirir (masked)

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

---

### 🌐 Route

```
GET {{base_url}}/workspaces/{{workspace_id}}/api-keys/{{api_key_id}}
```

---

### 📝 Path Variables

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `workspace_id` | string | ✅ Yes | Workspace ID'si |
| `api_key_id` | string | ✅ Yes | API Key ID'si |

---

### 📨 Request Body

Bu endpoint request body kullanmaz.

---

### ✅ Success Response (200 OK)

```json
{
  "status": "success",
  "code": 200,
  "message": "API key retrieved successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "id": "AKY-1234567890ABCDEF",
    "name": "Production API Key",
    "key_prefix": "sk_live_",
    "masked_key": "sk_live_****1234",
    "description": "API key for production environment",
    "is_active": true,
    "expires_at": null,
    "tags": ["production"],
    "allowed_ips": null,
    "permissions": {
      "workflows": {
        "execute": true,
        "read": true,
        "write": false,
        "delete": false
      }
    },
    "workspace_id": "WSP-1234567890ABCDEF",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "created_by": "USR-1234567890ABCDEF"
  }
}
```

---

## 3. Create API Key

### 📌 Endpoint Bilgileri

- **Method:** `POST`
- **Route:** `{{base_url}}/workspaces/{{workspace_id}}/api-keys`
- **Description:** Yeni API key oluşturur

**⚠️ ÖNEMLİ:** API key sadece oluşturulduğunda bir kez gösterilir. Güvenli bir yerde saklayın!

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

---

### 🌐 Route

```
POST {{base_url}}/workspaces/{{workspace_id}}/api-keys
```

---

### 📝 Path Variables

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `workspace_id` | string | ✅ Yes | Workspace ID'si |

---

### 📨 Request Body

```json
{
  "name": "Production API Key",
  "key_prefix": "sk_live_",
  "description": "API key for production environment",
  "permissions": {
    "workflows": {
      "execute": true,
      "read": true,
      "write": false,
      "delete": false
    }
  },
  "expires_at": "2025-12-31T23:59:59Z",
  "tags": ["production"],
  "allowed_ips": ["192.168.1.1", "10.0.0.1"]
}
```

**Body Parametreleri:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | ✅ Yes | API key adı |
| `key_prefix` | string | ❌ No | API key prefix (default: "sk_live_") |
| `description` | string | ❌ No | Açıklama |
| `permissions` | object | ❌ No | Özel izinler (default permissions kullanılır) |
| `expires_at` | datetime | ❌ No | Son kullanma tarihi (ISO 8601 format) |
| `tags` | array | ❌ No | Etiketler |
| `allowed_ips` | array | ❌ No | İzin verilen IP adresleri (null ise tüm IP'ler) |

---

### ✅ Success Response (201 Created)

```json
{
  "status": "success",
  "code": 201,
  "message": "API key created successfully. Store it securely - it won't be shown again!",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "id": "AKY-1234567890ABCDEF",
    "name": "Production API Key",
    "full_api_key": "sk_live_1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
    "key_prefix": "sk_live_",
    "description": "API key for production environment",
    "is_active": true,
    "expires_at": "2025-12-31T23:59:59Z",
    "tags": ["production"],
    "allowed_ips": ["192.168.1.1", "10.0.0.1"],
    "permissions": {
      "workflows": {
        "execute": true,
        "read": true,
        "write": false,
        "delete": false
      }
    },
    "workspace_id": "WSP-1234567890ABCDEF",
    "created_at": "2024-01-01T00:00:00Z",
    "created_by": "USR-1234567890ABCDEF"
  }
}
```

**⚠️ ÖNEMLİ:** `full_api_key` değeri sadece bu response'da gösterilir. Sonraki isteklerde masked olarak döner. Bu değeri güvenli bir yerde saklayın!

**API Key Kullanımı:**
```
Header: X-API-KEY: sk_live_1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef
```

---

## 4. Update API Key

### 📌 Endpoint Bilgileri

- **Method:** `PUT`
- **Route:** `{{base_url}}/workspaces/{{workspace_id}}/api-keys/{{api_key_id}}`
- **Description:** Mevcut API key'i günceller

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

---

### 🌐 Route

```
PUT {{base_url}}/workspaces/{{workspace_id}}/api-keys/{{api_key_id}}
```

---

### 📝 Path Variables

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `workspace_id` | string | ✅ Yes | Workspace ID'si |
| `api_key_id` | string | ✅ Yes | API Key ID'si |

---

### 📨 Request Body

```json
{
  "name": "Updated API Key Name",
  "description": "Updated description",
  "permissions": {
    "workflows": {
      "execute": true,
      "read": true,
      "write": true,
      "delete": false
    }
  },
  "tags": ["updated", "production"],
  "allowed_ips": ["192.168.1.1"],
  "is_active": true,
  "expires_at": "2026-12-31T23:59:59Z"
}
```

**Body Parametreleri (Tümü Opsiyonel):**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | ❌ No | API key adı |
| `description` | string | ❌ No | Açıklama |
| `permissions` | object | ❌ No | Özel izinler |
| `tags` | array | ❌ No | Etiketler |
| `allowed_ips` | array | ❌ No | İzin verilen IP adresleri |
| `is_active` | boolean | ❌ No | Aktif/pasif durumu |
| `expires_at` | datetime | ❌ No | Son kullanma tarihi |

---

### ✅ Success Response (200 OK)

```json
{
  "status": "success",
  "code": 200,
  "message": "API key updated successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "id": "AKY-1234567890ABCDEF",
    "name": "Updated API Key Name",
    "key_prefix": "sk_live_",
    "masked_key": "sk_live_****1234",
    "description": "Updated description",
    "is_active": true,
    "expires_at": "2026-12-31T23:59:59Z",
    "tags": ["updated", "production"],
    "allowed_ips": ["192.168.1.1"],
    "updated_at": "2024-01-01T00:00:00Z",
    "updated_by": "USR-1234567890ABCDEF"
  }
}
```

---

## 5. Delete API Key

### 📌 Endpoint Bilgileri

- **Method:** `DELETE`
- **Route:** `{{base_url}}/workspaces/{{workspace_id}}/api-keys/{{api_key_id}}`
- **Description:** API key'i siler

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

**⚠️ UYARI:** Bu işlem geri alınamaz! API key kalıcı olarak silinir.

---

### 🌐 Route

```
DELETE {{base_url}}/workspaces/{{workspace_id}}/api-keys/{{api_key_id}}
```

---

### 📝 Path Variables

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `workspace_id` | string | ✅ Yes | Workspace ID'si |
| `api_key_id` | string | ✅ Yes | API Key ID'si |

---

### 📨 Request Body

Bu endpoint request body kullanmaz.

---

### ✅ Success Response (200 OK)

```json
{
  "status": "success",
  "code": 200,
  "message": "API key deleted successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "api_key_id": "AKY-1234567890ABCDEF",
    "deleted_at": "2024-01-01T00:00:00Z"
  }
}
```

---

## 🧪 Test Senaryoları

### Senaryo 1: API Key Oluşturma ve Kullanımı

1. **API key oluştur:**
   ```
   POST {{base_url}}/workspaces/{{workspace_id}}/api-keys
   Headers: Authorization: Bearer {{access_token}}
   Body: { "name": "My API Key", ... }
   ```

2. **Full API key'i kaydet:**
   - Response'daki `full_api_key` değerini güvenli bir yerde saklayın
   - Bu değer bir daha gösterilmeyecek!

3. **API key ile istek yap:**
   ```
   GET {{base_url}}/workspaces/{{workspace_id}}/workflows
   Headers: X-API-KEY: {{full_api_key}}
   ```

---

### Senaryo 2: API Key Yönetimi

1. **API key listesini al:**
   ```
   GET {{base_url}}/workspaces/{{workspace_id}}/api-keys
   Headers: Authorization: Bearer {{access_token}}
   ```

2. **API key detaylarını al:**
   ```
   GET {{base_url}}/workspaces/{{workspace_id}}/api-keys/{{api_key_id}}
   Headers: Authorization: Bearer {{access_token}}
   ```

3. **API key'i güncelle:**
   ```
   PUT {{base_url}}/workspaces/{{workspace_id}}/api-keys/{{api_key_id}}
   Headers: Authorization: Bearer {{access_token}}
   Body: { "is_active": false, ... }
   ```

---

### Senaryo 3: API Key ile Authentication

1. **API key ile istek yap (JWT yerine):**
   ```
   GET {{base_url}}/workspaces/{{workspace_id}}/workflows
   Headers: X-API-KEY: sk_live_...
   ```

**Not:** API key ile authentication yapıldığında Bearer token gerekmez.

---

## 📝 Postman/Bruno Collection Örneği

### Environment Variables

```json
{
  "base_url": "http://localhost:8000",
  "access_token": "",
  "workspace_id": "",
  "api_key_id": "",
  "full_api_key": ""
}
```

### Pre-request Script (API Key ile istek için)

```javascript
// API key varsa Authorization header'ını kaldır
if (pm.environment.get("full_api_key")) {
    pm.request.headers.remove("Authorization");
}
```

---

## 🔗 İlgili Endpoint'ler

- **GET /workspaces/{{workspace_id}}/limits** - Workspace API key limitlerini kontrol etmek için
- **POST /workspaces/{{workspace_id}}/workflows** - API key ile workflow oluşturmak için

---

## 📌 Notlar

1. **API Key Güvenliği:**
   - API key sadece oluşturulduğunda bir kez gösterilir
   - Sonraki isteklerde masked olarak döner
   - API key'i güvenli bir yerde saklayın (environment variable, secret manager, vb.)

2. **API Key Prefix:**
   - Default: `sk_live_`
   - Özel prefix belirtilebilir

3. **API Key Permissions:**
   - Default permissions: workflows (execute, read), credentials (read), databases (read), variables (read), files (read)
   - Özel permissions belirtilebilir

4. **IP Restriction:**
   - `allowed_ips` null ise tüm IP'lerden erişim sağlanır
   - Belirtilirse sadece belirtilen IP'lerden erişim sağlanır

5. **API Key Expiration:**
   - `expires_at` null ise süresiz geçerlidir
   - Belirtilirse belirtilen tarihten sonra geçersiz olur

6. **Rate Limiting:**
   - API key'ler workspace plan'ına göre rate limit'e tabidir
   - Plan bazlı limitler `/workspace-plans/api-limits` endpoint'inden alınabilir

7. **API Key vs JWT Token:**
   - API key: `X-API-KEY` header'ı ile kullanılır
   - JWT Token: `Authorization: Bearer <token>` header'ı ile kullanılır
   - İkisi de aynı anda kullanılabilir (API key önceliklidir)

---

**Son Güncelleme:** 2024  
**Versiyon:** 1.0

