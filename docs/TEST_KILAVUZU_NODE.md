# Node Routes - Test Kılavuzu

## 📋 Genel Bilgiler

- **Base URL:** `{{base_url}}`
- **Prefix:** `/workspaces/{workspace_id}/workflows/{workflow_id}/nodes`
- **Authentication:** Tüm endpoint'ler Bearer token gerektirir
- **Content-Type:** `application/json`
- **Workspace ID Format:** `WSP-[16 haneli hexadecimal]`

---

## 1. Get All Nodes

### 📌 Endpoint Bilgileri

- **Method:** `GET`
- **Route:** `{{base_url}}/workspaces/{{workspace_id}}/workflows/{{workflow_id}}/nodes`
- **Description:** Workflow'daki tüm node'ları pagination ile getirir

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

---

### 🌐 Route

```
GET {{base_url}}/workspaces/{{workspace_id}}/workflows/{{workflow_id}}/nodes
```

---

### 📝 Path Variables

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `workspace_id` | string | ✅ Yes | Workspace ID'si (WSP- formatında) |
| `workflow_id` | string | ✅ Yes | Workflow ID'si |

---

### 📝 Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `page` | integer | ❌ No | 1 | Sayfa numarası (min: 1) |
| `page_size` | integer | ❌ No | 100 | Sayfa başına kayıt sayısı (1-1000) |
| `order_by` | string | ❌ No | created_at | Sıralama alanı |
| `order_desc` | boolean | ❌ No | false | Azalan sıralama |
| `include_deleted` | boolean | ❌ No | false | Silinen node'ları dahil et |

---

### 📨 Request Body

Bu endpoint request body kullanmaz.

---

### ✅ Success Response (200 OK)

