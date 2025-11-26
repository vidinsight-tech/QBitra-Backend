# Global Script Routes - Test Kılavuzu

## 📋 Genel Bilgiler

- **Base URL:** `{{base_url}}`
- **Prefix:** `/scripts`
- **Authentication:** 
  - GET endpoint'leri public (authentication gerekmez)
  - POST, PUT, DELETE endpoint'leri Bearer token gerektirir
- **Content-Type:** `application/json`

---

## 1. Get All Global Scripts

### 📌 Endpoint Bilgileri

- **Method:** `GET`
- **Route:** `{{base_url}}/scripts`
- **Description:** Tüm global script'leri pagination ve filtreleme ile getirir

---

### 🔧 Headers

```
Content-Type: application/json
```

**Not:** Bu endpoint authentication gerektirmez (public endpoint).

---

### 🌐 Route

```
GET {{base_url}}/scripts
```

---

### 📝 Path Variables

Bu endpoint path variable kullanmaz.

---

### 📝 Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `page` | integer | ❌ No | 1 | Sayfa numarası (min: 1) |
| `page_size` | integer | ❌ No | 100 | Sayfa başına kayıt sayısı (1-1000) |
| `order_by` | string | ❌ No | created_at | Sıralama alanı |
| `order_desc` | boolean | ❌ No | false | Azalan sıralama |
| `include_deleted` | boolean | ❌ No | false | Silinen script'leri dahil et |
| `category` | string | ❌ No | - | Kategoriye göre filtrele |
| `subcategory` | string | ❌ No | - | Alt kategoriye göre filtrele |

---

### 📨 Request Body

Bu endpoint request body kullanmaz.

---

### ✅ Success Response (200 OK)

