# File Routes - Test Kılavuzu

## 📋 Genel Bilgiler

- **Base URL:** `{{base_url}}`
- **Prefix:** `/workspaces/{workspace_id}/files`
- **Authentication:** Tüm endpoint'ler Bearer token gerektirir
- **Content-Type:** 
  - Upload: `multipart/form-data`
  - Diğer: `application/json`
- **Workspace ID Format:** `WSP-[16 haneli hexadecimal]`

---

## 1. Get All Files

### 📌 Endpoint Bilgileri

- **Method:** `GET`
- **Route:** `{{base_url}}/workspaces/{{workspace_id}}/files`
- **Description:** Workspace'teki tüm dosyaları pagination ile getirir

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

---

### 🌐 Route

```
GET {{base_url}}/workspaces/{{workspace_id}}/files
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
| `include_deleted` | boolean | ❌ No | false | Silinen dosyaları dahil et |

---

### 📨 Request Body

Bu endpoint request body kullanmaz.

---

### ✅ Success Response (200 OK)

```json
{
  "status": "success",
  "code": 200,
  "message": "Files retrieved successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "items": [
      {
        "id": "FIL-1234567890ABCDEF",
        "name": "document.pdf",
        "original_filename": "document.pdf",
        "description": "Important document",
        "mime_type": "application/pdf",
        "file_size_bytes": 1024000,
        "file_size_mb": 1.0,
        "file_path": "/workspaces/WSP-.../files/document.pdf",
        "tags": ["document", "important"],
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

## 2. Get File Metadata

### 📌 Endpoint Bilgileri

- **Method:** `GET`
- **Route:** `{{base_url}}/workspaces/{{workspace_id}}/files/{{file_id}}`
- **Description:** Belirli bir dosyanın metadata bilgilerini getirir

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

---

### 🌐 Route

```
GET {{base_url}}/workspaces/{{workspace_id}}/files/{{file_id}}
```

---

### 📝 Path Variables

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `workspace_id` | string | ✅ Yes | Workspace ID'si |
| `file_id` | string | ✅ Yes | File ID'si |

---

### 📨 Request Body

Bu endpoint request body kullanmaz.

---

### ✅ Success Response (200 OK)

```json
{
  "status": "success",
  "code": 200,
  "message": "File metadata retrieved successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "id": "FIL-1234567890ABCDEF",
    "name": "document.pdf",
    "original_filename": "document.pdf",
    "description": "Important document",
    "mime_type": "application/pdf",
    "file_size_bytes": 1024000,
    "file_size_mb": 1.0,
    "file_path": "/workspaces/WSP-.../files/document.pdf",
    "tags": ["document", "important"],
    "workspace_id": "WSP-1234567890ABCDEF",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "created_by": "USR-1234567890ABCDEF",
    "updated_by": null
  }
}
```

---

## 3. Download File Content

### 📌 Endpoint Bilgileri

- **Method:** `GET`
- **Route:** `{{base_url}}/workspaces/{{workspace_id}}/files/{{file_id}}/content`
- **Description:** Dosyanın içeriğini indirir

---

### 🔧 Headers

```
Authorization: Bearer {{access_token}}
```

**Not:** Content-Type header'ı gerekmez, response binary olacaktır.

---

### 🌐 Route

```
GET {{base_url}}/workspaces/{{workspace_id}}/files/{{file_id}}/content
```

---

### 📝 Path Variables

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `workspace_id` | string | ✅ Yes | Workspace ID'si |
| `file_id` | string | ✅ Yes | File ID'si |

---

### 📨 Request Body

Bu endpoint request body kullanmaz.

---

### ✅ Success Response (200 OK)

**Response Headers:**
```
Content-Type: application/pdf
Content-Disposition: attachment; filename="document.pdf"
```

**Response Body:**
- Binary file content (dosya içeriği)

---

## 4. Upload File

### 📌 Endpoint Bilgileri

- **Method:** `POST`
- **Route:** `{{base_url}}/workspaces/{{workspace_id}}/files`
- **Description:** Workspace'e yeni dosya yükler

---

### 🔧 Headers

```
Content-Type: multipart/form-data
Authorization: Bearer {{access_token}}
```

**⚠️ ÖNEMLİ:** Bu endpoint `multipart/form-data` kullanır, `application/json` değil!

---

### 🌐 Route

```
POST {{base_url}}/workspaces/{{workspace_id}}/files
```

---

### 📝 Path Variables

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `workspace_id` | string | ✅ Yes | Workspace ID'si |

---

### 📨 Request Body (multipart/form-data)

**Form Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file` | file | ✅ Yes | Yüklenecek dosya |
| `name` | string | ❌ No | Dosya adı (belirtilmezse original filename kullanılır) |
| `description` | string | ❌ No | Dosya açıklaması |
| `tags` | string | ❌ No | Virgülle ayrılmış etiketler (örn: "document,important") |

**Örnek Request (cURL):**
```bash
curl -X POST "{{base_url}}/workspaces/{{workspace_id}}/files" \
  -H "Authorization: Bearer {{access_token}}" \
  -F "file=@/path/to/document.pdf" \
  -F "name=document.pdf" \
  -F "description=Important document" \
  -F "tags=document,important"
```

**Örnek Request (Postman/Bruno):**
- Method: POST
- Body Type: form-data
- Fields:
  - `file`: [File] (Select File)
  - `name`: document.pdf (Text)
  - `description`: Important document (Text)
  - `tags`: document,important (Text)

---

### ✅ Success Response (201 Created)

```json
{
  "status": "success",
  "code": 201,
  "message": "File uploaded successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "id": "FIL-1234567890ABCDEF",
    "name": "document.pdf",
    "original_filename": "document.pdf",
    "description": "Important document",
    "mime_type": "application/pdf",
    "file_size_bytes": 1024000,
    "file_size_mb": 1.0,
    "file_path": "/workspaces/WSP-1234567890ABCDEF/files/document.pdf",
    "tags": ["document", "important"],
    "workspace_id": "WSP-1234567890ABCDEF",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "created_by": "USR-1234567890ABCDEF",
    "updated_by": null
  }
}
```

---

### ❌ Error Responses

#### 400 Bad Request (Storage Limit Exceeded)

```json
{
  "status": "error",
  "code": 400,
  "message": null,
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "error_message": "Workspace storage limit exceeded",
  "error_code": "BUSINESS_RULE_VIOLATION"
}
```

#### 400 Bad Request (File Too Large)

```json
{
  "status": "error",
  "code": 400,
  "message": null,
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "error_message": "File size exceeds maximum allowed size",
  "error_code": "INVALID_INPUT"
}
```

---

## 5. Update File Metadata

### 📌 Endpoint Bilgileri

- **Method:** `PUT`
- **Route:** `{{base_url}}/workspaces/{{workspace_id}}/files/{{file_id}}`
- **Description:** Dosya metadata'sını günceller (dosya içeriği değil)

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

---

### 🌐 Route

```
PUT {{base_url}}/workspaces/{{workspace_id}}/files/{{file_id}}
```

---

### 📝 Path Variables

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `workspace_id` | string | ✅ Yes | Workspace ID'si |
| `file_id` | string | ✅ Yes | File ID'si |

---

### 📨 Request Body

```json
{
  "name": "updated-document.pdf",
  "description": "Updated description",
  "tags": ["updated", "document"]
}
```

**Body Parametreleri (Tümü Opsiyonel):**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | ❌ No | Dosya adı (workspace içinde benzersiz olmalı) |
| `description` | string | ❌ No | Dosya açıklaması |
| `tags` | array | ❌ No | Etiketler |

**Not:** Bu endpoint sadece metadata günceller, dosya içeriğini değiştirmez.

---

### ✅ Success Response (200 OK)

```json
{
  "status": "success",
  "code": 200,
  "message": "File metadata updated successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "id": "FIL-1234567890ABCDEF",
    "name": "updated-document.pdf",
    "description": "Updated description",
    "tags": ["updated", "document"],
    "updated_at": "2024-01-01T00:00:00Z",
    "updated_by": "USR-1234567890ABCDEF"
  }
}
```

---

## 6. Delete File

### 📌 Endpoint Bilgileri

- **Method:** `DELETE`
- **Route:** `{{base_url}}/workspaces/{{workspace_id}}/files/{{file_id}}`
- **Description:** Dosyayı siler

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

**⚠️ UYARI:** Bu işlem geri alınamaz! Dosya kalıcı olarak silinir.

---

### 🌐 Route

```
DELETE {{base_url}}/workspaces/{{workspace_id}}/files/{{file_id}}
```

---

### 📝 Path Variables

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `workspace_id` | string | ✅ Yes | Workspace ID'si |
| `file_id` | string | ✅ Yes | File ID'si |

---

### 📨 Request Body

Bu endpoint request body kullanmaz.

---

### ✅ Success Response (200 OK)

```json
{
  "status": "success",
  "code": 200,
  "message": "File deleted successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "file_id": "FIL-1234567890ABCDEF",
    "deleted_at": "2024-01-01T00:00:00Z"
  }
}
```

**Not:** Dosya hem dosya sisteminden hem de veritabanından silinir. Workspace storage otomatik olarak güncellenir.

---

## 🧪 Test Senaryoları

### Senaryo 1: Dosya Yükleme ve İndirme

1. **Dosya yükle:**
   ```
   POST {{base_url}}/workspaces/{{workspace_id}}/files
   Headers: Authorization: Bearer {{access_token}}
   Body: multipart/form-data
     - file: [Select File]
     - name: document.pdf
     - description: Important document
     - tags: document,important
   ```

2. **Dosya metadata'sını al:**
   ```
   GET {{base_url}}/workspaces/{{workspace_id}}/files/{{file_id}}
   Headers: Authorization: Bearer {{access_token}}
   ```

3. **Dosyayı indir:**
   ```
   GET {{base_url}}/workspaces/{{workspace_id}}/files/{{file_id}}/content
   Headers: Authorization: Bearer {{access_token}}
   ```

---

### Senaryo 2: Dosya Metadata Güncelleme

1. **Metadata'yı güncelle:**
   ```
   PUT {{base_url}}/workspaces/{{workspace_id}}/files/{{file_id}}
   Headers: Authorization: Bearer {{access_token}}
   Body: {
     "name": "updated-name.pdf",
     "description": "Updated description",
     "tags": ["updated"]
   }
   ```

---

### Senaryo 3: Dosya Listeleme

1. **Tüm dosyaları listele:**
   ```
   GET {{base_url}}/workspaces/{{workspace_id}}/files?page=1&page_size=10
   Headers: Authorization: Bearer {{access_token}}
   ```

2. **Boyuta göre sırala:**
   ```
   GET {{base_url}}/workspaces/{{workspace_id}}/files?order_by=file_size_bytes&order_desc=true
   ```

---

## 📝 Postman/Bruno Collection Örneği

### Environment Variables

```json
{
  "base_url": "http://localhost:8000",
  "access_token": "",
  "workspace_id": "",
  "file_id": ""
}
```

### Postman Collection (Upload File)

```json
{
  "name": "Upload File",
  "request": {
    "method": "POST",
    "header": [
      {
        "key": "Authorization",
        "value": "Bearer {{access_token}}"
      }
    ],
    "body": {
      "mode": "formdata",
      "formdata": [
        {
          "key": "file",
          "type": "file",
          "src": []
        },
        {
          "key": "name",
          "value": "document.pdf",
          "type": "text"
        },
        {
          "key": "description",
          "value": "Important document",
          "type": "text"
        },
        {
          "key": "tags",
          "value": "document,important",
          "type": "text"
        }
      ]
    },
    "url": {
      "raw": "{{base_url}}/workspaces/{{workspace_id}}/files",
      "host": ["{{base_url}}"],
      "path": ["workspaces", "{{workspace_id}}", "files"]
    }
  }
}
```

---

## 🔗 İlgili Endpoint'ler

- **GET /workspaces/{{workspace_id}}/limits** - Workspace storage limitlerini kontrol etmek için
- **GET /workspaces/{{workspace_id}}** - Workspace bilgilerini almak için

---

## 📌 Notlar

1. **File Upload:**
   - `multipart/form-data` formatı kullanılmalıdır
   - `application/json` kullanılamaz
   - `file` field'ı zorunludur
   - Diğer field'lar (name, description, tags) opsiyoneldir

2. **Storage Limits:**
   - Workspace plan'ına göre storage limiti vardır
   - Dosya yükleme sırasında limit kontrolü yapılır
   - Limit aşılırsa upload reddedilir

3. **File Size:**
   - Her dosya için maksimum boyut sınırı vardır
   - Workspace plan'ına göre belirlenir
   - Büyük dosyalar reddedilir

4. **File Storage:**
   - Dosyalar workspace-specific klasörlerde saklanır
   - Path: `/workspaces/{workspace_id}/files/{filename}`
   - Dosya silindiğinde fiziksel dosya da silinir

5. **File Metadata:**
   - `name`: Workspace içinde benzersiz olmalıdır
   - `original_filename`: Yüklenen dosyanın orijinal adı
   - `mime_type`: Dosya tipi (otomatik tespit edilir)
   - `file_size_bytes`: Dosya boyutu (byte)
   - `file_size_mb`: Dosya boyutu (MB)

6. **File Download:**
   - `GET /files/{file_id}/content` endpoint'i binary response döner
   - `Content-Type` header'ı dosya tipine göre ayarlanır
   - `Content-Disposition` header'ı dosya adını içerir

7. **Tags:**
   - Upload sırasında virgülle ayrılmış string olarak gönderilir
   - Örnek: `"document,important,pdf"`
   - Sistem tarafından array'e çevrilir

8. **File Update:**
   - Sadece metadata güncellenebilir
   - Dosya içeriği değiştirilemez
   - İçeriği değiştirmek için yeni dosya yüklenmeli

---

**Son Güncelleme:** 2024  
**Versiyon:** 1.0

