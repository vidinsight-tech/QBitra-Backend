# Workspace Invitation Routes - Test Kılavuzu

## 📋 Genel Bilgiler

- **Base URL:** `{{base_url}}`
- **Prefix:** `/workspaces/{workspace_id}/invitations` ve `/invitations`
- **Authentication:** Tüm endpoint'ler Bearer token gerektirir
- **Content-Type:** `application/json`
- **Workspace ID Format:** `WSP-[16 haneli hexadecimal]`

---

## 1. Get User Pending Invitations

### 📌 Endpoint Bilgileri

- **Method:** `GET`
- **Route:** `{{base_url}}/users/{{user_id}}/invitations/pending`
- **Description:** Kullanıcının bekleyen workspace davetlerini getirir

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

---

### 🌐 Route

```
GET {{base_url}}/users/{{user_id}}/invitations/pending
```

---

### 📝 Path Variables

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `user_id` | string | ✅ Yes | Kullanıcı ID'si |

---

### 📨 Request Body

Bu endpoint request body kullanmaz.

---

### ✅ Success Response (200 OK)

```json
{
  "status": "success",
  "code": 200,
  "message": "Pending invitations retrieved successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": [
    {
      "id": "INV-1234567890ABCDEF",
      "workspace_id": "WSP-1234567890ABCDEF",
      "workspace": {
        "id": "WSP-1234567890ABCDEF",
        "name": "My Workspace",
        "slug": "my-workspace"
      },
      "user_id": "USR-1234567890ABCDEF",
      "role_id": "ROL-1234567890ABCDEF",
      "role": {
        "id": "ROL-1234567890ABCDEF",
        "name": "Member",
        "description": "Workspace member"
      },
      "status": "PENDING",
      "message": "Join our workspace!",
      "invited_by": "USR-FEDCBA0987654321",
      "inviter": {
        "id": "USR-FEDCBA0987654321",
        "username": "admin_user",
        "email": "admin@example.com"
      },
      "created_at": "2024-01-01T00:00:00Z",
      "expires_at": "2024-01-08T00:00:00Z"
    }
  ]
}
```

---

### ❌ Error Responses

#### 403 Forbidden (Başka kullanıcının davetlerini görüntüleme)

```json
{
  "status": "error",
  "code": 403,
  "message": null,
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "error_message": "You can only view your own invitations",
  "error_code": "FORBIDDEN"
}
```

---

## 2. Get Workspace Invitations

### 📌 Endpoint Bilgileri

- **Method:** `GET`
- **Route:** `{{base_url}}/workspaces/{{workspace_id}}/invitations`
- **Description:** Workspace'in tüm davetlerini getirir (pending, accepted, declined, cancelled)

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

---

### 🌐 Route

```
GET {{base_url}}/workspaces/{{workspace_id}}/invitations
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
  "message": "Workspace invitations retrieved successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "invitations": [
      {
        "id": "INV-1234567890ABCDEF",
        "workspace_id": "WSP-1234567890ABCDEF",
        "user_id": "USR-1234567890ABCDEF",
        "user": {
          "id": "USR-1234567890ABCDEF",
          "username": "john_doe",
          "email": "john.doe@example.com"
        },
        "role_id": "ROL-1234567890ABCDEF",
        "role": {
          "id": "ROL-1234567890ABCDEF",
          "name": "Member",
          "description": "Workspace member"
        },
        "status": "PENDING",
        "message": "Join our workspace!",
        "invited_by": "USR-FEDCBA0987654321",
        "inviter": {
          "id": "USR-FEDCBA0987654321",
          "username": "admin_user",
          "email": "admin@example.com"
        },
        "created_at": "2024-01-01T00:00:00Z",
        "accepted_at": null,
        "declined_at": null,
        "cancelled_at": null,
        "expires_at": "2024-01-08T00:00:00Z"
      },
      {
        "id": "INV-FEDCBA0987654321",
        "workspace_id": "WSP-1234567890ABCDEF",
        "user_id": "USR-FEDCBA0987654321",
        "status": "ACCEPTED",
        "accepted_at": "2024-01-02T00:00:00Z",
        "expires_at": null
      }
    ],
    "count": 2
  }
}
```

**Invitation Status Değerleri:**
- `PENDING` - Bekleyen davet
- `ACCEPTED` - Kabul edilmiş davet
- `DECLINED` - Reddedilmiş davet
- `CANCELLED` - İptal edilmiş davet
- `EXPIRED` - Süresi dolmuş davet

---

## 3. Invite User to Workspace

### 📌 Endpoint Bilgileri

- **Method:** `POST`
- **Route:** `{{base_url}}/workspaces/{{workspace_id}}/invitations`
- **Description:** Kullanıcıyı workspace'e davet eder

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

**Not:** Sadece workspace owner/admin'ler davet gönderebilir.

---

### 🌐 Route

```
POST {{base_url}}/workspaces/{{workspace_id}}/invitations
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
  "user_id": "USR-1234567890ABCDEF",
  "role_id": "ROL-1234567890ABCDEF",
  "message": "Join our workspace! We'd love to have you."
}
```