```json
{
  "status": "success",
  "code": 200,
  "message": "Global scripts retrieved successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "items": [
      {
        "id": "SCR-1234567890ABCDEF",
        "name": "Data Processor",
        "category": "data",
        "subcategory": "transformation",
        "description": "Processes and transforms data",
        "tags": ["data", "processing"],
        "documentation_url": "https://docs.example.com/scripts/data-processor",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
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

**Not:** Bu endpoint sadece metadata döner, script content içermez.

---

## 2. Get Global Script

### 📌 Endpoint Bilgileri

- **Method:** `GET`
- **Route:** `{{base_url}}/scripts/{{script_id}}`
- **Description:** Belirli bir global script'in metadata bilgilerini getirir

---

### 🔧 Headers

```
Content-Type: application/json
```

**Not:** Bu endpoint authentication gerektirmez (public endpoint).

---

### 🌐 Route

```
GET {{base_url}}/scripts/{{script_id}}
```

---

### 📝 Path Variables

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `script_id` | string | ✅ Yes | Script ID'si |

---

### 📨 Request Body

Bu endpoint request body kullanmaz.

---

### ✅ Success Response (200 OK)

```json
{
  "status": "success",
  "code": 200,
  "message": "Global script retrieved successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "id": "SCR-1234567890ABCDEF",
    "name": "Data Processor",
    "category": "data",
    "subcategory": "transformation",
    "description": "Processes and transforms data",
    "tags": ["data", "processing"],
    "documentation_url": "https://docs.example.com/scripts/data-processor",
    "required_packages": ["pandas", "numpy"],
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

**Not:** Bu endpoint sadece metadata döner, script content içermez. Content için `/scripts/{script_id}/content` endpoint'ini kullanın.

---

## 3. Get Script Content

### 📌 Endpoint Bilgileri

- **Method:** `GET`
- **Route:** `{{base_url}}/scripts/{{script_id}}/content`
- **Description:** Script içeriğini, input schema ve output schema'yı getirir

---

### 🔧 Headers

```
Content-Type: application/json
```

**Not:** Bu endpoint authentication gerektirmez (public endpoint).

---

### 🌐 Route

```
GET {{base_url}}/scripts/{{script_id}}/content
```

---

### 📝 Path Variables

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `script_id` | string | ✅ Yes | Script ID'si |

---

### 📨 Request Body

Bu endpoint request body kullanmaz.

---

### ✅ Success Response (200 OK)

```json
{
  "status": "success",
  "code": 200,
  "message": "Script content retrieved successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "id": "SCR-1234567890ABCDEF",
    "name": "Data Processor",
    "content": "def process_data(data, format='json'):\n    # Process data\n    return processed_data",
    "input_schema": {
      "type": "object",
      "properties": {
        "data": {
          "type": "string",
          "description": "Input data"
        },
        "format": {
          "type": "string",
          "enum": ["json", "xml", "csv"],
          "default": "json"
        }
      },
      "required": ["data"]
    },
    "output_schema": {
      "type": "object",
      "properties": {
        "processed_data": {
          "type": "string"
        }
      }
    }
  }
}
```

---

## 4. Create Global Script

### 📌 Endpoint Bilgileri

- **Method:** `POST`
- **Route:** `{{base_url}}/scripts`
- **Description:** Yeni global script oluşturur

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

---

### 🌐 Route

```
POST {{base_url}}/scripts
```

---

### 📝 Path Variables

Bu endpoint path variable kullanmaz.

---

### 📨 Request Body

```json
{
  "name": "Data Processor",
  "category": "data",
  "subcategory": "transformation",
  "description": "Processes and transforms data",
  "content": "def process_data(data, format='json'):\n    # Process data\n    return processed_data",
  "script_metadata": {
    "version": "1.0.0",
    "author": "System"
  },
  "required_packages": ["pandas", "numpy"],
  "input_schema": {
    "type": "object",
    "properties": {
      "data": {
        "type": "string",
        "description": "Input data"
      },
      "format": {
        "type": "string",
        "enum": ["json", "xml", "csv"],
        "default": "json"
      }
    },
    "required": ["data"]
  },
  "output_schema": {
    "type": "object",
    "properties": {
      "processed_data": {
        "type": "string"
      }
    }
  },
  "tags": ["data", "processing"],
  "documentation_url": "https://docs.example.com/scripts/data-processor"
}
```

**Body Parametreleri:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | ✅ Yes | Script adı (global olarak benzersiz olmalı) |
| `category` | string | ✅ Yes | Script kategorisi |
| `description` | string | ❌ No | Script açıklaması |
| `subcategory` | string | ❌ No | Script alt kategorisi |
| `content` | string | ✅ Yes | Script içeriği (Python kodu) |
| `script_metadata` | object | ❌ No | Script metadata |
| `required_packages` | array | ❌ No | Gerekli Python paketleri |
| `input_schema` | object | ❌ No | Input validation schema (JSON Schema format) |
| `output_schema` | object | ❌ No | Output validation schema (JSON Schema format) |
| `tags` | array | ❌ No | Etiketler |
| `documentation_url` | string | ❌ No | Dokümantasyon URL'si |

---

### ✅ Success Response (201 Created)

```json
{
  "status": "success",
  "code": 201,
  "message": "Global script created successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "id": "SCR-1234567890ABCDEF",
    "name": "Data Processor",
    "category": "data",
    "subcategory": "transformation",
    "description": "Processes and transforms data",
    "tags": ["data", "processing"],
    "documentation_url": "https://docs.example.com/scripts/data-processor",
    "required_packages": ["pandas", "numpy"],
    "file_path": "/scripts/SCR-1234567890ABCDEF.py",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

**Not:** Script dosyası otomatik olarak oluşturulur ve saklanır.

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
  "error_message": "Script with this name already exists",
  "error_code": "RESOURCE_ALREADY_EXISTS"
}
```

---

## 5. Update Global Script

### 📌 Endpoint Bilgileri

- **Method:** `PUT`
- **Route:** `{{base_url}}/scripts/{{script_id}}`
- **Description:** Global script metadata'sını günceller (script content değil)

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

---

### 🌐 Route

```
PUT {{base_url}}/scripts/{{script_id}}
```

---

### 📝 Path Variables

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `script_id` | string | ✅ Yes | Script ID'si |

---

### 📨 Request Body

```json
{
  "description": "Updated description",
  "tags": ["updated", "data", "processing"],
  "documentation_url": "https://docs.example.com/scripts/data-processor-v2"
}
```

**Body Parametreleri (Tümü Opsiyonel):**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `description` | string | ❌ No | Script açıklaması |
| `tags` | array | ❌ No | Etiketler |
| `documentation_url` | string | ❌ No | Dokümantasyon URL'si |

**Not:** Bu endpoint sadece metadata günceller, script content'i değiştirmez.

---

### ✅ Success Response (200 OK)

```json
{
  "status": "success",
  "code": 200,
  "message": "Global script updated successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "id": "SCR-1234567890ABCDEF",
    "description": "Updated description",
    "tags": ["updated", "data", "processing"],
    "documentation_url": "https://docs.example.com/scripts/data-processor-v2",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

---

## 6. Delete Global Script

### 📌 Endpoint Bilgileri

- **Method:** `DELETE`
- **Route:** `{{base_url}}/scripts/{{script_id}}`
- **Description:** Global script'i siler

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

**⚠️ UYARI:** Bu işlem geri alınamaz! Script kalıcı olarak silinir.

---

### 🌐 Route

```
DELETE {{base_url}}/scripts/{{script_id}}
```

---

### 📝 Path Variables

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `script_id` | string | ✅ Yes | Script ID'si |

---

### 📨 Request Body

Bu endpoint request body kullanmaz.

---

### ✅ Success Response (200 OK)

```json
{
  "status": "success",
  "code": 200,
  "message": "Global script deleted successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "script_id": "SCR-1234567890ABCDEF",
    "deleted_at": "2024-01-01T00:00:00Z"
  }
}
```

**Not:** Script dosyası hem dosya sisteminden hem de veritabanından silinir.

---

## 🧪 Test Senaryoları

### Senaryo 1: Global Script Oluşturma ve Kullanma

1. **Global script oluştur:**
   ```
   POST {{base_url}}/scripts
   Headers: Authorization: Bearer {{access_token}}
   Body: {
     "name": "Data Processor",
     "category": "data",
     "content": "def process_data(data):\n    return data.upper()",
     "input_schema": { ... },
     "output_schema": { ... }
   }
   ```

2. **Script metadata'sını al:**
   ```
   GET {{base_url}}/scripts/{{script_id}}
   ```

3. **Script content'ini al:**
   ```
   GET {{base_url}}/scripts/{{script_id}}/content
   ```

4. **Node oluştururken kullan:**
   ```
   POST {{base_url}}/workspaces/{{workspace_id}}/workflows/{{workflow_id}}/nodes
   Body: {
     "name": "Process Node",
     "script_id": "SCR-...",
     "input_params": { ... }
   }
   ```

---

### Senaryo 2: Script Filtreleme

1. **Kategoriye göre filtrele:**
   ```
   GET {{base_url}}/scripts?category=data
   ```

2. **Alt kategoriye göre filtrele:**
   ```
   GET {{base_url}}/scripts?category=data&subcategory=transformation
   ```

---

### Senaryo 3: Script Metadata Güncelleme

1. **Metadata'yı güncelle:**
   ```
   PUT {{base_url}}/scripts/{{script_id}}
   Headers: Authorization: Bearer {{access_token}}
   Body: {
     "description": "Updated description",
     "tags": ["updated"]
   }
   ```

---

## 📝 Postman/Bruno Collection Örneği

### Environment Variables

```json
{
  "base_url": "http://localhost:8000",
  "access_token": "",
  "script_id": ""
}
```

---

## 🔗 İlgili Endpoint'ler

- **POST /workspaces/{{workspace_id}}/workflows/{{workflow_id}}/nodes** - Node oluştururken global script kullanmak için
- **GET /workspaces/{{workspace_id}}/custom-scripts** - Custom script'leri listelemek için

---

## 📌 Notlar

1. **Global Script:**
   - Tüm workspace'ler tarafından kullanılabilir
   - Workspace-specific değildir
   - Sistem seviyesi script'lerdir

2. **Script Content:**
   - Python kodu olarak saklanır
   - Script dosyası otomatik olarak oluşturulur
   - File path: `/scripts/{script_id}.py`

3. **Input/Output Schema:**
   - JSON Schema formatında tanımlanır
   - Node oluştururken input validation için kullanılır
   - Frontend'de dinamik form oluşturmak için kullanılır

4. **Script Name:**
   - Global olarak benzersiz olmalıdır
   - Category/subcategory kombinasyonu içinde de benzersiz olmalıdır

5. **Required Packages:**
   - Script'in çalışması için gerekli Python paketleri
   - Node execution sırasında bu paketler yüklenir

6. **Public Endpoints:**
   - GET endpoint'leri public'tir (authentication gerekmez)
   - Script'leri herkes görebilir ve kullanabilir
   - POST, PUT, DELETE endpoint'leri authentication gerektirir

7. **Script Update:**
   - Sadece metadata güncellenebilir
   - Script content güncellenemez (yeni script oluşturulmalı)

8. **Script Usage:**
   - Global script'ler workflow node'larında kullanılabilir
   - Node oluştururken `script_id` parametresi ile referans edilir
   - Input schema'ya göre input parametreleri validate edilir

9. **Categories:**
   - Script'ler kategori ve alt kategori ile organize edilir
   - Filtreleme için kullanılır
   - Örnek kategoriler: data, api, file, database, vb.

---

**Son Güncelleme:** 2024  
**Versiyon:** 1.0

