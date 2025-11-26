# Credential Routes - Test Kılavuzu

## 📋 Genel Bilgiler

- **Base URL:** `{{base_url}}`
- **Prefix:** `/workspaces/{workspace_id}/credentials`
- **Authentication:** Tüm endpoint'ler Bearer token gerektirir
- **Content-Type:** `application/json`
- **Workspace ID Format:** `WSP-[16 haneli hexadecimal]`

---

## 1. Get All Credentials

### 📌 Endpoint Bilgileri

- **Method:** `GET`
- **Route:** `{{base_url}}/workspaces/{{workspace_id}}/credentials`
- **Description:** Workspace'teki tüm credential'ları pagination ve filtreleme ile getirir

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

---

### 🌐 Route

```
GET {{base_url}}/workspaces/{{workspace_id}}/credentials
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
| `credential_type` | string | ❌ No | - | Credential tipine göre filtrele (API_KEY, OAUTH2, BASIC_AUTH, JWT, AWS_CREDENTIALS, GCP_SERVICE_ACCOUNT, SSH_KEY, BEARER_TOKEN, CUSTOM) |
| `page` | integer | ❌ No | 1 | Sayfa numarası (min: 1) |
| `page_size` | integer | ❌ No | 100 | Sayfa başına kayıt sayısı (1-1000) |
| `order_by` | string | ❌ No | created_at | Sıralama alanı |
| `order_desc` | boolean | ❌ No | true | Azalan sıralama (default: true) |
| `include_deleted` | boolean | ❌ No | false | Silinen credential'ları dahil et |

---

### 📨 Request Body

Bu endpoint request body kullanmaz.

---

### ✅ Success Response (200 OK)

```json
{
  "status": "success",
  "code": 200,
  "message": "Credentials retrieved successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "items": [
      {
        "id": "CRD-1234567890ABCDEF",
        "name": "GitHub API Key",
        "credential_type": "API_KEY",
        "credential_provider": "GITHUB",
        "description": "GitHub personal access token",
        "tags": ["github", "api"],
        "api_key": "ghp_decrypted_key_value",
        "is_active": true,
        "expires_at": "2025-01-01T00:00:00Z",
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

**Not:** Credential data (api_key) otomatik olarak decrypt edilir ve düz metin olarak döner.

---

## 2. Get Credential

### 📌 Endpoint Bilgileri

- **Method:** `GET`
- **Route:** `{{base_url}}/workspaces/{{workspace_id}}/credentials/{{credential_id}}`
- **Description:** Belirli bir credential'ın detay bilgilerini getirir

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

---

### 🌐 Route

```
GET {{base_url}}/workspaces/{{workspace_id}}/credentials/{{credential_id}}
```

---

### 📝 Path Variables

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `workspace_id` | string | ✅ Yes | Workspace ID'si |
| `credential_id` | string | ✅ Yes | Credential ID'si |

---

### 📨 Request Body

Bu endpoint request body kullanmaz.

---

### ✅ Success Response (200 OK)

```json
{
  "status": "success",
  "code": 200,
  "message": "Credential retrieved successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "id": "CRD-1234567890ABCDEF",
    "name": "GitHub API Key",
    "credential_type": "API_KEY",
    "credential_provider": "GITHUB",
    "description": "GitHub personal access token",
    "tags": ["github", "api"],
    "api_key": "ghp_decrypted_key_value",
    "is_active": true,
    "expires_at": "2025-01-01T00:00:00Z",
    "workspace_id": "WSP-1234567890ABCDEF",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "created_by": "USR-1234567890ABCDEF",
    "updated_by": null
  }
}
```

**Not:** Credential data otomatik olarak decrypt edilir.

---

## 3. Create API Key Credential

### 📌 Endpoint Bilgileri

- **Method:** `POST`
- **Route:** `{{base_url}}/workspaces/{{workspace_id}}/credentials`
- **Description:** Workspace için yeni API key credential oluşturur

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

---

### 🌐 Route

```
POST {{base_url}}/workspaces/{{workspace_id}}/credentials
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
  "name": "GitHub API Key",
  "api_key": "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "credential_provider": "GITHUB",
  "description": "GitHub personal access token for repository access",
  "tags": ["github", "api", "repository"],
  "expires_at": "2025-01-01T00:00:00Z",
  "is_active": true
}
```

**Body Parametreleri:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | ✅ Yes | Credential adı (workspace içinde benzersiz olmalı) |
| `api_key` | string | ✅ Yes | API key değeri |
| `credential_provider` | string | ✅ Yes | Credential provider: GOOGLE, MICROSOFT, GITHUB |
| `description` | string | ❌ No | Credential açıklaması |
| `tags` | array | ❌ No | Etiketler |
| `expires_at` | datetime | ❌ No | Son kullanma tarihi (ISO 8601 format) |
| `is_active` | boolean | ❌ No | Aktif/pasif durumu (default: true) |

**Credential Provider Değerleri:**
- `GOOGLE` - Google API credentials
- `MICROSOFT` - Microsoft API credentials
- `GITHUB` - GitHub API credentials

---

### ✅ Success Response (201 Created)

```json
{
  "status": "success",
  "code": 201,
  "message": "Credential created successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "id": "CRD-1234567890ABCDEF",
    "name": "GitHub API Key",
    "credential_type": "API_KEY",
    "credential_provider": "GITHUB",
    "description": "GitHub personal access token for repository access",
    "tags": ["github", "api", "repository"],
    "api_key": "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "is_active": true,
    "expires_at": "2025-01-01T00:00:00Z",
    "workspace_id": "WSP-1234567890ABCDEF",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "created_by": "USR-1234567890ABCDEF",
    "updated_by": null
  }
}
```

**Not:** API key otomatik olarak encrypt edilir ve veritabanında şifreli olarak saklanır.

---

### ❌ Error Responses

#### 409 Conflict (Duplicate Name)

```json
{
  "status": "error",
  "code": 409,
  "message": null,
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "error_message": "Credential with this name already exists in workspace",
  "error_code": "RESOURCE_ALREADY_EXISTS"
}
```

---

## 4. Delete Credential

### 📌 Endpoint Bilgileri

- **Method:** `DELETE`
- **Route:** `{{base_url}}/workspaces/{{workspace_id}}/credentials/{{credential_id}}`
- **Description:** Credential'ı siler

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

**⚠️ UYARI:** Bu işlem geri alınamaz! Credential kalıcı olarak silinir.

---

### 🌐 Route

```
DELETE {{base_url}}/workspaces/{{workspace_id}}/credentials/{{credential_id}}
```

---

### 📝 Path Variables

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `workspace_id` | string | ✅ Yes | Workspace ID'si |
| `credential_id` | string | ✅ Yes | Credential ID'si |

---

### 📨 Request Body

Bu endpoint request body kullanmaz.

---

### ✅ Success Response (200 OK)

```json
{
  "status": "success",
  "code": 200,
  "message": "Credential deleted successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "credential_id": "CRD-1234567890ABCDEF",
    "deleted_at": "2024-01-01T00:00:00Z"
  }
}
```

---

## 🧪 Test Senaryoları

### Senaryo 1: API Key Credential Oluşturma

1. **GitHub API key credential oluştur:**
   ```
   POST {{base_url}}/workspaces/{{workspace_id}}/credentials
   Headers: Authorization: Bearer {{access_token}}
   Body: {
     "name": "GitHub API Key",
     "api_key": "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
     "credential_provider": "GITHUB",
     "description": "GitHub personal access token",
     "tags": ["github", "api"],
     "is_active": true
   }
   ```

2. **Credential'ı kontrol et:**
   ```
   GET {{base_url}}/workspaces/{{workspace_id}}/credentials/{{credential_id}}
   Headers: Authorization: Bearer {{access_token}}
   ```
   - API key decrypt edilmiş olarak dönmeli

---

### Senaryo 2: Credential Filtreleme

1. **Sadece API_KEY tipindeki credential'ları getir:**
   ```
   GET {{base_url}}/workspaces/{{workspace_id}}/credentials?credential_type=API_KEY
   Headers: Authorization: Bearer {{access_token}}
   ```

2. **Sadece GitHub provider'ı olan credential'ları getir:**
   ```
   GET {{base_url}}/workspaces/{{workspace_id}}/credentials
   ```
   - Response'da `credential_provider: "GITHUB"` olanları filtrele

---

### Senaryo 3: Credential Yönetimi

1. **Tüm credential'ları listele:**
   ```
   GET {{base_url}}/workspaces/{{workspace_id}}/credentials
   Headers: Authorization: Bearer {{access_token}}
   ```

2. **Belirli credential'ı sil:**
   ```
   DELETE {{base_url}}/workspaces/{{workspace_id}}/credentials/{{credential_id}}
   Headers: Authorization: Bearer {{access_token}}
   ```

---

## 📝 Postman/Bruno Collection Örneği

### Environment Variables

```json
{
  "base_url": "http://localhost:8000",
  "access_token": "",
  "workspace_id": "",
  "credential_id": ""
}
```

---

## 🔗 İlgili Endpoint'ler

- **GET /workspaces/{{workspace_id}}** - Workspace bilgilerini almak için
- **POST /workspaces/{{workspace_id}}/workflows/{{workflow_id}}/nodes** - Node oluştururken credential kullanmak için

---

## 📌 Notlar

1. **Credential Encryption:**
   - Tüm credential'lar otomatik olarak encrypt edilir
   - Veritabanında şifreli olarak saklanır
   - API response'larında otomatik olarak decrypt edilir ve düz metin olarak döner

2. **Credential Types:**
   - **API_KEY:** API key credentials (şu an desteklenen)
   - **OAUTH2:** OAuth2 credentials (gelecekte)
   - **BASIC_AUTH:** Basic authentication credentials (gelecekte)
   - **JWT:** JWT token credentials (gelecekte)
   - **AWS_CREDENTIALS:** AWS credentials (gelecekte)
   - **GCP_SERVICE_ACCOUNT:** GCP service account (gelecekte)
   - **SSH_KEY:** SSH key credentials (gelecekte)
   - **BEARER_TOKEN:** Bearer token credentials (gelecekte)
   - **CUSTOM:** Custom credentials (gelecekte)

3. **Credential Providers:**
   - **GOOGLE:** Google API credentials
   - **MICROSOFT:** Microsoft API credentials
   - **GITHUB:** GitHub API credentials

4. **Credential Name:**
   - Workspace içinde benzersiz olmalıdır
   - Aynı workspace'te aynı isimde iki credential olamaz

5. **Credential Expiration:**
   - `expires_at` field'ı opsiyoneldir
   - ISO 8601 formatında tarih belirtilir
   - Expire olan credential'lar kullanılamaz (kontrol edilir)

6. **Credential Active Status:**
   - `is_active: false` olan credential'lar kullanılamaz
   - Pasif credential'lar listede görünür ama workflow execution'da kullanılamaz

7. **Credential Usage:**
   - Credential'lar workflow node'larında kullanılabilir
   - Node execution sırasında credential değerleri inject edilir
   - Credential'lar script'lerde environment variable olarak kullanılabilir

8. **Security:**
   - Credential'lar asla log'larda görünmez
   - Sadece workspace üyeleri credential'ları görebilir
   - Credential'lar workspace bazlı izole edilir

---

**Son Güncelleme:** 2024  
**Versiyon:** 1.0