**Body Parametreleri:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_id` | string | ✅ Yes | Davet edilecek kullanıcı ID'si |
| `role_id` | string | ✅ Yes | Davet için rol ID'si (Owner, Admin, Member) |
| `message` | string | ❌ No | Opsiyonel davet mesajı |

---

### ✅ Success Response (201 Created)

```json
{
  "status": "success",
  "code": 201,
  "message": "User invited successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "id": "INV-1234567890ABCDEF",
    "workspace_id": "WSP-1234567890ABCDEF",
    "workspace": {
      "id": "WSP-1234567890ABCDEF",
      "name": "My Workspace",
      "slug": "my-workspace"
    },
    "user_id": "USR-1234567890ABCDEF",
    "user": {
      "id": "USR-1234567890ABCDEF",
      "username": "john_doe",
      "email": "john.doe@example.com"
    },
    "role_id": "ROL-1234567890ABCDEF",
    "role": {
      "id": "ROL-1234567890ABCDEF",
      "name": "Member",
      "description": "Workspace member"
    },
    "status": "PENDING",
    "message": "Join our workspace! We'd love to have you.",
    "invited_by": "USR-FEDCBA0987654321",
    "created_at": "2024-01-01T00:00:00Z",
    "expires_at": "2024-01-08T00:00:00Z"
  }
}
```

**Not:** Davet otomatik olarak 7 gün sonra expire olur.

---

### ❌ Error Responses

#### 409 Conflict (User Already Invited)

```json
{
  "status": "error",
  "code": 409,
  "message": null,
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "error_message": "User already has a pending invitation to this workspace",
  "error_code": "RESOURCE_ALREADY_EXISTS"
}
```

#### 409 Conflict (User Already Member)

```json
{
  "status": "error",
  "code": 409,
  "message": null,
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "error_message": "User is already a member of this workspace",
  "error_code": "RESOURCE_ALREADY_EXISTS"
}
```

---

## 4. Accept Invitation

### 📌 Endpoint Bilgileri

- **Method:** `POST`
- **Route:** `{{base_url}}/invitations/{{invitation_id}}/accept`
- **Description:** Workspace davetini kabul eder

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

---

### 🌐 Route

```
POST {{base_url}}/invitations/{{invitation_id}}/accept
```

---

### 📝 Path Variables

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `invitation_id` | string | ✅ Yes | Invitation ID'si |

---

### 📨 Request Body

Bu endpoint request body kullanmaz.

---

### ✅ Success Response (200 OK)

```json
{
  "status": "success",
  "code": 200,
  "message": "Invitation accepted successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "id": "INV-1234567890ABCDEF",
    "workspace_id": "WSP-1234567890ABCDEF",
    "workspace": {
      "id": "WSP-1234567890ABCDEF",
      "name": "My Workspace",
      "slug": "my-workspace"
    },
    "user_id": "USR-1234567890ABCDEF",
    "role_id": "ROL-1234567890ABCDEF",
    "status": "ACCEPTED",
    "accepted_at": "2024-01-01T00:00:00Z",
    "member_id": "MEM-1234567890ABCDEF"
  }
}
```

**Not:** Davet kabul edildiğinde kullanıcı otomatik olarak workspace üyesi olur ve `member_id` döner.

---

### ❌ Error Responses

#### 400 Bad Request (Invitation Already Accepted)

```json
{
  "status": "error",
  "code": 400,
  "message": null,
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "error_message": "Invitation has already been accepted",
  "error_code": "BUSINESS_RULE_VIOLATION"
}
```

#### 400 Bad Request (Invitation Expired)

```json
{
  "status": "error",
  "code": 400,
  "message": null,
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "error_message": "Invitation has expired",
  "error_code": "BUSINESS_RULE_VIOLATION"
}
```

---

## 5. Decline Invitation

### 📌 Endpoint Bilgileri

- **Method:** `POST`
- **Route:** `{{base_url}}/invitations/{{invitation_id}}/decline`
- **Description:** Workspace davetini reddeder

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

---

### 🌐 Route

```
POST {{base_url}}/invitations/{{invitation_id}}/decline
```

---

### 📝 Path Variables

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `invitation_id` | string | ✅ Yes | Invitation ID'si |

---

### 📨 Request Body

Bu endpoint request body kullanmaz.

---

### ✅ Success Response (200 OK)

```json
{
  "status": "success",
  "code": 200,
  "message": "Invitation declined successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "id": "INV-1234567890ABCDEF",
    "workspace_id": "WSP-1234567890ABCDEF",
    "user_id": "USR-1234567890ABCDEF",
    "status": "DECLINED",
    "declined_at": "2024-01-01T00:00:00Z"
  }
}
```

---

## 6. Cancel Invitation

### 📌 Endpoint Bilgileri

- **Method:** `DELETE`
- **Route:** `{{base_url}}/invitations/{{invitation_id}}`
- **Description:** Workspace davetini iptal eder (sadece davet gönderen kişi)

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

**Not:** Sadece daveti gönderen kişi (inviter) daveti iptal edebilir.

---

### 🌐 Route

```
DELETE {{base_url}}/invitations/{{invitation_id}}
```

---

### 📝 Path Variables

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `invitation_id` | string | ✅ Yes | Invitation ID'si |

---

### 📨 Request Body

Bu endpoint request body kullanmaz.

---

### ✅ Success Response (200 OK)

```json
{
  "status": "success",
  "code": 200,
  "message": "Invitation cancelled successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "id": "INV-1234567890ABCDEF",
    "workspace_id": "WSP-1234567890ABCDEF",
    "user_id": "USR-1234567890ABCDEF",
    "status": "CANCELLED",
    "cancelled_at": "2024-01-01T00:00:00Z",
    "cancelled_by": "USR-FEDCBA0987654321"
  }
}
```

---

### ❌ Error Responses

#### 403 Forbidden (Not the Inviter)

```json
{
  "status": "error",
  "code": 403,
  "message": null,
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "error_message": "Only the user who created the invitation can cancel it",
  "error_code": "FORBIDDEN"
}
```

---

## 🧪 Test Senaryoları

### Senaryo 1: Tam Davet Akışı

1. **Kullanıcıyı workspace'e davet et:**
   ```
   POST {{base_url}}/workspaces/{{workspace_id}}/invitations
   Headers: Authorization: Bearer {{access_token}}
   Body: { "user_id": "USR-...", "role_id": "ROL-...", "message": "..." }
   ```

2. **Davet edilen kullanıcı bekleyen davetlerini görüntüle:**
   ```
   GET {{base_url}}/users/{{user_id}}/invitations/pending
   Headers: Authorization: Bearer {{invited_user_access_token}}
   ```

3. **Daveti kabul et:**
   ```
   POST {{base_url}}/invitations/{{invitation_id}}/accept
   Headers: Authorization: Bearer {{invited_user_access_token}}
   ```

4. **Workspace üyelerini kontrol et:**
   ```
   GET {{base_url}}/workspaces/{{workspace_id}}/members
   Headers: Authorization: Bearer {{access_token}}
   ```

---

### Senaryo 2: Davet Reddetme

1. **Daveti reddet:**
   ```
   POST {{base_url}}/invitations/{{invitation_id}}/decline
   Headers: Authorization: Bearer {{invited_user_access_token}}
   ```

2. **Workspace davetlerini kontrol et:**
   ```
   GET {{base_url}}/workspaces/{{workspace_id}}/invitations
   Headers: Authorization: Bearer {{access_token}}
   ```
   - Status: `DECLINED` olarak görünür

---

### Senaryo 3: Davet İptal Etme

1. **Daveti iptal et (sadece inviter):**
   ```
   DELETE {{base_url}}/invitations/{{invitation_id}}
   Headers: Authorization: Bearer {{inviter_access_token}}
   ```

---

## 📝 Postman/Bruno Collection Örneği

### Environment Variables

```json
{
  "base_url": "http://localhost:8000",
  "access_token": "",
  "invited_user_access_token": "",
  "workspace_id": "",
  "user_id": "",
  "invited_user_id": "",
  "invitation_id": "",
  "role_id_member": "",
  "role_id_admin": ""
}
```

---

## 🔗 İlgili Endpoint'ler

- **GET /workspaces/{{workspace_id}}/members** - Workspace üyelerini listelemek için
- **GET /users/{{user_id}}/workspaces** - Kullanıcının workspace'lerini listelemek için
- **PUT /workspaces/{{workspace_id}}/members/{{member_id}}/role** - Üye rolünü değiştirmek için

---

## 📌 Notlar

1. **Davet Süresi:**
   - Davetler otomatik olarak 7 gün sonra expire olur
   - Expire olan davetler `EXPIRED` status'üne geçer

2. **Davet Durumları:**
   - `PENDING` - Bekleyen davet (kabul/red edilebilir)
   - `ACCEPTED` - Kabul edilmiş (kullanıcı workspace üyesi olur)
   - `DECLINED` - Reddedilmiş
   - `CANCELLED` - İptal edilmiş (inviter tarafından)
   - `EXPIRED` - Süresi dolmuş

3. **Davet Gönderme Yetkisi:**
   - Sadece workspace owner ve admin'ler davet gönderebilir
   - Normal member'lar davet gönderemez

4. **Davet İptal Yetkisi:**
   - Sadece daveti gönderen kişi (inviter) daveti iptal edebilir
   - Workspace owner/admin'ler de iptal edebilir (inviter kontrolü yapılır)

5. **Duplicate Invitation:**
   - Aynı kullanıcıya aynı workspace için birden fazla pending davet gönderilemez
   - Zaten workspace üyesi olan kullanıcıya davet gönderilemez

6. **Davet Kabul:**
   - Davet kabul edildiğinde kullanıcı otomatik olarak workspace üyesi olur
   - Belirtilen rol ile üye eklenir
   - Workspace member count artar

---

**Son Güncelleme:** 2024  
**Versiyon:** 1.0

