# Variable Routes - Test Kılavuzu

## 📋 Genel Bilgiler

- **Base URL:** `{{base_url}}`
- **Prefix:** `/workspaces/{workspace_id}/variables`
- **Authentication:** Tüm endpoint'ler Bearer token gerektirir
- **Content-Type:** `application/json`
- **Workspace ID Format:** `WSP-[16 haneli hexadecimal]`

---

## 1. Get All Variables

### 📌 Endpoint Bilgileri

- **Method:** `GET`
- **Route:** `{{base_url}}/workspaces/{{workspace_id}}/variables`
- **Description:** Workspace'teki tüm variable'ları pagination ile getirir

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

---

### 🌐 Route

```
GET {{base_url}}/workspaces/{{workspace_id}}/variables
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
| `include_deleted` | boolean | ❌ No | false | Silinen variable'ları dahil et |

---

### 📨 Request Body

Bu endpoint request body kullanmaz.

---

### ✅ Success Response (200 OK)

```json
{
  "status": "success",
  "code": 200,
  "message": "Variables retrieved successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "items": [
      {
        "id": "VAR-1234567890ABCDEF",
        "key": "API_URL",
        "value": "https://api.example.com",
        "description": "API base URL",
        "is_secret": false,
        "workspace_id": "WSP-1234567890ABCDEF",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "created_by": "USR-1234567890ABCDEF",
        "updated_by": null
      },
      {
        "id": "VAR-FEDCBA0987654321",
        "key": "SECRET_TOKEN",
        "value": "decrypted_secret_value",
        "description": "Secret token",
        "is_secret": true,
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
      "total": 2,
      "total_pages": 1
    }
  }
}
```

**Not:** Secret variable'lar otomatik olarak decrypt edilir ve düz metin olarak döner.

---

## 2. Get Variable

### 📌 Endpoint Bilgileri

- **Method:** `GET`
- **Route:** `{{base_url}}/workspaces/{{workspace_id}}/variables/{{variable_id}}`
- **Description:** Belirli bir variable'ın detay bilgilerini getirir

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

---

### 🌐 Route

```
GET {{base_url}}/workspaces/{{workspace_id}}/variables/{{variable_id}}
```

---

### 📝 Path Variables

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `workspace_id` | string | ✅ Yes | Workspace ID'si |
| `variable_id` | string | ✅ Yes | Variable ID'si |

---

### 📨 Request Body

Bu endpoint request body kullanmaz.

---

### ✅ Success Response (200 OK)

```json
{
  "status": "success",
  "code": 200,
  "message": "Variable retrieved successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "id": "VAR-1234567890ABCDEF",
    "key": "API_URL",
    "value": "https://api.example.com",
    "description": "API base URL",
    "is_secret": false,
    "workspace_id": "WSP-1234567890ABCDEF",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "created_by": "USR-1234567890ABCDEF",
    "updated_by": null
  }
}
```

---

## 3. Create Variable

### 📌 Endpoint Bilgileri

- **Method:** `POST`
- **Route:** `{{base_url}}/workspaces/{{workspace_id}}/variables`
- **Description:** Yeni variable oluşturur

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

---

### 🌐 Route

```
POST {{base_url}}/workspaces/{{workspace_id}}/variables
```

---

### 📝 Path Variables

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `workspace_id` | string | ✅ Yes | Workspace ID'si |

---

### 📨 Request Body

**Non-Secret Variable:**
```json
{
  "key": "API_URL",
  "value": "https://api.example.com",
  "description": "API base URL",
  "is_secret": false
}
```

**Secret Variable:**
```json
{
  "key": "SECRET_TOKEN",
  "value": "my_secret_value_123",
  "description": "Secret token for API",
  "is_secret": true
}
```

**Body Parametreleri:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `key` | string | ✅ Yes | Variable key (workspace içinde benzersiz olmalı) |
| `value` | string | ✅ Yes | Variable değeri |
| `description` | string | ❌ No | Açıklama |
| `is_secret` | boolean | ❌ No | Secret variable mı? (default: false) - True ise encrypt edilir |

---

### ✅ Success Response (201 Created)

```json
{
  "status": "success",
  "code": 201,
  "message": "Variable created successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "id": "VAR-1234567890ABCDEF",
    "key": "API_URL",
    "value": "https://api.example.com",
    "description": "API base URL",
    "is_secret": false,
    "workspace_id": "WSP-1234567890ABCDEF",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "created_by": "USR-1234567890ABCDEF",
    "updated_by": null
  }
}
```

**Not:** Secret variable'lar otomatik olarak encrypt edilir ve veritabanında şifreli olarak saklanır.

---

## 4. Update Variable

### 📌 Endpoint Bilgileri

- **Method:** `PUT`
- **Route:** `{{base_url}}/workspaces/{{workspace_id}}/variables/{{variable_id}}`
- **Description:** Mevcut variable'ı günceller

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

---

### 🌐 Route

```
PUT {{base_url}}/workspaces/{{workspace_id}}/variables/{{variable_id}}
```

---

### 📝 Path Variables

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `workspace_id` | string | ✅ Yes | Workspace ID'si |
| `variable_id` | string | ✅ Yes | Variable ID'si |

---

### 📨 Request Body

```json
{
  "key": "UPDATED_API_URL",
  "value": "https://api.updated.com",
  "description": "Updated API URL",
  "is_secret": false
}
```

**Body Parametreleri (Tümü Opsiyonel):**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `key` | string | ❌ No | Variable key (workspace içinde benzersiz olmalı) |
| `value` | string | ❌ No | Variable değeri |
| `description` | string | ❌ No | Açıklama |
| `is_secret` | boolean | ❌ No | Secret variable mı? |

**Not:** 
- `is_secret` false'tan true'ya değiştirilirse value encrypt edilir
- `is_secret` true'dan false'a değiştirilirse value decrypt edilir

---

### ✅ Success Response (200 OK)

```json
{
  "status": "success",
  "code": 200,
  "message": "Variable updated successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "id": "VAR-1234567890ABCDEF",
    "key": "UPDATED_API_URL",
    "value": "https://api.updated.com",
    "description": "Updated API URL",
    "is_secret": false,
    "updated_at": "2024-01-01T00:00:00Z",
    "updated_by": "USR-1234567890ABCDEF"
  }
}
```

---

## 5. Delete Variable

### 📌 Endpoint Bilgileri

- **Method:** `DELETE`
- **Route:** `{{base_url}}/workspaces/{{workspace_id}}/variables/{{variable_id}}`
- **Description:** Variable'ı siler

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

**⚠️ UYARI:** Bu işlem geri alınamaz! Variable kalıcı olarak silinir.

---

### 🌐 Route

```
DELETE {{base_url}}/workspaces/{{workspace_id}}/variables/{{variable_id}}
```

---

### 📝 Path Variables

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `workspace_id` | string | ✅ Yes | Workspace ID'si |
| `variable_id` | string | ✅ Yes | Variable ID'si |

---

### 📨 Request Body

Bu endpoint request body kullanmaz.

---

### ✅ Success Response (200 OK)

```json
{
  "status": "success",
  "code": 200,
  "message": "Variable deleted successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "variable_id": "VAR-1234567890ABCDEF",
    "deleted_at": "2024-01-01T00:00:00Z"
  }
}
```

---

## 🧪 Test Senaryoları

### Senaryo 1: Variable Oluşturma ve Yönetimi

1. **Non-secret variable oluştur:**
   ```
   POST {{base_url}}/workspaces/{{workspace_id}}/variables
   Headers: Authorization: Bearer {{access_token}}
   Body: { "key": "API_URL", "value": "https://api.example.com", "is_secret": false }
   ```

2. **Secret variable oluştur:**
   ```
   POST {{base_url}}/workspaces/{{workspace_id}}/variables
   Headers: Authorization: Bearer {{access_token}}
   Body: { "key": "SECRET_TOKEN", "value": "secret123", "is_secret": true }
   ```

3. **Variable listesini al:**
   ```
   GET {{base_url}}/workspaces/{{workspace_id}}/variables
   Headers: Authorization: Bearer {{access_token}}
   ```

4. **Variable'ı güncelle:**
   ```
   PUT {{base_url}}/workspaces/{{workspace_id}}/variables/{{variable_id}}
   Headers: Authorization: Bearer {{access_token}}
   Body: { "value": "https://api.updated.com" }
   ```

---

### Senaryo 2: Secret Variable Encryption/Decryption

1. **Secret variable oluştur:**
   ```
   POST {{base_url}}/workspaces/{{workspace_id}}/variables
   Body: { "key": "SECRET", "value": "my_secret", "is_secret": true }
   ```

2. **Secret variable'ı non-secret'e çevir:**
   ```
   PUT {{base_url}}/workspaces/{{workspace_id}}/variables/{{variable_id}}
   Body: { "is_secret": false }
   ```
   - Value otomatik olarak decrypt edilir

3. **Non-secret variable'ı secret'a çevir:**
   ```
   PUT {{base_url}}/workspaces/{{workspace_id}}/variables/{{variable_id}}
   Body: { "is_secret": true }
   ```
   - Value otomatik olarak encrypt edilir

---

## 📝 Postman/Bruno Collection Örneği

### Environment Variables

```json
{
  "base_url": "http://localhost:8000",
  "access_token": "",
  "workspace_id": "",
  "variable_id": ""
}
```

---

## 🔗 İlgili Endpoint'ler

- **GET /workspaces/{{workspace_id}}** - Workspace bilgilerini almak için
- **POST /workspaces/{{workspace_id}}/workflows/{{workflow_id}}/nodes** - Node oluştururken variable kullanmak için

---

## 📌 Notlar

1. **Variable Key:** Workspace içinde benzersiz olmalıdır.
2. **Secret Variables:**
   - `is_secret: true` olan variable'lar otomatik olarak encrypt edilir
   - Veritabanında şifreli olarak saklanır
   - API response'larında otomatik olarak decrypt edilir ve düz metin olarak döner
3. **Encryption/Decryption:**
   - Secret'tan non-secret'e geçiş: Otomatik decrypt
   - Non-secret'ten secret'a geçiş: Otomatik encrypt
4. **Variable Kullanımı:**
   - Workflow execution sırasında variable değerleri kullanılabilir
   - Node input parametrelerinde variable referansları kullanılabilir
5. **Pagination:** Default olarak sayfa başına 100 kayıt döner, maksimum 1000.

---

**Son Güncelleme:** 2024  
**Versiyon:** 1.0

