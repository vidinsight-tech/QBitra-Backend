# Workspace Member Routes - Test Kılavuzu

## 📋 Genel Bilgiler

- **Base URL:** `{{base_url}}`
- **Prefix:** `/workspaces/{workspace_id}/members`
- **Authentication:** Tüm endpoint'ler Bearer token gerektirir
- **Content-Type:** `application/json`
- **Workspace ID Format:** `WSP-[16 haneli hexadecimal]`

---

## 1. Get Workspace Members

### 📌 Endpoint Bilgileri

- **Method:** `GET`
- **Route:** `{{base_url}}/workspaces/{{workspace_id}}/members`
- **Description:** Workspace'teki tüm üyeleri listeler

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

---

### 🌐 Route

```
GET {{base_url}}/workspaces/{{workspace_id}}/members
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
  "message": "Workspace members retrieved successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "members": [
      {
        "id": "MEM-1234567890ABCDEF",
        "workspace_id": "WSP-1234567890ABCDEF",
        "user_id": "USR-1234567890ABCDEF",
        "user": {
          "id": "USR-1234567890ABCDEF",
          "username": "john_doe",
          "email": "john.doe@example.com",
          "name": "John",
          "surname": "Doe"
        },
        "role_id": "ROL-1234567890ABCDEF",
        "role": {
          "id": "ROL-1234567890ABCDEF",
          "name": "Owner",
          "description": "Workspace owner"
        },
        "joined_at": "2024-01-01T00:00:00Z",
        "last_accessed_at": "2024-01-01T12:00:00Z",
        "custom_permissions": null
      },
      {
        "id": "MEM-FEDCBA0987654321",
        "workspace_id": "WSP-1234567890ABCDEF",
        "user_id": "USR-FEDCBA0987654321",
        "user": {
          "id": "USR-FEDCBA0987654321",
          "username": "jane_smith",
          "email": "jane.smith@example.com",
          "name": "Jane",
          "surname": "Smith"
        },
        "role_id": "ROL-FEDCBA0987654321",
        "role": {
          "id": "ROL-FEDCBA0987654321",
          "name": "Member",
          "description": "Workspace member"
        },
        "joined_at": "2024-01-02T00:00:00Z",
        "last_accessed_at": "2024-01-02T10:00:00Z",
        "custom_permissions": null
      }
    ],
    "total": 2
  }
}
```

---

## 2. Get Workspace Member

### 📌 Endpoint Bilgileri

- **Method:** `GET`
- **Route:** `{{base_url}}/workspaces/{{workspace_id}}/members/{{member_id}}`
- **Description:** Belirli bir workspace üyesinin detay bilgilerini getirir

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

---

### 🌐 Route

```
GET {{base_url}}/workspaces/{{workspace_id}}/members/{{member_id}}
```

---

### 📝 Path Variables

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `workspace_id` | string | ✅ Yes | Workspace ID'si |
| `member_id` | string | ✅ Yes | Member ID'si |

---

### 📨 Request Body

Bu endpoint request body kullanmaz.

---

### ✅ Success Response (200 OK)

```json
{
  "status": "success",
  "code": 200,
  "message": "Workspace member retrieved successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "id": "MEM-1234567890ABCDEF",
    "workspace_id": "WSP-1234567890ABCDEF",
    "user_id": "USR-1234567890ABCDEF",
    "user": {
      "id": "USR-1234567890ABCDEF",
      "username": "john_doe",
      "email": "john.doe@example.com",
      "name": "John",
      "surname": "Doe"
    },
    "role_id": "ROL-1234567890ABCDEF",
    "role": {
      "id": "ROL-1234567890ABCDEF",
      "name": "Owner",
      "description": "Workspace owner"
    },
    "joined_at": "2024-01-01T00:00:00Z",
    "last_accessed_at": "2024-01-01T12:00:00Z",
    "custom_permissions": null
  }
}
```

---

## 3. Change Member Role

### 📌 Endpoint Bilgileri

- **Method:** `PUT`
- **Route:** `{{base_url}}/workspaces/{{workspace_id}}/members/{{member_id}}/role`
- **Description:** Workspace üyesinin rolünü değiştirir

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

**Not:** Sadece workspace owner/admin'ler üye rollerini değiştirebilir.

---

### 🌐 Route

```
PUT {{base_url}}/workspaces/{{workspace_id}}/members/{{member_id}}/role
```

---

### 📝 Path Variables

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `workspace_id` | string | ✅ Yes | Workspace ID'si |
| `member_id` | string | ✅ Yes | Member ID'si |

---

### 📨 Request Body

```json
{
  "role_id": "ROL-FEDCBA0987654321"
}
```

**Body Parametreleri:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `role_id` | string | ✅ Yes | Yeni rol ID'si (Owner, Admin, Member, vb.) |

**Mevcut Roller:**
- `Owner` - Workspace sahibi (en yüksek yetki)
- `Admin` - Workspace yöneticisi
- `Member` - Normal üye

---

### ✅ Success Response (200 OK)

