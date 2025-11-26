# Workspace Routes - Test Kılavuzu

## 📋 Genel Bilgiler

- **Base URL:** `{{base_url}}`
- **Prefix:** `/workspaces`
- **Authentication:** Tüm endpoint'ler Bearer token gerektirir
- **Content-Type:** `application/json`
- **Workspace ID Format:** `WSP-[16 haneli hexadecimal]` (örn: `WSP-1234567890ABCDEF`)

---

## 1. Create Workspace

### 📌 Endpoint Bilgileri

- **Method:** `POST`
- **Route:** `{{base_url}}/workspaces`
- **Description:** Yeni workspace oluşturur (kullanıcı owner olur)

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

---

### 🌐 Route

```
POST {{base_url}}/workspaces
```

---

### 📝 Path Variables

Bu endpoint path variable kullanmaz.

---

### 📨 Request Body

```json
{
  "name": "My Workspace",
  "slug": "my-workspace",
  "description": "My first workspace description"
}
```

**Body Parametreleri:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | ✅ Yes | Workspace adı (1-100 karakter) |
| `slug` | string | ✅ Yes | Workspace slug (URL-friendly, 1-100 karakter) |
| `description` | string | ❌ No | Workspace açıklaması (max 500 karakter) |

**Not:** Workspace otomatik olarak Freemium planı ile oluşturulur.

---

### ✅ Success Response (201 Created)

