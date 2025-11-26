# Custom Script Routes - Test Kılavuzu

## 📋 Genel Bilgiler

- **Base URL:** `{{base_url}}`
- **Prefix:** `/workspaces/{workspace_id}/custom-scripts`
- **Authentication:** Tüm endpoint'ler Bearer token gerektirir
- **Content-Type:** `application/json`
- **Workspace ID Format:** `WSP-[16 haneli hexadecimal]`

---

## 1. Get All Custom Scripts

### 📌 Endpoint Bilgileri

- **Method:** `GET`
- **Route:** `{{base_url}}/workspaces/{{workspace_id}}/custom-scripts`
- **Description:** Workspace'teki tüm custom script'leri pagination ve filtreleme ile getirir

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

---

### 🌐 Route

```
GET {{base_url}}/workspaces/{{workspace_id}}/custom-scripts
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
| `include_deleted` | boolean | ❌ No | false | Silinen script'leri dahil et |
| `category` | string | ❌ No | - | Kategoriye göre filtrele |
| `subcategory` | string | ❌ No | - | Alt kategoriye göre filtrele |
| `approval_status` | string | ❌ No | - | Approval durumuna göre filtrele (PENDING, APPROVED, REJECTED, REVISION_NEEDED) |
| `test_status` | string | ❌ No | - | Test durumuna göre filtrele (UNTESTED, TESTING, PASSED, FAILED, PARTIAL) |

---

### 📨 Request Body

Bu endpoint request body kullanmaz.

---

### ✅ Success Response (200 OK)

```json
{
  "status": "success",
  "code": 200,
  "message": "Custom scripts retrieved successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "items": [
      {
        "id": "CUS-1234567890ABCDEF",
        "name": "Custom Data Processor",
        "category": "data",
        "subcategory": "transformation",
        "description": "Custom data processing script",
        "tags": ["custom", "data"],
        "approval_status": "PENDING",
        "test_status": "UNTESTED",
        "documentation_url": null,
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

**Not:** Bu endpoint sadece metadata döner, script content içermez.

**Approval Status Değerleri:**
- `PENDING` - Onay bekliyor
- `APPROVED` - Onaylandı (kullanılabilir)
- `REJECTED` - Reddedildi
- `REVISION_NEEDED` - Revizyon gerekli

**Test Status Değerleri:**
- `UNTESTED` - Test edilmedi
- `TESTING` - Test ediliyor
- `PASSED` - Test başarılı
- `FAILED` - Test başarısız
- `PARTIAL` - Kısmen başarılı

---

## 2. Get Custom Script

### 📌 Endpoint Bilgileri

- **Method:** `GET`
- **Route:** `{{base_url}}/workspaces/{{workspace_id}}/custom-scripts/{{custom_script_id}}`
- **Description:** Belirli bir custom script'in metadata bilgilerini getirir

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

---

### 🌐 Route

```
GET {{base_url}}/workspaces/{{workspace_id}}/custom-scripts/{{custom_script_id}}
```

---

### 📝 Path Variables

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `workspace_id` | string | ✅ Yes | Workspace ID'si |
| `custom_script_id` | string | ✅ Yes | Custom Script ID'si |

---

### 📨 Request Body

Bu endpoint request body kullanmaz.

---

### ✅ Success Response (200 OK)

```json
{
  "status": "success",
  "code": 200,
  "message": "Custom script retrieved successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "id": "CUS-1234567890ABCDEF",
    "name": "Custom Data Processor",
    "category": "data",
    "subcategory": "transformation",
    "description": "Custom data processing script",
    "tags": ["custom", "data"],
    "approval_status": "PENDING",
    "test_status": "UNTESTED",
    "required_packages": ["pandas", "numpy"],
    "documentation_url": null,
    "workspace_id": "WSP-1234567890ABCDEF",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "created_by": "USR-1234567890ABCDEF",
    "updated_by": null
  }
}
```

**Not:** Bu endpoint sadece metadata döner, script content içermez. Content için `/custom-scripts/{custom_script_id}/content` endpoint'ini kullanın.

---

## 3. Get Custom Script Content

### 📌 Endpoint Bilgileri

- **Method:** `GET`
- **Route:** `{{base_url}}/workspaces/{{workspace_id}}/custom-scripts/{{custom_script_id}}/content`
- **Description:** Script içeriğini, input schema ve output schema'yı getirir

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

---

### 🌐 Route

```
GET {{base_url}}/workspaces/{{workspace_id}}/custom-scripts/{{custom_script_id}}/content
```

---

### 📝 Path Variables

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `workspace_id` | string | ✅ Yes | Workspace ID'si |
| `custom_script_id` | string | ✅ Yes | Custom Script ID'si |

---

### 📨 Request Body

Bu endpoint request body kullanmaz.

---

### ✅ Success Response (200 OK)

```json
{
  "status": "success",
  "code": 200,
  "message": "Custom script content retrieved successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "id": "CUS-1234567890ABCDEF",
    "name": "Custom Data Processor",
    "content": "def process_data(data, format='json'):\n    # Custom processing logic\n    return processed_data",
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

## 4. Create Custom Script

### 📌 Endpoint Bilgileri

- **Method:** `POST`
- **Route:** `{{base_url}}/workspaces/{{workspace_id}}/custom-scripts`
- **Description:** Workspace için yeni custom script oluşturur

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

---

### 🌐 Route

```
POST {{base_url}}/workspaces/{{workspace_id}}/custom-scripts
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
  "name": "Custom Data Processor",
  "content": "def process_data(data, format='json'):\n    # Custom processing logic\n    return processed_data",
  "description": "Custom data processing script",
  "category": "data",
  "subcategory": "transformation",
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
  "tags": ["custom", "data"],
  "documentation_url": "https://docs.example.com/scripts/custom-processor"
}
```

**Body Parametreleri:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | ✅ Yes | Script adı (workspace içinde benzersiz olmalı) |
| `content` | string | ✅ Yes | Script içeriği (Python kodu) |
| `description` | string | ❌ No | Script açıklaması |
| `category` | string | ❌ No | Script kategorisi |
| `subcategory` | string | ❌ No | Script alt kategorisi |
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
  "message": "Custom script created successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "id": "CUS-1234567890ABCDEF",
    "name": "Custom Data Processor",
    "category": "data",
    "subcategory": "transformation",
    "description": "Custom data processing script",
    "tags": ["custom", "data"],
    "approval_status": "PENDING",
    "test_status": "UNTESTED",
    "required_packages": ["pandas", "numpy"],
    "file_path": "/workspaces/WSP-1234567890ABCDEF/custom-scripts/CUS-1234567890ABCDEF.py",
    "workspace_id": "WSP-1234567890ABCDEF",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "created_by": "USR-1234567890ABCDEF",
    "updated_by": null
  }
}
```

**Not:** 
- Script dosyası otomatik olarak oluşturulur ve saklanır
- Script başlangıçta `PENDING` approval status'ü ile oluşturulur
- Workspace custom script count otomatik olarak güncellenir

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
  "error_message": "Script with this name already exists in workspace",
  "error_code": "RESOURCE_ALREADY_EXISTS"
}
```

---

## 5. Update Custom Script

### 📌 Endpoint Bilgileri

- **Method:** `PUT`
- **Route:** `{{base_url}}/workspaces/{{workspace_id}}/custom-scripts/{{custom_script_id}}`
- **Description:** Custom script metadata'sını günceller (script content değil)

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

---

### 🌐 Route

```
PUT {{base_url}}/workspaces/{{workspace_id}}/custom-scripts/{{custom_script_id}}
```

---

### 📝 Path Variables

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `workspace_id` | string | ✅ Yes | Workspace ID'si |
| `custom_script_id` | string | ✅ Yes | Custom Script ID'si |

---

### 📨 Request Body

```json
{
  "description": "Updated description",
  "tags": ["updated", "custom", "data"],
  "documentation_url": "https://docs.example.com/scripts/custom-processor-v2"
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
  "message": "Custom script updated successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "id": "CUS-1234567890ABCDEF",
    "description": "Updated description",
    "tags": ["updated", "custom", "data"],
    "documentation_url": "https://docs.example.com/scripts/custom-processor-v2",
    "updated_at": "2024-01-01T00:00:00Z",
    "updated_by": "USR-1234567890ABCDEF"
  }
}
```

---

## 6. Delete Custom Script

### 📌 Endpoint Bilgileri

- **Method:** `DELETE`
- **Route:** `{{base_url}}/workspaces/{{workspace_id}}/custom-scripts/{{custom_script_id}}`
- **Description:** Custom script'i siler

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
DELETE {{base_url}}/workspaces/{{workspace_id}}/custom-scripts/{{custom_script_id}}
```