```json
{
  "status": "success",
  "code": 200,
  "message": "Member role updated successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "id": "MEM-1234567890ABCDEF",
    "workspace_id": "WSP-1234567890ABCDEF",
    "user_id": "USR-1234567890ABCDEF",
    "role_id": "ROL-FEDCBA0987654321",
    "role": {
      "id": "ROL-FEDCBA0987654321",
      "name": "Admin",
      "description": "Workspace administrator"
    },
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

---

### ❌ Error Responses

#### 403 Forbidden (Insufficient Permissions)

```json
{
  "status": "error",
  "code": 403,
  "message": null,
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "error_message": "Only workspace owners and admins can change member roles",
  "error_code": "INSUFFICIENT_PERMISSIONS"
}
```

---

## 4. Remove Member from Workspace

### 📌 Endpoint Bilgileri

- **Method:** `DELETE`
- **Route:** `{{base_url}}/workspaces/{{workspace_id}}/members/{{user_id}}`
- **Description:** Kullanıcıyı workspace'ten çıkarır

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

**⚠️ UYARI:** Workspace owner silinemez. Ownership transfer edilmeli veya workspace silinmeli.

---

### 🌐 Route

```
DELETE {{base_url}}/workspaces/{{workspace_id}}/members/{{user_id}}
```

---

### 📝 Path Variables

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `workspace_id` | string | ✅ Yes | Workspace ID'si |
| `user_id` | string | ✅ Yes | Çıkarılacak kullanıcı ID'si |

---

### 📨 Request Body

Bu endpoint request body kullanmaz.

---

### ✅ Success Response (200 OK)

```json
{
  "status": "success",
  "code": 200,
  "message": "Member removed from workspace successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "workspace_id": "WSP-1234567890ABCDEF",
    "user_id": "USR-FEDCBA0987654321",
    "removed_at": "2024-01-01T00:00:00Z"
  }
}
```

---

### ❌ Error Responses

#### 400 Bad Request (Cannot Remove Owner)

```json
{
  "status": "error",
  "code": 400,
  "message": null,
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "error_message": "Cannot remove workspace owner. Transfer ownership first or delete workspace.",
  "error_code": "BUSINESS_RULE_VIOLATION"
}
```

---

## 🧪 Test Senaryoları

### Senaryo 1: Workspace Üye Yönetimi

1. **Workspace üyelerini listele:**
   ```
   GET {{base_url}}/workspaces/{{workspace_id}}/members
   Headers: Authorization: Bearer {{access_token}}
   ```

2. **Belirli bir üyenin detaylarını al:**
   ```
   GET {{base_url}}/workspaces/{{workspace_id}}/members/{{member_id}}
   Headers: Authorization: Bearer {{access_token}}
   ```

3. **Üye rolünü değiştir:**
   ```
   PUT {{base_url}}/workspaces/{{workspace_id}}/members/{{member_id}}/role
   Headers: Authorization: Bearer {{access_token}}
   Body: { "role_id": "ROL-..." }
   ```

---

### Senaryo 2: Üye Çıkarma

1. **Üyeyi workspace'ten çıkar:**
   ```
   DELETE {{base_url}}/workspaces/{{workspace_id}}/members/{{user_id}}
   Headers: Authorization: Bearer {{access_token}}
   ```

**Not:** Owner çıkarılamaz.

---

### Senaryo 3: Workspace Davet Sistemi

1. **Davet gönder (workspace_invitation_routes):**
   ```
   POST {{base_url}}/workspaces/{{workspace_id}}/invitations
   Body: { "email": "newuser@example.com", "role_id": "ROL-..." }
   ```

2. **Davet kabul edildiğinde otomatik olarak üye eklenir**

3. **Üyeleri listele:**
   ```
   GET {{base_url}}/workspaces/{{workspace_id}}/members
   ```

---

## 📝 Postman/Bruno Collection Örneği

### Environment Variables

```json
{
  "base_url": "http://localhost:8000",
  "access_token": "",
  "workspace_id": "",
  "member_id": "",
  "user_id": "",
  "role_id_owner": "",
  "role_id_admin": "",
  "role_id_member": ""
}
```

---

## 🔗 İlgili Endpoint'ler

- **GET /workspaces/{{workspace_id}}** - Workspace bilgilerini almak için
- **POST /workspaces/{{workspace_id}}/invitations** - Workspace'e davet göndermek için
- **GET /users/{{user_id}}/workspaces** - Kullanıcının workspace'lerini listelemek için

---

## 📌 Notlar

1. **Workspace Owner:**
   - Workspace oluşturan kullanıcı otomatik olarak Owner rolü alır
   - Owner silinemez
   - Ownership transfer edilmeli veya workspace silinmeli

2. **Role Permissions:**
   - **Owner:** Tüm yetkilere sahiptir (workspace silme dahil)
   - **Admin:** Workspace yönetimi, üye yönetimi (owner hariç)
   - **Member:** Sınırlı yetkiler (okuma, workflow execution)

3. **Member Management:**
   - Sadece Owner ve Admin'ler üye ekleyebilir/çıkarabilir
   - Sadece Owner ve Admin'ler üye rollerini değiştirebilir

4. **Workspace Membership:**
   - Workspace oluşturulduğunda owner otomatik olarak üye eklenir
   - Davet sistemi ile yeni üyeler eklenebilir
   - Üyeler workspace'ten çıkarılabilir (owner hariç)

5. **Last Accessed At:**
   - Üyenin workspace'e son erişim zamanı otomatik olarak güncellenir
   - Her workspace-scoped request'te güncellenir

---

**Son Güncelleme:** 2024  
**Versiyon:** 1.0