```json
{
  "status": "success",
  "code": 201,
  "message": "Workspace created successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "id": "WSP-1234567890ABCDEF",
    "name": "My Workspace",
    "slug": "my-workspace",
    "description": "My first workspace description",
    "owner_id": "USR-1234567890ABCDEF",
    "plan_id": "PLN-1234567890ABCDEF",
    "plan_name": "Freemium",
    "is_suspended": false,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

---

### ❌ Error Responses

#### 400 Bad Request (Validation Error)

```json
{
  "status": "error",
  "code": 400,
  "message": null,
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "error_message": "Workspace name cannot be empty",
  "error_code": "INVALID_INPUT"
}
```

#### 409 Conflict (Workspace Already Exists)

```json
{
  "status": "error",
  "code": 409,
  "message": null,
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "error_message": "Workspace already exists",
  "error_code": "RESOURCE_ALREADY_EXISTS"
}
```

---

## 2. Get Workspace Details

### 📌 Endpoint Bilgileri

- **Method:** `GET`
- **Route:** `{{base_url}}/workspaces/{{workspace_id}}`
- **Description:** Workspace detay bilgilerini getirir

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

---

### 🌐 Route

```
GET {{base_url}}/workspaces/{{workspace_id}}
```

---

### 📝 Path Variables

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `workspace_id` | string | ✅ Yes | Workspace ID'si (WSP- formatında) |

---

### 📨 Request Body

Bu endpoint request body kullanmaz.

---

### ✅ Success Response (200 OK)

```json
{
  "status": "success",
  "code": 200,
  "message": "Workspace details retrieved successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "id": "WSP-1234567890ABCDEF",
    "name": "My Workspace",
    "slug": "my-workspace",
    "description": "My first workspace description",
    "owner_id": "USR-1234567890ABCDEF",
    "owner": {
      "id": "USR-1234567890ABCDEF",
      "username": "john_doe",
      "email": "john.doe@example.com"
    },
    "plan_id": "PLN-1234567890ABCDEF",
    "plan_name": "Freemium",
    "is_suspended": false,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

---

### ❌ Error Responses

#### 403 Forbidden (Not a Member)

```json
{
  "status": "error",
  "code": 403,
  "message": null,
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "error_message": "You are not a member of this workspace",
  "error_code": "FORBIDDEN"
}
```

#### 404 Not Found (Workspace Not Found)

```json
{
  "status": "error",
  "code": 404,
  "message": null,
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "error_message": "Workspace not found",
  "error_code": "RESOURCE_NOT_FOUND"
}
```

---

## 3. Get Workspace Limits

### 📌 Endpoint Bilgileri

- **Method:** `GET`
- **Route:** `{{base_url}}/workspaces/{{workspace_id}}/limits`
- **Description:** Workspace kaynak limitlerini ve mevcut kullanımı getirir

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

---

### 🌐 Route

```
GET {{base_url}}/workspaces/{{workspace_id}}/limits
```

---

### 📝 Path Variables

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `workspace_id` | string | ✅ Yes | Workspace ID'si |

---

### 📨 Request Body

Bu endpoint request body kullanmaz.

---

### ✅ Success Response (200 OK)

```json
{
  "status": "success",
  "code": 200,
  "message": "Workspace limits retrieved successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "workspace_id": "WSP-1234567890ABCDEF",
    "plan_name": "Freemium",
    "limits": {
      "members": {
        "limit": 5,
        "current": 1,
        "remaining": 4
      },
      "workflows": {
        "limit": 10,
        "current": 2,
        "remaining": 8
      },
      "custom_scripts": {
        "limit": 5,
        "current": 0,
        "remaining": 5
      },
      "storage_mb": {
        "limit": 100,
        "current": 25,
        "remaining": 75
      },
      "api_keys": {
        "limit": 3,
        "current": 1,
        "remaining": 2
      },
      "monthly_executions": {
        "limit": 1000,
        "current": 150,
        "remaining": 850
      }
    }
  }
}
```

---

## 4. Update Workspace

### 📌 Endpoint Bilgileri

- **Method:** `PUT`
- **Route:** `{{base_url}}/workspaces/{{workspace_id}}`
- **Description:** Workspace bilgilerini günceller (name, slug, description)

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

---

### 🌐 Route

```
PUT {{base_url}}/workspaces/{{workspace_id}}
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
  "name": "Updated Workspace Name",
  "slug": "updated-workspace-slug",
  "description": "Updated description"
}
```

**Body Parametreleri (Tümü Opsiyonel):**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | ❌ No | Workspace adı (1-100 karakter) |
| `slug` | string | ❌ No | Workspace slug (1-100 karakter) |
| `description` | string | ❌ No | Workspace açıklaması (max 500 karakter) |

**Not:** Sadece gönderilen alanlar güncellenir.

---

### ✅ Success Response (200 OK)

```json
{
  "status": "success",
  "code": 200,
  "message": "Workspace updated successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "id": "WSP-1234567890ABCDEF",
    "name": "Updated Workspace Name",
    "slug": "updated-workspace-slug",
    "description": "Updated description",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

---

### ❌ Error Responses

#### 409 Conflict (Slug Already Exists)

```json
{
  "status": "error",
  "code": 409,
  "message": null,
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "error_message": "Workspace with this slug already exists",
  "error_code": "RESOURCE_ALREADY_EXISTS"
}
```

---

## 5. Delete Workspace

### 📌 Endpoint Bilgileri

- **Method:** `DELETE`
- **Route:** `{{base_url}}/workspaces/{{workspace_id}}`
- **Description:** Workspace'i ve tüm ilişkili kaynakları siler

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

**⚠️ UYARI:** Bu işlem geri alınamaz! Workspace ve tüm ilişkili veriler kalıcı olarak silinir.

---

### 🌐 Route

```
DELETE {{base_url}}/workspaces/{{workspace_id}}
```

---

### 📝 Path Variables

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `workspace_id` | string | ✅ Yes | Workspace ID'si |

---

### 📨 Request Body

Bu endpoint request body kullanmaz.

---

### ✅ Success Response (200 OK)

```json
{
  "status": "success",
  "code": 200,
  "message": "Workspace deleted successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "workspace_id": "WSP-1234567890ABCDEF",
    "deleted_at": "2024-01-01T00:00:00Z",
    "resources_deleted": {
      "members": 5,
      "workflows": 10,
      "scripts": 3,
      "files": 15,
      "variables": 8,
      "api_keys": 2
    }
  }
}
```

**Silinen Kaynaklar:**
- Workspace üyeleri
- Workspace davetleri
- Workflow'lar ve execution'lar
- Script'ler (custom)
- Değişkenler (variables)
- Dosyalar (files)
- Database bağlantıları
- Credential'lar
- API key'ler
- Workspace klasörleri ve dosyaları

---

### ❌ Error Responses

#### 403 Forbidden (Not a Member)

```json
{
  "status": "error",
  "code": 403,
  "message": null,
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "error_message": "You are not a member of this workspace",
  "error_code": "FORBIDDEN"
}
```

---

## 🧪 Test Senaryoları

### Senaryo 1: Workspace Oluşturma ve Yönetimi

1. **Workspace oluştur:**
   ```
   POST {{base_url}}/workspaces
   Headers: Authorization: Bearer {{access_token}}
   Body: { "name": "My Workspace", "slug": "my-workspace", ... }
   ```

2. **Workspace detaylarını al:**
   ```
   GET {{base_url}}/workspaces/{{workspace_id}}
   Headers: Authorization: Bearer {{access_token}}
   ```

3. **Workspace limitlerini kontrol et:**
   ```
   GET {{base_url}}/workspaces/{{workspace_id}}/limits
   Headers: Authorization: Bearer {{access_token}}
   ```

4. **Workspace bilgilerini güncelle:**
   ```
   PUT {{base_url}}/workspaces/{{workspace_id}}
   Headers: Authorization: Bearer {{access_token}}
   Body: { "name": "Updated Name", ... }
   ```

---

### Senaryo 2: Workspace Silme (Dikkatli!)

1. **Workspace'i sil:**
   ```
   DELETE {{base_url}}/workspaces/{{workspace_id}}
   Headers: Authorization: Bearer {{access_token}}
   ```

**⚠️ UYARI:** Bu işlem geri alınamaz!

---

## 📝 Postman/Bruno Collection Örneği

### Environment Variables

```json
{
  "base_url": "http://localhost:8000",
  "access_token": "",
  "workspace_id": "",
  "user_id": ""
}
```

### Collection Structure

```
Workspace Routes
├── Create Workspace
├── Get Workspace Details
├── Get Workspace Limits
├── Update Workspace
└── Delete Workspace
```

---

## 🔗 İlgili Endpoint'ler

- **POST /auth/login** - Giriş yapmak için (access_token almak için)
- **GET /users/{{user_id}}/workspaces** - Kullanıcının workspace'lerini listelemek için
- **GET /workspaces/{{workspace_id}}/members** - Workspace üyelerini listelemek için
- **POST /workspaces/{{workspace_id}}/workflows** - Workspace'te workflow oluşturmak için

---

## 📌 Notlar

1. **Workspace ID Format:** `WSP-[16 haneli hexadecimal]` (örn: `WSP-1234567890ABCDEF`)
2. **Workspace Slug:** URL-friendly identifier, benzersiz olmalı
3. **Freemium Plan:** Yeni workspace'ler otomatik olarak Freemium planı ile oluşturulur
4. **Workspace Membership:** Tüm endpoint'ler workspace üyeliği gerektirir
5. **Delete İşlemi:** Workspace silme işlemi geri alınamaz, tüm ilişkili veriler silinir
6. **Limit Kontrolleri:** Workspace limitleri plan'a göre belirlenir
7. **Owner:** Workspace oluşturan kullanıcı otomatik olarak Owner rolü alır

---

## 🎯 Workspace ID Format Kontrolü

Workspace ID'leri şu formatta olmalıdır:
- Format: `WSP-[A-F0-9]{16}`
- Örnek: `WSP-1234567890ABCDEF`
- Regex: `^WSP-[A-F0-9]{16}$`

Geçersiz format durumunda **400 Bad Request** hatası döner.

---

**Son Güncelleme:** 2024  
**Versiyon:** 1.0