```json
{
  "status": "success",
  "code": 200,
  "message": "Nodes retrieved successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "items": [
      {
        "id": "NOD-1234567890ABCDEF",
        "name": "Process Data",
        "description": "Processes incoming data",
        "script_id": "SCR-1234567890ABCDEF",
        "script_type": "GLOBAL",
        "input_params": {
          "data": "input_data",
          "format": "json"
        },
        "output_params": {},
        "meta_data": {},
        "max_retries": 3,
        "timeout_seconds": 300,
        "workflow_id": "WFL-1234567890ABCDEF",
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

## 2. Get Node

### 📌 Endpoint Bilgileri

- **Method:** `GET`
- **Route:** `{{base_url}}/workspaces/{{workspace_id}}/workflows/{{workflow_id}}/nodes/{{node_id}}`
- **Description:** Belirli bir node'un detay bilgilerini getirir

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

---

### 🌐 Route

```
GET {{base_url}}/workspaces/{{workspace_id}}/workflows/{{workflow_id}}/nodes/{{node_id}}
```

---

### 📝 Path Variables

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `workspace_id` | string | ✅ Yes | Workspace ID'si |
| `workflow_id` | string | ✅ Yes | Workflow ID'si |
| `node_id` | string | ✅ Yes | Node ID'si |

---

### 📨 Request Body

Bu endpoint request body kullanmaz.

---

### ✅ Success Response (200 OK)

```json
{
  "status": "success",
  "code": 200,
  "message": "Node retrieved successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "id": "NOD-1234567890ABCDEF",
    "name": "Process Data",
    "description": "Processes incoming data",
    "script_id": "SCR-1234567890ABCDEF",
    "script_type": "GLOBAL",
    "script": {
      "id": "SCR-1234567890ABCDEF",
      "name": "Data Processor",
      "input_schema": {
        "type": "object",
        "properties": {
          "data": {"type": "string"},
          "format": {"type": "string", "enum": ["json", "xml", "csv"]}
        },
        "required": ["data"]
      }
    },
    "input_params": {
      "data": "input_data",
      "format": "json"
    },
    "output_params": {},
    "meta_data": {},
    "max_retries": 3,
    "timeout_seconds": 300,
    "workflow_id": "WFL-1234567890ABCDEF",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "created_by": "USR-1234567890ABCDEF",
    "updated_by": null
  }
}
```

---

## 3. Get Node Form Schema

### 📌 Endpoint Bilgileri

- **Method:** `GET`
- **Route:** `{{base_url}}/workspaces/{{workspace_id}}/workflows/{{workflow_id}}/nodes/{{node_id}}/form-schema`
- **Description:** Node için frontend form schema'sını getirir (script'in input_schema'sından türetilir)

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

---

### 🌐 Route

```
GET {{base_url}}/workspaces/{{workspace_id}}/workflows/{{workflow_id}}/nodes/{{node_id}}/form-schema
```

---

### 📝 Path Variables

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `workspace_id` | string | ✅ Yes | Workspace ID'si |
| `workflow_id` | string | ✅ Yes | Workflow ID'si |
| `node_id` | string | ✅ Yes | Node ID'si |

---

### 📨 Request Body

Bu endpoint request body kullanmaz.

---

### ✅ Success Response (200 OK)

```json
{
  "status": "success",
  "code": 200,
  "message": "Node form schema retrieved successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "schema": {
      "type": "object",
      "properties": {
        "data": {
          "type": "string",
          "title": "Data",
          "default": "input_data"
        },
        "format": {
          "type": "string",
          "title": "Format",
          "enum": ["json", "xml", "csv"],
          "default": "json"
        }
      },
      "required": ["data"]
    },
    "current_values": {
      "data": "input_data",
      "format": "json"
    }
  }
}
```

**Not:** Bu endpoint frontend'de dinamik form oluşturmak için kullanılır. Script'in `input_schema`'sından türetilir ve node'un mevcut `input_params` değerleri ile birleştirilir.

---

## 4. Create Node

### 📌 Endpoint Bilgileri

- **Method:** `POST`
- **Route:** `{{base_url}}/workspaces/{{workspace_id}}/workflows/{{workflow_id}}/nodes`
- **Description:** Workflow için yeni node oluşturur

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

---

### 🌐 Route

```
POST {{base_url}}/workspaces/{{workspace_id}}/workflows/{{workflow_id}}/nodes
```

---

### 📝 Path Variables

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `workspace_id` | string | ✅ Yes | Workspace ID'si |
| `workflow_id` | string | ✅ Yes | Workflow ID'si |

---

### 📨 Request Body

**Global Script ile Node:**
```json
{
  "name": "Process Data",
  "script_id": "SCR-1234567890ABCDEF",
  "description": "Processes incoming data",
  "input_params": {
    "data": "input_data",
    "format": "json"
  },
  "output_params": {},
  "meta_data": {},
  "max_retries": 3,
  "timeout_seconds": 300
}
```

**Custom Script ile Node:**
```json
{
  "name": "Custom Process",
  "custom_script_id": "CUS-1234567890ABCDEF",
  "description": "Uses custom script",
  "input_params": {
    "custom_param": "value"
  },
  "max_retries": 5,
  "timeout_seconds": 600
}
```

**Body Parametreleri:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | ✅ Yes | Node adı (workflow içinde benzersiz olmalı) |
| `script_id` | string | ❌ No* | Global script ID (script_id veya custom_script_id'den biri gerekli) |
| `custom_script_id` | string | ❌ No* | Custom script ID (script_id veya custom_script_id'den biri gerekli) |
| `description` | string | ❌ No | Node açıklaması |
| `input_params` | object | ❌ No | Input parametreleri (script'in input_schema'sına göre validate edilir) |
| `output_params` | object | ❌ No | Output parametreleri |
| `meta_data` | object | ❌ No | Metadata |
| `max_retries` | integer | ❌ No | Maksimum retry sayısı (default: 3, min: 0) |
| `timeout_seconds` | integer | ❌ No | Timeout süresi saniye (default: 300, min: 1) |

**Not:** `script_id` veya `custom_script_id`'den tam olarak biri sağlanmalıdır.

---

### ✅ Success Response (201 Created)

```json
{
  "status": "success",
  "code": 201,
  "message": "Node created successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "id": "NOD-1234567890ABCDEF",
    "name": "Process Data",
    "description": "Processes incoming data",
    "script_id": "SCR-1234567890ABCDEF",
    "script_type": "GLOBAL",
    "input_params": {
      "data": "input_data",
      "format": "json"
    },
    "output_params": {},
    "meta_data": {},
    "max_retries": 3,
    "timeout_seconds": 300,
    "workflow_id": "WFL-1234567890ABCDEF",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "created_by": "USR-1234567890ABCDEF",
    "updated_by": null
  }
}
```

---

## 5. Update Node

### 📌 Endpoint Bilgileri

- **Method:** `PUT`
- **Route:** `{{base_url}}/workspaces/{{workspace_id}}/workflows/{{workflow_id}}/nodes/{{node_id}}`
- **Description:** Mevcut node'u günceller

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

---

### 🌐 Route

```
PUT {{base_url}}/workspaces/{{workspace_id}}/workflows/{{workflow_id}}/nodes/{{node_id}}
```

---

### 📝 Path Variables

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `workspace_id` | string | ✅ Yes | Workspace ID'si |
| `workflow_id` | string | ✅ Yes | Workflow ID'si |
| `node_id` | string | ✅ Yes | Node ID'si |

---

### 📨 Request Body

```json
{
  "name": "Updated Node Name",
  "description": "Updated description",
  "input_params": {
    "data": "updated_data",
    "format": "xml"
  },
  "max_retries": 5,
  "timeout_seconds": 600
}
```

**Body Parametreleri (Tümü Opsiyonel):**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | ❌ No | Node adı (workflow içinde benzersiz olmalı) |
| `description` | string | ❌ No | Node açıklaması |
| `script_id` | string | ❌ No | Global script ID |
| `custom_script_id` | string | ❌ No | Custom script ID |
| `input_params` | object | ❌ No | Input parametreleri |
| `output_params` | object | ❌ No | Output parametreleri |
| `meta_data` | object | ❌ No | Metadata |
| `max_retries` | integer | ❌ No | Maksimum retry sayısı (min: 0) |
| `timeout_seconds` | integer | ❌ No | Timeout süresi saniye (min: 1) |

**Not:** Güncelleme sonrası `script_id` veya `custom_script_id`'den tam olarak biri olmalıdır.

---

### ✅ Success Response (200 OK)

```json
{
  "status": "success",
  "code": 200,
  "message": "Node updated successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "id": "NOD-1234567890ABCDEF",
    "name": "Updated Node Name",
    "description": "Updated description",
    "input_params": {
      "data": "updated_data",
      "format": "xml"
    },
    "max_retries": 5,
    "timeout_seconds": 600,
    "updated_at": "2024-01-01T00:00:00Z",
    "updated_by": "USR-1234567890ABCDEF"
  }
}
```

---

## 6. Update Node Input Params

### 📌 Endpoint Bilgileri

- **Method:** `PATCH`
- **Route:** `{{base_url}}/workspaces/{{workspace_id}}/workflows/{{workflow_id}}/nodes/{{node_id}}/input-params`
- **Description:** Sadece node'un input parametrelerini günceller

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

---

### 🌐 Route

```
PATCH {{base_url}}/workspaces/{{workspace_id}}/workflows/{{workflow_id}}/nodes/{{node_id}}/input-params
```

---

### 📝 Path Variables

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `workspace_id` | string | ✅ Yes | Workspace ID'si |
| `workflow_id` | string | ✅ Yes | Workflow ID'si |
| `node_id` | string | ✅ Yes | Node ID'si |

---

### 📨 Request Body

```json
{
  "input_params": {
    "data": "new_input_data",
    "format": "csv"
  }
}
```

**Body Parametreleri:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `input_params` | object | ✅ Yes | Input parametreleri (script'in input_schema'sına göre validate edilir) |

---

### ✅ Success Response (200 OK)

```json
{
  "status": "success",
  "code": 200,
  "message": "Node input parameters updated successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "id": "NOD-1234567890ABCDEF",
    "input_params": {
      "data": "new_input_data",
      "format": "csv"
    },
    "updated_at": "2024-01-01T00:00:00Z",
    "updated_by": "USR-1234567890ABCDEF"
  }
}
```

---

## 7. Delete Node

### 📌 Endpoint Bilgileri

- **Method:** `DELETE`
- **Route:** `{{base_url}}/workspaces/{{workspace_id}}/workflows/{{workflow_id}}/nodes/{{node_id}}`
- **Description:** Node'u siler

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

**⚠️ UYARI:** Bu işlem geri alınamaz! Node ve tüm ilişkili edge'ler kalıcı olarak silinir.

---

### 🌐 Route

```
DELETE {{base_url}}/workspaces/{{workspace_id}}/workflows/{{workflow_id}}/nodes/{{node_id}}
```

---

### 📝 Path Variables

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `workspace_id` | string | ✅ Yes | Workspace ID'si |
| `workflow_id` | string | ✅ Yes | Workflow ID'si |
| `node_id` | string | ✅ Yes | Node ID'si |

---

### 📨 Request Body

Bu endpoint request body kullanmaz.

---

### ✅ Success Response (200 OK)

```json
{
  "status": "success",
  "code": 200,
  "message": "Node deleted successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "node_id": "NOD-1234567890ABCDEF",
    "deleted_at": "2024-01-01T00:00:00Z"
  }
}
```

**Silinen Kaynaklar:**
- Node
- Node'a bağlı tüm edge'ler (CASCADE)

---

## 🧪 Test Senaryoları

### Senaryo 1: Node Oluşturma ve Yönetimi

1. **Global script ile node oluştur:**
   ```
   POST {{base_url}}/workspaces/{{workspace_id}}/workflows/{{workflow_id}}/nodes
   Headers: Authorization: Bearer {{access_token}}
   Body: {
     "name": "Process Data",
     "script_id": "SCR-...",
     "input_params": { ... }
   }
   ```

2. **Custom script ile node oluştur:**
   ```
   POST {{base_url}}/workspaces/{{workspace_id}}/workflows/{{workflow_id}}/nodes
   Body: {
     "name": "Custom Process",
     "custom_script_id": "CUS-...",
     "input_params": { ... }
   }
   ```

3. **Node listesini al:**
   ```
   GET {{base_url}}/workspaces/{{workspace_id}}/workflows/{{workflow_id}}/nodes
   ```

4. **Node form schema'sını al:**
   ```
   GET {{base_url}}/workspaces/{{workspace_id}}/workflows/{{workflow_id}}/nodes/{{node_id}}/form-schema
   ```

5. **Input parametrelerini güncelle:**
   ```
   PATCH {{base_url}}/workspaces/{{workspace_id}}/workflows/{{workflow_id}}/nodes/{{node_id}}/input-params
   Body: { "input_params": { ... } }
   ```

---

### Senaryo 2: Script Değiştirme

1. **Node'u global script'ten custom script'e çevir:**
   ```
   PUT {{base_url}}/workspaces/{{workspace_id}}/workflows/{{workflow_id}}/nodes/{{node_id}}
   Body: {
     "script_id": null,
     "custom_script_id": "CUS-..."
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
  "workflow_id": "",
  "node_id": "",
  "script_id": "",
  "custom_script_id": ""
}
```

---

## 🔗 İlgili Endpoint'ler

- **POST /workspaces/{{workspace_id}}/workflows** - Workflow oluşturmak için
- **GET /workspaces/{{workspace_id}}/workflows/{{workflow_id}}** - Workflow detaylarını almak için
- **POST /workspaces/{{workspace_id}}/workflows/{{workflow_id}}/edges** - Node'lar arası edge oluşturmak için
- **GET /workspaces/{{workspace_id}}/global-scripts** - Global script'leri listelemek için
- **GET /workspaces/{{workspace_id}}/custom-scripts** - Custom script'leri listelemek için

---

## 📌 Notlar

1. **Script Seçimi:**
   - Node oluştururken `script_id` (global) veya `custom_script_id` (custom) kullanılabilir
   - İkisi de sağlanmamalı veya ikisi de sağlanmamalı (tam olarak biri gerekli)
   - Custom script kullanılıyorsa, script aynı workspace'e ait olmalı

2. **Input Parameters:**
   - `input_params` script'in `input_schema`'sına göre validate edilir
   - Frontend format kullanılır (JSON object)
   - Script'in required field'ları sağlanmalıdır

3. **Form Schema:**
   - `GET /nodes/{node_id}/form-schema` endpoint'i frontend'de dinamik form oluşturmak için kullanılır
   - Script'in `input_schema`'sından türetilir
   - Node'un mevcut `input_params` değerleri ile birleştirilir

4. **Node Name:**
   - Workflow içinde benzersiz olmalıdır
   - Aynı workflow'da aynı isimde iki node olamaz

5. **Node Silme:**
   - Node silindiğinde tüm ilişkili edge'ler CASCADE olarak silinir
   - Workflow execution'ları etkilenmez (geçmiş execution'lar korunur)

6. **Retry ve Timeout:**
   - `max_retries`: Node execution başarısız olursa kaç kez tekrar deneneceği
   - `timeout_seconds`: Node execution'ın maksimum süresi (saniye)

7. **Script Types:**
   - `GLOBAL`: Sistem seviyesi script (tüm workspace'ler kullanabilir)
   - `CUSTOM`: Workspace-specific script (sadece o workspace kullanabilir)

---

**Son Güncelleme:** 2024  
**Versiyon:** 1.0

