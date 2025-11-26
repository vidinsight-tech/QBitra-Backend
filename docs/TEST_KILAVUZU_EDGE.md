# Edge Routes - Test Kılavuzu

## 📋 Genel Bilgiler

- **Base URL:** `{{base_url}}`
- **Prefix:** `/workspaces/{workspace_id}/workflows/{workflow_id}/edges`
- **Authentication:** Tüm endpoint'ler Bearer token gerektirir
- **Content-Type:** `application/json`
- **Workspace ID Format:** `WSP-[16 haneli hexadecimal]`

---

## 1. Get All Edges

### 📌 Endpoint Bilgileri

- **Method:** `GET`
- **Route:** `{{base_url}}/workspaces/{{workspace_id}}/workflows/{{workflow_id}}/edges`
- **Description:** Workflow'daki tüm edge'leri pagination ve filtreleme ile getirir

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

---

### 🌐 Route

```
GET {{base_url}}/workspaces/{{workspace_id}}/workflows/{{workflow_id}}/edges
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
| `include_deleted` | boolean | ❌ No | false | Silinen edge'leri dahil et |
| `from_node_id` | string | ❌ No | - | Kaynak node ID'sine göre filtrele |
| `to_node_id` | string | ❌ No | - | Hedef node ID'sine göre filtrele |

---

### 📨 Request Body

Bu endpoint request body kullanmaz.

---

### ✅ Success Response (200 OK)

```json
{
  "status": "success",
  "code": 200,
  "message": "Edges retrieved successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "items": [
      {
        "id": "EDG-1234567890ABCDEF",
        "from_node_id": "NOD-1234567890ABCDEF",
        "to_node_id": "NOD-FEDCBA0987654321",
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

## 2. Get Edge

### 📌 Endpoint Bilgileri

- **Method:** `GET`
- **Route:** `{{base_url}}/workspaces/{{workspace_id}}/workflows/{{workflow_id}}/edges/{{edge_id}}`
- **Description:** Belirli bir edge'in detay bilgilerini getirir

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

---

### 🌐 Route

```
GET {{base_url}}/workspaces/{{workspace_id}}/workflows/{{workflow_id}}/edges/{{edge_id}}
```

---

### 📝 Path Variables

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `workspace_id` | string | ✅ Yes | Workspace ID'si |
| `workflow_id` | string | ✅ Yes | Workflow ID'si |
| `edge_id` | string | ✅ Yes | Edge ID'si |

---

### 📨 Request Body

Bu endpoint request body kullanmaz.

---

### ✅ Success Response (200 OK)

```json
{
  "status": "success",
  "code": 200,
  "message": "Edge retrieved successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "id": "EDG-1234567890ABCDEF",
    "from_node_id": "NOD-1234567890ABCDEF",
    "from_node": {
      "id": "NOD-1234567890ABCDEF",
      "name": "Start Node",
      "script_type": "GLOBAL"
    },
    "to_node_id": "NOD-FEDCBA0987654321",
    "to_node": {
      "id": "NOD-FEDCBA0987654321",
      "name": "End Node",
      "script_type": "CUSTOM"
    },
    "workflow_id": "WFL-1234567890ABCDEF",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "created_by": "USR-1234567890ABCDEF",
    "updated_by": null
  }
}
```

---

## 3. Create Edge

### 📌 Endpoint Bilgileri

- **Method:** `POST`
- **Route:** `{{base_url}}/workspaces/{{workspace_id}}/workflows/{{workflow_id}}/edges`
- **Description:** İki node arasında yeni edge (bağlantı) oluşturur

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

---

### 🌐 Route

```
POST {{base_url}}/workspaces/{{workspace_id}}/workflows/{{workflow_id}}/edges
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
  "from_node_id": "NOD-1234567890ABCDEF",
  "to_node_id": "NOD-FEDCBA0987654321"
}
```

**Body Parametreleri:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `from_node_id` | string | ✅ Yes | Kaynak node ID'si (workflow'a ait olmalı) |
| `to_node_id` | string | ✅ Yes | Hedef node ID'si (workflow'a ait olmalı) |

**Kurallar:**
- Her iki node da aynı workflow'a ait olmalıdır
- Edge bir node'u kendisine bağlayamaz (self-loop yasak)
- Aynı iki node arasında duplicate edge olamaz

---

### ✅ Success Response (201 Created)