---

### 📝 Path Variables

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `workspace_id` | string | ✅ Yes | Workspace ID'si |
| `custom_script_id` | string | ✅ Yes | Custom Script ID'si |

---

### 📨 Request Body

Bu endpoint request body kullanmaz.

---

### ✅ Success Response (200 OK)

```json
{
  "status": "success",
  "code": 200,
  "message": "Custom script deleted successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "custom_script_id": "CUS-1234567890ABCDEF",
    "deleted_at": "2024-01-01T00:00:00Z"
  }
}
```

**Not:** Script dosyası hem dosya sisteminden hem de veritabanından silinir. Workspace custom script count otomatik olarak güncellenir.

---

## 🧪 Test Senaryoları

### Senaryo 1: Custom Script Oluşturma ve Kullanma

1. **Custom script oluştur:**
   ```
   POST {{base_url}}/workspaces/{{workspace_id}}/custom-scripts
   Headers: Authorization: Bearer {{access_token}}
   Body: {
     "name": "Custom Data Processor",
     "content": "def process_data(data):\n    return data.upper()",
     "input_schema": { ... },
     "output_schema": { ... }
   }
   ```

2. **Script metadata'sını al:**
   ```
   GET {{base_url}}/workspaces/{{workspace_id}}/custom-scripts/{{custom_script_id}}
   ```
   - Approval status: `PENDING` olmalı

