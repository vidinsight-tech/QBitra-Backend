# User Routes - Test Kılavuzu

## 📋 Genel Bilgiler

- **Base URL:** `{{base_url}}`
- **Prefix:** `/users`
- **Authentication:** Çoğu endpoint Bearer token gerektirir, password reset endpoint'leri public
- **Content-Type:** `application/json`

---

## 1. Get User Profile

### 📌 Endpoint Bilgileri

- **Method:** `GET`
- **Route:** `{{base_url}}/users/{{user_id}}`
- **Description:** Kullanıcı profil bilgilerini getirir

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

---

### 🌐 Route

```
GET {{base_url}}/users/{{user_id}}
```

---

### 📝 Path Variables

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `user_id` | string | ✅ Yes | Kullanıcı ID'si (örn: USR-1234567890ABCDEF) |

---

### 📨 Request Body

Bu endpoint request body kullanmaz.

---

### ✅ Success Response (200 OK)

```json
{
  "status": "success",
  "code": 200,
  "message": "User profile retrieved successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "id": "USR-1234567890ABCDEF",
    "username": "john_doe",
    "email": "john.doe@example.com",
    "name": "John",
    "surname": "Doe",
    "is_verified": true,
    "marketing_consent": false,
    "avatar_url": null,
    "country_code": "TR",
    "phone_number": null,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

---

### ❌ Error Responses

#### 403 Forbidden (Başka kullanıcının profilini görüntüleme)

```json
{
  "status": "error",
  "code": 403,
  "message": null,
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "error_message": "You can only view your own profile",
  "error_code": "FORBIDDEN"
}
```

---

## 2. Get Active Sessions

### 📌 Endpoint Bilgileri

- **Method:** `GET`
- **Route:** `{{base_url}}/users/{{user_id}}/sessions`
- **Description:** Kullanıcının aktif oturumlarını listeler

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

---

### 🌐 Route

```
GET {{base_url}}/users/{{user_id}}/sessions
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
  "message": "Active sessions retrieved successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "sessions": [
      {
        "session_id": "SES-1234567890ABCDEF",
        "ip_address": "192.168.1.1",
        "user_agent": "Mozilla/5.0...",
        "created_at": "2024-01-01T00:00:00Z",
        "last_accessed_at": "2024-01-01T12:00:00Z"
      }
    ],
    "total": 1
  }
}
```

---

## 3. Revoke Specific Session

### 📌 Endpoint Bilgileri

- **Method:** `DELETE`
- **Route:** `{{base_url}}/users/{{user_id}}/sessions/{{session_id}}`
- **Description:** Belirli bir oturumu iptal eder

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

---

### 🌐 Route

```
DELETE {{base_url}}/users/{{user_id}}/sessions/{{session_id}}
```

---

### 📝 Path Variables

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `user_id` | string | ✅ Yes | Kullanıcı ID'si |
| `session_id` | string | ✅ Yes | Oturum ID'si |

---

### 📨 Request Body

Bu endpoint request body kullanmaz.

---

### ✅ Success Response (200 OK)

```json
{
  "status": "success",
  "code": 200,
  "message": "Session revoked successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "success": true,
    "session_id": "SES-1234567890ABCDEF"
  }
}
```

---

## 4. Get Login History

### 📌 Endpoint Bilgileri

- **Method:** `GET`
- **Route:** `{{base_url}}/users/{{user_id}}/login-history`
- **Description:** Kullanıcının giriş geçmişini listeler

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

---

### 🌐 Route

```
GET {{base_url}}/users/{{user_id}}/login-history?limit=20
```

---

### 📝 Path Variables

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `user_id` | string | ✅ Yes | Kullanıcı ID'si |

---

### 📝 Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `limit` | integer | ❌ No | 20 | Döndürülecek kayıt sayısı (1-100) |

---

### 📨 Request Body

Bu endpoint request body kullanmaz.

---

### ✅ Success Response (200 OK)

```json
{
  "status": "success",
  "code": 200,
  "message": "Login history retrieved successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "login_history": [
      {
        "id": "LOG-1234567890ABCDEF",
        "login_status": "SUCCESS",
        "login_method": "PASSWORD",
        "ip_address": "192.168.1.1",
        "user_agent": "Mozilla/5.0...",
        "created_at": "2024-01-01T00:00:00Z"
      }
    ],
    "total": 1
  }
}
```

---

## 5. Get Password History

### 📌 Endpoint Bilgileri

- **Method:** `GET`
- **Route:** `{{base_url}}/users/{{user_id}}/password-history`
- **Description:** Kullanıcının şifre değiştirme geçmişini listeler

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

---

### 🌐 Route

```
GET {{base_url}}/users/{{user_id}}/password-history?limit=10
```

---

### 📝 Path Variables

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `user_id` | string | ✅ Yes | Kullanıcı ID'si |

---

### 📝 Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `limit` | integer | ❌ No | 10 | Döndürülecek kayıt sayısı (1-50) |

---

### 📨 Request Body

Bu endpoint request body kullanmaz.

---

### ✅ Success Response (200 OK)

```json
{
  "status": "success",
  "code": 200,
  "message": "Password history retrieved successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "password_history": [
      {
        "id": "PWD-1234567890ABCDEF",
        "password_changed_at": "2024-01-01T00:00:00Z",
        "change_reason": "USER_REQUEST"
      }
    ],
    "total": 1
  }
}
```

---

## 6. Update Username

### 📌 Endpoint Bilgileri

- **Method:** `PUT`
- **Route:** `{{base_url}}/users/{{user_id}}/username`
- **Description:** Kullanıcı adını günceller

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

---

### 🌐 Route

```
PUT {{base_url}}/users/{{user_id}}/username
```

---

### 📝 Path Variables

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `user_id` | string | ✅ Yes | Kullanıcı ID'si |

---

### 📨 Request Body

```json
{
  "new_user_name": "new_username"
}
```

**Body Parametreleri:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `new_user_name` | string | ✅ Yes | Yeni kullanıcı adı (3-50 karakter) |

---

### ✅ Success Response (200 OK)

```json
{
  "status": "success",
  "code": 200,
  "message": "Username updated successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "user_id": "USR-1234567890ABCDEF",
    "username": "new_username",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

---

## 7. Update Email

### 📌 Endpoint Bilgileri

- **Method:** `PUT`
- **Route:** `{{base_url}}/users/{{user_id}}/email`
- **Description:** Email adresini günceller (doğrulama gerektirir)

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

---

### 🌐 Route

```
PUT {{base_url}}/users/{{user_id}}/email
```

---

### 📝 Path Variables

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `user_id` | string | ✅ Yes | Kullanıcı ID'si |

---

### 📨 Request Body

```json
{
  "new_email": "newemail@example.com"
}
```

**Body Parametreleri:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `new_email` | string | ✅ Yes | Yeni email adresi |

---

### ✅ Success Response (200 OK)

```json
{
  "status": "success",
  "code": 200,
  "message": "Email updated successfully. Please verify your new email address.",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "user_id": "USR-1234567890ABCDEF",
    "email": "newemail@example.com",
    "is_verified": false,
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

---

## 8. Update User Info

### 📌 Endpoint Bilgileri

- **Method:** `PATCH`
- **Route:** `{{base_url}}/users/{{user_id}}`
- **Description:** Kullanıcı profil bilgilerini günceller (avatar, name, surname, country, phone)

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

---

### 🌐 Route

```
PATCH {{base_url}}/users/{{user_id}}
```

---

### 📝 Path Variables

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `user_id` | string | ✅ Yes | Kullanıcı ID'si |

---

### 📨 Request Body

```json
{
  "avatar_url": "https://example.com/avatar.jpg",
  "name": "John",
  "surname": "Doe",
  "country_code": "TR",
  "phone_number": "+905551234567"
}
```

**Body Parametreleri (Tümü Opsiyonel):**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `avatar_url` | string | ❌ No | Avatar URL'si |
| `name` | string | ❌ No | Ad (1-100 karakter) |
| `surname` | string | ❌ No | Soyad (1-100 karakter) |
| `country_code` | string | ❌ No | Ülke kodu (ISO 3166-1 alpha-2, 2 karakter) |
| `phone_number` | string | ❌ No | Telefon numarası (max 20 karakter) |

---

### ✅ Success Response (200 OK)

```json
{
  "status": "success",
  "code": 200,
  "message": "User info updated successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "user_id": "USR-1234567890ABCDEF",
    "avatar_url": "https://example.com/avatar.jpg",
    "name": "John",
    "surname": "Doe",
    "country_code": "TR",
    "phone_number": "+905551234567",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

---

## 9. Request User Deletion

### 📌 Endpoint Bilgileri

- **Method:** `POST`
- **Route:** `{{base_url}}/users/{{user_id}}/deletion-request`
- **Description:** Hesap silme talebi oluşturur (30 günlük bekleme süresi)

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

---

### 🌐 Route

```
POST {{base_url}}/users/{{user_id}}/deletion-request
```

---

### 📝 Path Variables

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `user_id` | string | ✅ Yes | Kullanıcı ID'si |

---

### 📨 Request Body

```json
{
  "reason": "No longer using the service"
}
```

**Body Parametreleri:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `reason` | string | ✅ Yes | Hesap silme nedeni (1-500 karakter) |

---

### ✅ Success Response (200 OK)

```json
{
  "status": "success",
  "code": 200,
  "message": "Account deletion requested successfully. Your account will be deleted in 30 days unless cancelled.",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "user_id": "USR-1234567890ABCDEF",
    "deletion_requested_at": "2024-01-01T00:00:00Z",
    "scheduled_deletion_at": "2024-01-31T00:00:00Z"
  }
}
```

---

## 10. Cancel User Deletion

### 📌 Endpoint Bilgileri

- **Method:** `DELETE`
- **Route:** `{{base_url}}/users/{{user_id}}/deletion-request`
- **Description:** Bekleyen hesap silme talebini iptal eder

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

---

### 🌐 Route

```
DELETE {{base_url}}/users/{{user_id}}/deletion-request
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
  "message": "Account deletion request cancelled successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "user_id": "USR-1234567890ABCDEF",
    "deletion_cancelled_at": "2024-01-01T00:00:00Z"
  }
}
```

---

## 11. Change Password

### 📌 Endpoint Bilgileri

- **Method:** `PUT`
- **Route:** `{{base_url}}/users/{{user_id}}/password`
- **Description:** Şifreyi değiştirir (eski şifre gerektirir)

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
X-Forwarded-For: {{client_ip}} (optional)
User-Agent: {{user_agent}} (optional)
```

---

### 🌐 Route

```
PUT {{base_url}}/users/{{user_id}}/password
```

---

### 📝 Path Variables

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `user_id` | string | ✅ Yes | Kullanıcı ID'si |

---

### 📨 Request Body

```json
{
  "old_password": "OldPassword123!",
  "new_password": "NewPassword123!"
}
```

**Body Parametreleri:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `old_password` | string | ✅ Yes | Mevcut şifre |
| `new_password` | string | ✅ Yes | Yeni şifre (minimum 8 karakter) |

---

### ✅ Success Response (200 OK)

```json
{
  "status": "success",
  "code": 200,
  "message": "Password changed successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "user_id": "USR-1234567890ABCDEF",
    "password_changed_at": "2024-01-01T00:00:00Z"
  }
}
```

---

## 12. Request Password Reset (Public)

### 📌 Endpoint Bilgileri

- **Method:** `POST`
- **Route:** `{{base_url}}/users/password-reset/request`
- **Description:** Şifre sıfırlama email'i gönderir (public endpoint)

---

### 🔧 Headers

```
Content-Type: application/json
```

**Not:** Bu endpoint authentication gerektirmez (public endpoint).

---

### 🌐 Route

```
POST {{base_url}}/users/password-reset/request
```

---

### 📝 Path Variables

Bu endpoint path variable kullanmaz.

---

### 📨 Request Body

```json
{
  "email": "user@example.com"
}
```

**Body Parametreleri:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `email` | string | ✅ Yes | Şifre sıfırlama email'inin gönderileceği adres |

---

### ✅ Success Response (200 OK)

```json
{
  "status": "success",
  "code": 200,
  "message": "If an account with that email exists, a password reset link has been sent.",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "email": "user@example.com",
    "message": "Password reset email sent"
  }
}
```

**Not:** Güvenlik nedeniyle, email sistemde olsa da olmasa da aynı mesaj döner.

---

## 13. Validate Password Reset Token (Public)

### 📌 Endpoint Bilgileri

- **Method:** `POST`
- **Route:** `{{base_url}}/users/password-reset/validate`
- **Description:** Şifre sıfırlama token'ını doğrular (public endpoint)

---

### 🔧 Headers

```
Content-Type: application/json
```

**Not:** Bu endpoint authentication gerektirmez (public endpoint).

---

### 🌐 Route

```
POST {{base_url}}/users/password-reset/validate
```

---

### 📝 Path Variables

Bu endpoint path variable kullanmaz.

---

### 📨 Request Body

```json
{
  "password_reset_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Body Parametreleri:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `password_reset_token` | string | ✅ Yes | Şifre sıfırlama token'ı (email linkinden) |

---

### ✅ Success Response (200 OK)

```json
{
  "status": "success",
  "code": 200,
  "message": "Password reset token is valid",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "valid": true,
    "user_id": "USR-1234567890ABCDEF"
  }
}
```

---

## 14. Reset Password (Public)

### 📌 Endpoint Bilgileri

- **Method:** `POST`
- **Route:** `{{base_url}}/users/password-reset/reset`
- **Description:** Token kullanarak şifreyi sıfırlar (public endpoint)

---

### 🔧 Headers

```
Content-Type: application/json
X-Forwarded-For: {{client_ip}} (optional)
User-Agent: {{user_agent}} (optional)
```

**Not:** Bu endpoint authentication gerektirmez (public endpoint).

---

### 🌐 Route

```
POST {{base_url}}/users/password-reset/reset
```

---

### 📝 Path Variables

Bu endpoint path variable kullanmaz.

---

### 📨 Request Body

```json
{
  "password_reset_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "password": "NewSecurePassword123!"
}
```

**Body Parametreleri:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `password_reset_token` | string | ✅ Yes | Şifre sıfırlama token'ı |
| `password` | string | ✅ Yes | Yeni şifre (minimum 8 karakter) |

---

### ✅ Success Response (200 OK)

```json
{
  "status": "success",
  "code": 200,
  "message": "Password reset successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "user_id": "USR-1234567890ABCDEF",
    "password_reset_at": "2024-01-01T00:00:00Z"
  }
}
```

---

## 15. Get User Workspaces

### 📌 Endpoint Bilgileri

- **Method:** `GET`
- **Route:** `{{base_url}}/users/{{user_id}}/workspaces`
- **Description:** Kullanıcının sahip olduğu ve üye olduğu workspace'leri listeler

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

---

### 🌐 Route

```
GET {{base_url}}/users/{{user_id}}/workspaces
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
  "message": "User workspaces retrieved successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "owned_workspaces": [
      {
        "workspace_id": "WSP-1234567890ABCDEF",
        "name": "My Workspace",
        "slug": "my-workspace",
        "role": "Owner"
      }
    ],
    "member_workspaces": [
      {
        "workspace_id": "WSP-FEDCBA0987654321",
        "name": "Team Workspace",
        "slug": "team-workspace",
        "role": "Member"
      }
    ],
    "total": 2
  }
}
```

---

## 🧪 Test Senaryoları

### Senaryo 1: Profil Güncelleme Akışı

1. **Profil bilgilerini al:**
   ```
   GET {{base_url}}/users/{{user_id}}
   Headers: Authorization: Bearer {{access_token}}
   ```

2. **Profil bilgilerini güncelle:**
   ```
   PATCH {{base_url}}/users/{{user_id}}
   Headers: Authorization: Bearer {{access_token}}
   Body: { "name": "John", "surname": "Doe", ... }
   ```

3. **Kullanıcı adını güncelle:**
   ```
   PUT {{base_url}}/users/{{user_id}}/username
   Headers: Authorization: Bearer {{access_token}}
   Body: { "new_user_name": "new_username" }
   ```

---

### Senaryo 2: Şifre Değiştirme

1. **Şifreyi değiştir:**
   ```
   PUT {{base_url}}/users/{{user_id}}/password
   Headers: Authorization: Bearer {{access_token}}
   Body: { "old_password": "...", "new_password": "..." }
   ```

---

### Senaryo 3: Şifre Sıfırlama (Unutulan Şifre)

1. **Şifre sıfırlama talebi:**
   ```
   POST {{base_url}}/users/password-reset/request
   Body: { "email": "user@example.com" }
   ```

2. **Token'ı doğrula:**
   ```
   POST {{base_url}}/users/password-reset/validate
   Body: { "password_reset_token": "..." }
   ```

3. **Şifreyi sıfırla:**
   ```
   POST {{base_url}}/users/password-reset/reset
   Body: { "password_reset_token": "...", "password": "..." }
   ```

---

### Senaryo 4: Oturum Yönetimi

1. **Aktif oturumları listele:**
   ```
   GET {{base_url}}/users/{{user_id}}/sessions
   Headers: Authorization: Bearer {{access_token}}
   ```

2. **Belirli bir oturumu iptal et:**
   ```
   DELETE {{base_url}}/users/{{user_id}}/sessions/{{session_id}}
   Headers: Authorization: Bearer {{access_token}}
   ```

---

## 📝 Postman/Bruno Collection Örneği

### Environment Variables

```json
{
  "base_url": "http://localhost:8000",
  "access_token": "",
  "user_id": "",
  "session_id": "",
  "client_ip": "192.168.1.1",
  "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}
```

---

## 🔗 İlgili Endpoint'ler

- **POST /auth/login** - Giriş yapmak için (access_token almak için)
- **POST /auth/logout** - Oturum kapatmak için
- **GET /workspaces** - Workspace listesini görmek için

---

## 📌 Notlar

1. Tüm endpoint'ler (password reset hariç) authentication gerektirir.
2. Kullanıcılar sadece kendi bilgilerini görüntüleyebilir/güncelleyebilir (403 Forbidden).
3. Email güncelleme sonrası yeni email doğrulanmalıdır.
4. Hesap silme talebi 30 gün içinde iptal edilebilir.
5. Password reset endpoint'leri public'tir, authentication gerektirmez.
6. Şifre değiştirme ve sıfırlama işlemleri password history'ye kaydedilir.

---

**Son Güncelleme:** 2024  
**Versiyon:** 1.0