```json
{
  "status": "success",
  "code": 201,
  "message": "Edge created successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "id": "EDG-1234567890ABCDEF",
    "from_node_id": "NOD-1234567890ABCDEF",
    "to_node_id": "NOD-FEDCBA0987654321",
    "workflow_id": "WFL-1234567890ABCDEF",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "created_by": "USR-1234567890ABCDEF",
    "updated_by": null
  }
}
```

---

### ❌ Error Responses

#### 400 Bad Request (Self-Loop)

```json
{
  "status": "error",
  "code": 400,
  "message": null,
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "error_message": "Edge cannot connect a node to itself",
  "error_code": "BUSINESS_RULE_VIOLATION"
}
```

#### 409 Conflict (Duplicate Edge)

```json
{
  "status": "error",
  "code": 409,
  "message": null,
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "error_message": "Edge already exists between these nodes",
  "error_code": "RESOURCE_ALREADY_EXISTS"
}
```

---

## 4. Update Edge

### 📌 Endpoint Bilgileri

- **Method:** `PUT`
- **Route:** `{{base_url}}/workspaces/{{workspace_id}}/workflows/{{workflow_id}}/edges/{{edge_id}}`
- **Description:** Mevcut edge'i günceller (kaynak veya hedef node'u değiştirir)

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

---

### 🌐 Route

```
PUT {{base_url}}/workspaces/{{workspace_id}}/workflows/{{workflow_id}}/edges/{{edge_id}}
```

---

### 📝 Path Variables

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `workspace_id` | string | ✅ Yes | Workspace ID'si |
| `workflow_id` | string | ✅ Yes | Workflow ID'si |
| `edge_id` | string | ✅ Yes | Edge ID'si |

---

### 📨 Request Body

```json
{
  "from_node_id": "NOD-NEW1234567890ABCD",
  "to_node_id": "NOD-NEWFEDCBA09876543"
}
```

**Body Parametreleri (Tümü Opsiyonel):**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `from_node_id` | string | ❌ No | Yeni kaynak node ID'si (workflow'a ait olmalı) |
| `to_node_id` | string | ❌ No | Yeni hedef node ID'si (workflow'a ait olmalı) |

**Kurallar:**
- Her iki node da aynı workflow'a ait olmalıdır
- Edge bir node'u kendisine bağlayamaz (self-loop yasak)
- Güncellenmiş edge duplicate olmamalıdır

---

### ✅ Success Response (200 OK)

```json
{
  "status": "success",
  "code": 200,
  "message": "Edge updated successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "id": "EDG-1234567890ABCDEF",
    "from_node_id": "NOD-NEW1234567890ABCD",
    "to_node_id": "NOD-NEWFEDCBA09876543",
    "updated_at": "2024-01-01T00:00:00Z",
    "updated_by": "USR-1234567890ABCDEF"
  }
}
```

---

## 5. Delete Edge

### 📌 Endpoint Bilgileri

- **Method:** `DELETE`
- **Route:** `{{base_url}}/workspaces/{{workspace_id}}/workflows/{{workflow_id}}/edges/{{edge_id}}`
- **Description:** Edge'i siler

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

**⚠️ UYARI:** Bu işlem geri alınamaz! Edge kalıcı olarak silinir.

---

### 🌐 Route

```
DELETE {{base_url}}/workspaces/{{workspace_id}}/workflows/{{workflow_id}}/edges/{{edge_id}}
```

---

### 📝 Path Variables

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `workspace_id` | string | ✅ Yes | Workspace ID'si |
| `workflow_id` | string | ✅ Yes | Workflow ID'si |
| `edge_id` | string | ✅ Yes | Edge ID'si |

---

### 📨 Request Body

Bu endpoint request body kullanmaz.

---

### ✅ Success Response (200 OK)

```json
{
  "status": "success",
  "code": 200,
  "message": "Edge deleted successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "edge_id": "EDG-1234567890ABCDEF",
    "deleted_at": "2024-01-01T00:00:00Z"
  }
}
```

---

## 🧪 Test Senaryoları

### Senaryo 1: Workflow Grafiği Oluşturma

1. **Workflow oluştur:**
   ```
   POST {{base_url}}/workspaces/{{workspace_id}}/workflows
   Body: { "name": "My Workflow", ... }
   ```