3. **Script content'ini al:**
   ```
   GET {{base_url}}/workspaces/{{workspace_id}}/custom-scripts/{{custom_script_id}}/content
   ```

4. **Node oluştururken kullan:**
   ```
   POST {{base_url}}/workspaces/{{workspace_id}}/workflows/{{workflow_id}}/nodes
   Body: {
     "name": "Process Node",
     "custom_script_id": "CUS-...",
     "input_params": { ... }
   }
   ```

---

### Senaryo 2: Script Filtreleme

1. **Sadece onaylanmış script'leri getir:**
   ```
   GET {{base_url}}/workspaces/{{workspace_id}}/custom-scripts?approval_status=APPROVED
   ```

2. **Test edilmiş script'leri getir:**
   ```
   GET {{base_url}}/workspaces/{{workspace_id}}/custom-scripts?test_status=PASSED
   ```

3. **Kategoriye göre filtrele:**
   ```
   GET {{base_url}}/workspaces/{{workspace_id}}/custom-scripts?category=data
   ```

---

### Senaryo 3: Script Metadata Güncelleme

1. **Metadata'yı güncelle:**
   ```
   PUT {{base_url}}/workspaces/{{workspace_id}}/custom-scripts/{{custom_script_id}}
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
  "workspace_id": "",
  "custom_script_id": ""
}
```

---

## 🔗 İlgili Endpoint'ler

- **POST /workspaces/{{workspace_id}}/workflows/{{workflow_id}}/nodes** - Node oluştururken custom script kullanmak için
- **GET /scripts** - Global script'leri listelemek için
- **GET /workspaces/{{workspace_id}}** - Workspace bilgilerini almak için

---

## 📌 Notlar

1. **Custom Script:**
   - Workspace-specific script'lerdir
   - Sadece o workspace tarafından kullanılabilir
   - Global script'lerden farklı olarak workspace'e özeldir

2. **Approval Status:**
   - Custom script'ler onay gerektirir
   - Başlangıçta `PENDING` status'ü ile oluşturulur
   - `APPROVED` olan script'ler kullanılabilir
   - `REJECTED` veya `REVISION_NEEDED` olan script'ler kullanılamaz

3. **Test Status:**
   - Script'ler test edilebilir
   - Test durumu ayrı olarak takip edilir
   - `PASSED` olan script'ler güvenilir kabul edilir

4. **Script Content:**
   - Python kodu olarak saklanır
   - Script dosyası otomatik olarak oluşturulur
   - File path: `/workspaces/{workspace_id}/custom-scripts/{custom_script_id}.py`

5. **Input/Output Schema:**
   - JSON Schema formatında tanımlanır
   - Node oluştururken input validation için kullanılır
   - Frontend'de dinamik form oluşturmak için kullanılır

6. **Script Name:**
   - Workspace içinde benzersiz olmalıdır
   - Category/subcategory kombinasyonu içinde de benzersiz olmalıdır

7. **Required Packages:**
   - Script'in çalışması için gerekli Python paketleri
   - Node execution sırasında bu paketler yüklenir

8. **Script Update:**
   - Sadece metadata güncellenebilir
   - Script content güncellenemez (yeni script oluşturulmalı veya approval süreci gerekir)

9. **Script Usage:**
   - Custom script'ler workflow node'larında kullanılabilir
   - Node oluştururken `custom_script_id` parametresi ile referans edilir
   - Sadece `APPROVED` olan script'ler kullanılabilir

10. **Workspace Limits:**
    - Workspace plan'ına göre custom script limiti vardır
    - Limit aşılırsa yeni script oluşturulamaz
    - Workspace custom script count otomatik olarak güncellenir

11. **Security:**
    - Custom script'ler workspace bazlı izole edilir
    - Sadece workspace üyeleri custom script'leri görebilir
    - Approval süreci güvenlik için önemlidir

---

**Son Güncelleme:** 2024  
**Versiyon:** 1.0

