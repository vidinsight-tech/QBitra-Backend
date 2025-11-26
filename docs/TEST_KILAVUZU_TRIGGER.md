# Trigger Routes - Test Kılavuzu

## 📋 Genel Bilgiler

- **Base URL:** `{{base_url}}`
- **Prefix:** `/workspaces/{workspace_id}/triggers` ve `/workspaces/{workspace_id}/workflows/{workflow_id}/triggers`
- **Authentication:** Tüm endpoint'ler Bearer token gerektirir
- **Content-Type:** `application/json`
- **Workspace ID Format:** `WSP-[16 haneli hexadecimal]`

---

## 1. Get All Triggers

### 📌 Endpoint Bilgileri

- **Method:** `GET`
- **Route:** `{{base_url}}/workspaces/{{workspace_id}}/triggers`
- **Description:** Workspace'teki tüm trigger'ları pagination ve filtreleme ile getirir

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

---

### 🌐 Route

```
GET {{base_url}}/workspaces/{{workspace_id}}/triggers
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
| `include_deleted` | boolean | ❌ No | false | Silinen trigger'ları dahil et |
| `workflow_id` | string | ❌ No | - | Workflow ID'ye göre filtrele |
| `trigger_type` | string | ❌ No | - | Trigger tipine göre filtrele (MANUAL, SCHEDULED, WEBHOOK, EVENT) |
| `is_enabled` | boolean | ❌ No | - | Enabled durumuna göre filtrele |

---

### 📨 Request Body

Bu endpoint request body kullanmaz.

---

### ✅ Success Response (200 OK)

```json
{
  "status": "success",
  "code": 200,
  "message": "Triggers retrieved successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "items": [
      {
        "id": "TRG-1234567890ABCDEF",
        "name": "DEFAULT",
        "trigger_type": "WEBHOOK",
        "config": {
          "method": "POST",
          "path": "/webhook/trigger-id"
        },
        "description": "Default webhook trigger",
        "input_mapping": null,
        "is_enabled": true,
        "workflow_id": "WFL-1234567890ABCDEF",
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

## 2. Get Trigger

### 📌 Endpoint Bilgileri

- **Method:** `GET`
- **Route:** `{{base_url}}/workspaces/{{workspace_id}}/triggers/{{trigger_id}}`
- **Description:** Belirli bir trigger'ın detay bilgilerini getirir

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

---

### 🌐 Route

```
GET {{base_url}}/workspaces/{{workspace_id}}/triggers/{{trigger_id}}
```

---

### 📝 Path Variables

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `workspace_id` | string | ✅ Yes | Workspace ID'si |
| `trigger_id` | string | ✅ Yes | Trigger ID'si |

---

### 📨 Request Body

Bu endpoint request body kullanmaz.

---

### ✅ Success Response (200 OK)

```json
{
  "status": "success",
  "code": 200,
  "message": "Trigger retrieved successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "id": "TRG-1234567890ABCDEF",
    "name": "DEFAULT",
    "trigger_type": "WEBHOOK",
    "config": {
      "method": "POST",
      "path": "/webhook/trigger-id",
      "headers": {},
      "query_params": {}
    },
    "description": "Default webhook trigger",
    "input_mapping": null,
    "is_enabled": true,
    "workflow_id": "WFL-1234567890ABCDEF",
    "workspace_id": "WSP-1234567890ABCDEF",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "created_by": "USR-1234567890ABCDEF",
    "updated_by": null
  }
}
```

---

## 3. Create Trigger

### 📌 Endpoint Bilgileri

- **Method:** `POST`
- **Route:** `{{base_url}}/workspaces/{{workspace_id}}/workflows/{{workflow_id}}/triggers`
- **Description:** Workflow için yeni trigger oluşturur

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

---

### 🌐 Route

```
POST {{base_url}}/workspaces/{{workspace_id}}/workflows/{{workflow_id}}/triggers
```

---

### 📝 Path Variables

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `workspace_id` | string | ✅ Yes | Workspace ID'si |
| `workflow_id` | string | ✅ Yes | Workflow ID'si |

---

### 📨 Request Body

**WEBHOOK Trigger Örneği:**
```json
{
  "name": "Webhook Trigger",
  "trigger_type": "WEBHOOK",
  "config": {
    "method": "POST",
    "path": "/webhook/custom-path",
    "headers": {
      "X-Custom-Header": "value"
    },
    "query_params": {
      "token": "secret-token"
    }
  },
  "description": "Webhook trigger for external integrations",
  "input_mapping": {
    "INPUT_DATA": {
      "type": "json",
      "value": "$.body.data"
    }
  },
  "is_enabled": true
}
```

**SCHEDULED Trigger Örneği:**
```json
{
  "name": "Daily Schedule",
  "trigger_type": "SCHEDULED",
  "config": {
    "schedule": "0 0 * * *",
    "timezone": "UTC"
  },
  "description": "Runs daily at midnight",
  "input_mapping": null,
  "is_enabled": true
}
```

**MANUAL Trigger Örneği:**
```json
{
  "name": "Manual Trigger",
  "trigger_type": "MANUAL",
  "config": {},
  "description": "Manual execution trigger",
  "input_mapping": null,
  "is_enabled": true
}
```

**EVENT Trigger Örneği:**
```json
{
  "name": "Event Trigger",
  "trigger_type": "EVENT",
  "config": {
    "event_type": "user.created",
    "filters": {
      "workspace_id": "WSP-1234567890ABCDEF"
    }
  },
  "description": "Triggers on user creation event",
  "input_mapping": {
    "USER_ID": {
      "type": "string",
      "value": "$.event.user_id"
    }
  },
  "is_enabled": true
}
```

**Body Parametreleri:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | ✅ Yes | Trigger adı (workspace içinde benzersiz olmalı) |
| `trigger_type` | string | ✅ Yes | Trigger tipi: MANUAL, SCHEDULED, WEBHOOK, EVENT |
| `config` | object | ✅ Yes | Trigger konfigürasyonu (tip'e göre değişir) |
| `description` | string | ❌ No | Trigger açıklaması |
| `input_mapping` | object | ❌ No | Input mapping kuralları |
| `is_enabled` | boolean | ❌ No | Aktif/pasif durumu (default: true) |

**Trigger Type Config Örnekleri:**

**WEBHOOK:**
```json
{
  "method": "POST",
  "path": "/webhook/path",
  "headers": {},
  "query_params": {}
}
```

**SCHEDULED:**
```json
{
  "schedule": "0 0 * * *",
  "timezone": "UTC"
}
```

**MANUAL:**
```json
{}
```

**EVENT:**
```json
{
  "event_type": "user.created",
  "filters": {}
}
```

---

### ✅ Success Response (201 Created)

```json
{
  "status": "success",
  "code": 201,
  "message": "Trigger created successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "id": "TRG-1234567890ABCDEF",
    "name": "Webhook Trigger",
    "trigger_type": "WEBHOOK",
    "config": {
      "method": "POST",
      "path": "/webhook/custom-path",
      "headers": {
        "X-Custom-Header": "value"
      },
      "query_params": {
        "token": "secret-token"
      }
    },
    "description": "Webhook trigger for external integrations",
    "input_mapping": {
      "INPUT_DATA": {
        "type": "json",
        "value": "$.body.data"
      }
    },
    "is_enabled": true,
    "workflow_id": "WFL-1234567890ABCDEF",
    "workspace_id": "WSP-1234567890ABCDEF",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "created_by": "USR-1234567890ABCDEF",
    "updated_by": null
  }
}
```

---

## 4. Update Trigger

### 📌 Endpoint Bilgileri

- **Method:** `PUT`
- **Route:** `{{base_url}}/workspaces/{{workspace_id}}/triggers/{{trigger_id}}`
- **Description:** Mevcut trigger'ı günceller

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

---

### 🌐 Route

```
PUT {{base_url}}/workspaces/{{workspace_id}}/triggers/{{trigger_id}}
```

---

### 📝 Path Variables

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `workspace_id` | string | ✅ Yes | Workspace ID'si |
| `trigger_id` | string | ✅ Yes | Trigger ID'si |

---

### 📨 Request Body

```json
{
  "name": "Updated Trigger Name",
  "description": "Updated description",
  "trigger_type": "WEBHOOK",
  "config": {
    "method": "POST",
    "path": "/webhook/updated-path"
  },
  "input_mapping": {
    "UPDATED_INPUT": {
      "type": "string",
      "value": "$.body.updated"
    }
  },
  "is_enabled": false
}
```

**Body Parametreleri (Tümü Opsiyonel):**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | ❌ No | Trigger adı (workspace içinde benzersiz olmalı) |
| `description` | string | ❌ No | Trigger açıklaması |
| `trigger_type` | string | ❌ No | Trigger tipi |
| `config` | object | ❌ No | Trigger konfigürasyonu |
| `input_mapping` | object | ❌ No | Input mapping kuralları |
| `is_enabled` | boolean | ❌ No | Aktif/pasif durumu |

---

### ✅ Success Response (200 OK)

```json
{
  "status": "success",
  "code": 200,
  "message": "Trigger updated successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "id": "TRG-1234567890ABCDEF",
    "name": "Updated Trigger Name",
    "trigger_type": "WEBHOOK",
    "config": {
      "method": "POST",
      "path": "/webhook/updated-path"
    },
    "description": "Updated description",
    "input_mapping": {
      "UPDATED_INPUT": {
        "type": "string",
        "value": "$.body.updated"
      }
    },
    "is_enabled": false,
    "updated_at": "2024-01-01T00:00:00Z",
    "updated_by": "USR-1234567890ABCDEF"
  }
}
```

---

## 5. Delete Trigger

### 📌 Endpoint Bilgileri

- **Method:** `DELETE`
- **Route:** `{{base_url}}/workspaces/{{workspace_id}}/triggers/{{trigger_id}}`
- **Description:** Trigger'ı siler

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

**⚠️ UYARI:** Bu işlem geri alınamaz! Trigger kalıcı olarak silinir.

---

### 🌐 Route

```
DELETE {{base_url}}/workspaces/{{workspace_id}}/triggers/{{trigger_id}}
```

---

### 📝 Path Variables

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `workspace_id` | string | ✅ Yes | Workspace ID'si |
| `trigger_id` | string | ✅ Yes | Trigger ID'si |

---

### 📨 Request Body

Bu endpoint request body kullanmaz.

---

### ✅ Success Response (200 OK)

```json
{
  "status": "success",
  "code": 200,
  "message": "Trigger deleted successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "trigger_id": "TRG-1234567890ABCDEF",
    "deleted_at": "2024-01-01T00:00:00Z"
  }
}
```

---

## 🧪 Test Senaryoları

### Senaryo 1: Webhook Trigger Oluşturma

1. **Webhook trigger oluştur:**
   ```
   POST {{base_url}}/workspaces/{{workspace_id}}/workflows/{{workflow_id}}/triggers
   Headers: Authorization: Bearer {{access_token}}
   Body: {
     "name": "Webhook Trigger",
     "trigger_type": "WEBHOOK",
     "config": {
       "method": "POST",
       "path": "/webhook/my-trigger"
     },
     "is_enabled": true
   }
   ```

2. **Trigger'ı test et:**
   ```
   POST {{base_url}}/webhook/my-trigger
   Body: { "data": "test" }
   ```

---

### Senaryo 2: Scheduled Trigger Oluşturma

1. **Scheduled trigger oluştur:**
   ```
   POST {{base_url}}/workspaces/{{workspace_id}}/workflows/{{workflow_id}}/triggers
   Body: {
     "name": "Daily Schedule",
     "trigger_type": "SCHEDULED",
     "config": {
       "schedule": "0 0 * * *",
       "timezone": "UTC"
     },
     "is_enabled": true
   }
   ```

---

### Senaryo 3: Trigger Filtreleme

1. **Sadece webhook trigger'ları getir:**
   ```
   GET {{base_url}}/workspaces/{{workspace_id}}/triggers?trigger_type=WEBHOOK
   ```

2. **Belirli workflow'un trigger'larını getir:**
   ```
   GET {{base_url}}/workspaces/{{workspace_id}}/triggers?workflow_id={{workflow_id}}
   ```

3. **Sadece aktif trigger'ları getir:**
   ```
   GET {{base_url}}/workspaces/{{workspace_id}}/triggers?is_enabled=true
   ```

---

## 📝 Postman/Bruno Collection Örneği

### Environment Variables

```json
{
  "base_url": "http://localhost:8000",
  "access_token": "",
  "workspace_id": "",
  "workflow_id": "",
  "trigger_id": ""
}
```

---

## 🔗 İlgili Endpoint'ler

- **POST /workspaces/{{workspace_id}}/workflows** - Workflow oluşturmak için (otomatik DEFAULT trigger oluşturulur)
- **GET /workspaces/{{workspace_id}}/workflows/{{workflow_id}}** - Workflow detaylarını almak için
- **POST /workspaces/{{workspace_id}}/workflows/{{workflow_id}}/execute** - Workflow'u manuel olarak çalıştırmak için

---

## 📌 Notlar

1. **Default Trigger:**
   - Her workflow oluşturulduğunda otomatik olarak "DEFAULT" adında bir WEBHOOK trigger oluşturulur
   - Bu trigger silinebilir veya güncellenebilir

2. **Trigger Types:**
   - **MANUAL:** Manuel çalıştırma (API üzerinden)
   - **SCHEDULED:** Zamanlanmış çalıştırma (cron expression)
   - **WEBHOOK:** HTTP webhook ile tetikleme
   - **EVENT:** Sistem event'leri ile tetikleme

3. **Trigger Config:**
   - Her trigger tipi için farklı config yapısı gerekir
   - WEBHOOK: method, path, headers, query_params
   - SCHEDULED: schedule (cron), timezone
   - MANUAL: boş config
   - EVENT: event_type, filters

4. **Input Mapping:**
   - Trigger'dan gelen verileri workflow input'larına map etmek için kullanılır
   - Format: `{VARIABLE_NAME: {type: str, value: Any}}`
   - JSON path expression'lar kullanılabilir (örn: `$.body.data`)

5. **Trigger Name:**
   - Workspace içinde benzersiz olmalıdır
   - "DEFAULT" adı workflow oluşturulduğunda otomatik kullanılır

6. **Trigger Enable/Disable:**
   - `is_enabled: false` olan trigger'lar çalıştırılamaz
   - Pasif trigger'lar listede görünür ama tetiklenmez

7. **Webhook Path:**
   - WEBHOOK trigger'lar için path belirtilir
   - Webhook URL: `{{base_url}}/webhook/{path}`
   - Path benzersiz olmalıdır

---

**Son Güncelleme:** 2024  
**Versiyon:** 1.0