2. **Node'ları oluştur:**
   ```
   POST {{base_url}}/workspaces/{{workspace_id}}/workflows/{{workflow_id}}/nodes
   Body: { "name": "Start Node", "script_id": "SCR-...", ... }
   
   POST {{base_url}}/workspaces/{{workspace_id}}/workflows/{{workflow_id}}/nodes
   Body: { "name": "Process Node", "script_id": "SCR-...", ... }
   
   POST {{base_url}}/workspaces/{{workspace_id}}/workflows/{{workflow_id}}/nodes
   Body: { "name": "End Node", "script_id": "SCR-...", ... }
   ```

3. **Edge'leri oluştur:**
   ```
   POST {{base_url}}/workspaces/{{workspace_id}}/workflows/{{workflow_id}}/edges
   Body: { "from_node_id": "NOD-START", "to_node_id": "NOD-PROCESS" }
   
   POST {{base_url}}/workspaces/{{workspace_id}}/workflows/{{workflow_id}}/edges
   Body: { "from_node_id": "NOD-PROCESS", "to_node_id": "NOD-END" }
   ```

4. **Workflow grafiğini görüntüle:**
   ```
   GET {{base_url}}/workspaces/{{workspace_id}}/workflows/{{workflow_id}}/edges
   ```

---

### Senaryo 2: Edge Filtreleme

1. **Belirli bir node'dan çıkan edge'leri getir:**
   ```
   GET {{base_url}}/workspaces/{{workspace_id}}/workflows/{{workflow_id}}/edges?from_node_id={{node_id}}
   ```

2. **Belirli bir node'a giren edge'leri getir:**
   ```
   GET {{base_url}}/workspaces/{{workspace_id}}/workflows/{{workflow_id}}/edges?to_node_id={{node_id}}
   ```

---

### Senaryo 3: Edge Güncelleme

1. **Edge'in hedef node'unu değiştir:**
   ```
   PUT {{base_url}}/workspaces/{{workspace_id}}/workflows/{{workflow_id}}/edges/{{edge_id}}
   Body: { "to_node_id": "NOD-NEW-TARGET" }
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
  "edge_id": "",
  "from_node_id": "",
  "to_node_id": ""
}
```

---

## 🔗 İlgili Endpoint'ler

- **POST /workspaces/{{workspace_id}}/workflows/{{workflow_id}}/nodes** - Node oluşturmak için
- **GET /workspaces/{{workspace_id}}/workflows/{{workflow_id}}/nodes** - Node'ları listelemek için
- **GET /workspaces/{{workspace_id}}/workflows/{{workflow_id}}** - Workflow detaylarını almak için

---

## 📌 Notlar

1. **Edge Yapısı:**
   - Edge'ler workflow'larda node'lar arası bağlantıları temsil eder
   - Her edge bir kaynak node (`from_node_id`) ve bir hedef node (`to_node_id`) içerir
   - Edge'ler workflow execution sırasında node'ların çalıştırılma sırasını belirler

2. **Edge Kuralları:**
   - **Self-Loop Yasak:** Bir node kendisine bağlanamaz (`from_node_id` != `to_node_id`)
   - **Duplicate Yasak:** Aynı iki node arasında birden fazla edge olamaz
   - **Workflow Kısıtı:** Her iki node da aynı workflow'a ait olmalıdır

3. **Workflow Grafiği:**
   - Edge'ler workflow'un yürütme grafiğini oluşturur
   - Execution sırasında node'lar edge'lere göre sırayla çalıştırılır
   - Döngüler (cycles) mümkündür (dikkatli kullanılmalı)

4. **Edge Silme:**
   - Edge silindiğinde node'lar silinmez
   - Sadece bağlantı kaldırılır
   - Node silindiğinde tüm ilişkili edge'ler CASCADE olarak silinir

5. **Edge Filtreleme:**
   - `from_node_id` ile kaynak node'a göre filtreleme
   - `to_node_id` ile hedef node'a göre filtreleme
   - Her iki parametre birlikte kullanılabilir

6. **Workflow Execution:**
   - Edge'ler execution sırasında kullanılır
   - Bir node tamamlandığında, o node'dan çıkan edge'lere göre sonraki node'lar çalıştırılır
   - Paralel execution mümkündür (birden fazla edge aynı node'dan çıkıyorsa)

---

**Son Güncelleme:** 2024  
**Versiyon:** 1.0

