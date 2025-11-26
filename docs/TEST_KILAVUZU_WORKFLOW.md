# Workflow Routes - Test Kılavuzu

## 📋 Genel Bilgiler

- **Base URL:** `{{base_url}}`
- **Prefix:** `/workspaces/{workspace_id}/workflows`
- **Authentication:** Tüm endpoint'ler Bearer token gerektirir
- **Content-Type:** `application/json`
- **Workspace ID Format:** `WSP-[16 haneli hexadecimal]`

---

## 1. Get All Workflows

### 📌 Endpoint Bilgileri

- **Method:** `GET`
- **Route:** `{{base_url}}/workspaces/{{workspace_id}}/workflows`
- **Description:** Workspace'teki tüm workflow'ları pagination ve filtreleme ile getirir

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

---

### 🌐 Route

```
GET {{base_url}}/workspaces/{{workspace_id}}/workflows
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
| `include_deleted` | boolean | ❌ No | false | Silinen workflow'ları dahil et |
| `status` | string | ❌ No | - | Durum filtresi (DRAFT, ACTIVE, DEACTIVATED, ARCHIVED) |

---

### 📨 Request Body

Bu endpoint request body kullanmaz.

---

### ✅ Success Response (200 OK)

```json
{
  "status": "success",
  "code": 200,
  "message": "Workflows retrieved successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "items": [
      {
        "id": "WFL-1234567890ABCDEF",
        "name": "Data Processing Workflow",
        "description": "Processes incoming data",
        "priority": 1,
        "status": "DRAFT",
        "status_message": "Currently no error context is available",
        "tags": ["data", "processing"],
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

---

## 2. Get Workflow

### 📌 Endpoint Bilgileri

- **Method:** `GET`
- **Route:** `{{base_url}}/workspaces/{{workspace_id}}/workflows/{{workflow_id}}`
- **Description:** Belirli bir workflow'un detay bilgilerini getirir

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

---

### 🌐 Route

```
GET {{base_url}}/workspaces/{{workspace_id}}/workflows/{{workflow_id}}
```

---

### 📝 Path Variables

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `workspace_id` | string | ✅ Yes | Workspace ID'si |
| `workflow_id` | string | ✅ Yes | Workflow ID'si |

---

### 📨 Request Body

Bu endpoint request body kullanmaz.

---

### ✅ Success Response (200 OK)

```json
{
  "status": "success",
  "code": 200,
  "message": "Workflow retrieved successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "id": "WFL-1234567890ABCDEF",
    "name": "Data Processing Workflow",
    "description": "Processes incoming data",
    "priority": 1,
    "status": "DRAFT",
    "status_message": "Currently no error context is available",
    "tags": ["data", "processing"],
    "workspace_id": "WSP-1234567890ABCDEF",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "created_by": "USR-1234567890ABCDEF",
    "updated_by": null
  }
}
```

---

## 3. Create Workflow

### 📌 Endpoint Bilgileri

- **Method:** `POST`
- **Route:** `{{base_url}}/workspaces/{{workspace_id}}/workflows`
- **Description:** Yeni workflow oluşturur (otomatik olarak DEFAULT trigger oluşturulur)

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

---

### 🌐 Route

```
POST {{base_url}}/workspaces/{{workspace_id}}/workflows
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
  "name": "Data Processing Workflow",
  "description": "Processes incoming data",
  "priority": 1,
  "status": "DRAFT",
  "status_message": null,
  "tags": ["data", "processing"]
}
```

**Body Parametreleri:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | ✅ Yes | Workflow adı (workspace içinde benzersiz olmalı) |
| `description` | string | ❌ No | Workflow açıklaması |
| `priority` | integer | ❌ No | Öncelik seviyesi (default: 1, min: 1) |
| `status` | string | ❌ No | Durum (default: DRAFT) - DRAFT, ACTIVE, DEACTIVATED, ARCHIVED |
| `status_message` | string | ❌ No | Durum mesajı |
| `tags` | array | ❌ No | Etiketler |

**Not:** Workflow oluşturulduğunda otomatik olarak "DEFAULT" adında bir WEBHOOK trigger oluşturulur.

---

### ✅ Success Response (201 Created)

```json
{
  "status": "success",
  "code": 201,
  "message": "Workflow created successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "id": "WFL-1234567890ABCDEF",
    "name": "Data Processing Workflow",
    "description": "Processes incoming data",
    "priority": 1,
    "status": "DRAFT",
    "status_message": "Currently no error context is available",
    "tags": ["data", "processing"],
    "workspace_id": "WSP-1234567890ABCDEF",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "created_by": "USR-1234567890ABCDEF",
    "updated_by": null
  }
}
```

---

## 4. Update Workflow

### 📌 Endpoint Bilgileri

- **Method:** `PUT`
- **Route:** `{{base_url}}/workspaces/{{workspace_id}}/workflows/{{workflow_id}}`
- **Description:** Mevcut workflow'u günceller

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

---

### 🌐 Route

```
PUT {{base_url}}/workspaces/{{workspace_id}}/workflows/{{workflow_id}}
```

---

### 📝 Path Variables

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `workspace_id` | string | ✅ Yes | Workspace ID'si |
| `workflow_id` | string | ✅ Yes | Workflow ID'si |

---

### 📨 Request Body

```json
{
  "name": "Updated Workflow Name",
  "description": "Updated description",
  "priority": 2,
  "status": "ACTIVE",
  "status_message": "Workflow is active",
  "tags": ["updated", "active"]
}
```

**Body Parametreleri (Tümü Opsiyonel):**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | ❌ No | Workflow adı (workspace içinde benzersiz olmalı) |
| `description` | string | ❌ No | Workflow açıklaması |
| `priority` | integer | ❌ No | Öncelik seviyesi (min: 1) |
| `status` | string | ❌ No | Durum - DRAFT, ACTIVE, DEACTIVATED, ARCHIVED |
| `status_message` | string | ❌ No | Durum mesajı |
| `tags` | array | ❌ No | Etiketler |

---

### ✅ Success Response (200 OK)

```json
{
  "status": "success",
  "code": 200,
  "message": "Workflow updated successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "id": "WFL-1234567890ABCDEF",
    "name": "Updated Workflow Name",
    "description": "Updated description",
    "priority": 2,
    "status": "ACTIVE",
    "status_message": "Workflow is active",
    "tags": ["updated", "active"],
    "updated_at": "2024-01-01T00:00:00Z",
    "updated_by": "USR-1234567890ABCDEF"
  }
}
```

---

## 5. Delete Workflow

### 📌 Endpoint Bilgileri

- **Method:** `DELETE`
- **Route:** `{{base_url}}/workspaces/{{workspace_id}}/workflows/{{workflow_id}}`
- **Description:** Workflow'u ve tüm ilişkili kaynakları siler (CASCADE)

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

**⚠️ UYARI:** Bu işlem geri alınamaz! Workflow ve tüm ilişkili veriler kalıcı olarak silinir.

---

### 🌐 Route

```
DELETE {{base_url}}/workspaces/{{workspace_id}}/workflows/{{workflow_id}}
```

---

### 📝 Path Variables

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `workspace_id` | string | ✅ Yes | Workspace ID'si |
| `workflow_id` | string | ✅ Yes | Workflow ID'si |

---

### 📨 Request Body

Bu endpoint request body kullanmaz.

---

### ✅ Success Response (200 OK)

```json
{
  "status": "success",
  "code": 200,
  "message": "Workflow deleted successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "workflow_id": "WFL-1234567890ABCDEF",
    "deleted_at": "2024-01-01T00:00:00Z"
  }
}
```

**Silinen Kaynaklar:**
- Workflow
- Tüm node'lar
- Tüm edge'ler
- Tüm trigger'lar
- Tüm execution'lar (CASCADE)

---

## 🧪 Test Senaryoları

### Senaryo 1: Workflow Oluşturma ve Yönetimi

1. **Workflow oluştur:**
   ```
   POST {{base_url}}/workspaces/{{workspace_id}}/workflows
   Headers: Authorization: Bearer {{access_token}}
   Body: { "name": "My Workflow", ... }
   ```

2. **Workflow listesini al:**
   ```
   GET {{base_url}}/workspaces/{{workspace_id}}/workflows?page=1&page_size=10
   Headers: Authorization: Bearer {{access_token}}
   ```

3. **Workflow detaylarını al:**
   ```
   GET {{base_url}}/workspaces/{{workspace_id}}/workflows/{{workflow_id}}
   Headers: Authorization: Bearer {{access_token}}
   ```

4. **Workflow'u güncelle:**
   ```
   PUT {{base_url}}/workspaces/{{workspace_id}}/workflows/{{workflow_id}}
   Headers: Authorization: Bearer {{access_token}}
   Body: { "status": "ACTIVE", ... }
   ```

---

### Senaryo 2: Workflow Filtreleme

1. **Sadece aktif workflow'ları getir:**
   ```
   GET {{base_url}}/workspaces/{{workspace_id}}/workflows?status=ACTIVE
   ```

2. **Silinen workflow'ları dahil et:**
   ```
   GET {{base_url}}/workspaces/{{workspace_id}}/workflows?include_deleted=true
   ```

3. **Önceliğe göre sırala:**
   ```
   GET {{base_url}}/workspaces/{{workspace_id}}/workflows?order_by=priority&order_desc=true
   ```

---

## 📝 Postman/Bruno Collection Örneği

### Environment Variables

```json
{
  "base_url": "http://localhost:8000",
  "access_token": "",
  "workspace_id": "",
  "workflow_id": ""
}
```

---

## 🔗 İlgili Endpoint'ler

- **GET /workspaces/{{workspace_id}}** - Workspace bilgilerini almak için
- **POST /workspaces/{{workspace_id}}/workflows/{{workflow_id}}/nodes** - Node oluşturmak için
- **POST /workspaces/{{workspace_id}}/workflows/{{workflow_id}}/triggers** - Trigger oluşturmak için
- **POST /workspaces/{{workspace_id}}/workflows/{{workflow_id}}/edges** - Edge oluşturmak için

---

## 📌 Notlar

1. **Workflow Oluşturma:** Yeni workflow oluşturulduğunda otomatik olarak "DEFAULT" adında bir WEBHOOK trigger oluşturulur.
2. **Workflow Status:** DRAFT, ACTIVE, DEACTIVATED, ARCHIVED değerlerini alabilir.
3. **Workflow Silme:** Workflow silindiğinde tüm ilişkili kaynaklar (node, edge, trigger, execution) CASCADE olarak silinir.
4. **Workflow Name:** Workspace içinde benzersiz olmalıdır.
5. **Pagination:** Default olarak sayfa başına 100 kayıt döner, maksimum 1000.

---

**Son Güncelleme:** 2024  
**Versiyon:** 1.0

