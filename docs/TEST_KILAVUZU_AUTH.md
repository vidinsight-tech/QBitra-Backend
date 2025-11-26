# Authentication Routes - Test Kılavuzu

## 📋 Genel Bilgiler

- **Base URL:** `{{base_url}}`
- **Prefix:** `/auth`
- **Authentication:** Çoğu endpoint public, logout/logout-all için Bearer token gerekli
- **Content-Type:** `application/json`

---

## 1. Register User

### 📌 Endpoint Bilgileri

- **Method:** `POST`
- **Route:** `{{base_url}}/auth/register`
- **Description:** Yeni kullanıcı kaydı oluşturur ve email doğrulama gönderir

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
POST {{base_url}}/auth/register
```

---

### 📝 Path Variables

Bu endpoint path variable kullanmaz.

---

### 📨 Request Body

```json
{
  "username": "john_doe",
  "email": "john.doe@example.com",
  "password": "SecurePass123!",
  "name": "John",
  "surname": "Doe",
  "marketing_consent": false,
  "terms_accepted_version": "AGR-1234567890ABCDEF",
  "privacy_policy_accepted_version": "AGR-FEDCBA0987654321"
}
```

**Body Parametreleri:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `username` | string | ✅ Yes | Kullanıcı adı (3-50 karakter) |
| `email` | string | ✅ Yes | Email adresi |
| `password` | string | ✅ Yes | Şifre (minimum 8 karakter) |
| `name` | string | ✅ Yes | Ad (1-100 karakter) |
| `surname` | string | ✅ Yes | Soyad (1-100 karakter) |
| `marketing_consent` | boolean | ❌ No | Pazarlama izni (default: false) |
| `terms_accepted_version` | string | ✅ Yes | Kullanım şartları versiyon ID'si |
| `privacy_policy_accepted_version` | string | ✅ Yes | Gizlilik politikası versiyon ID'si |

**Not:** `terms_accepted_version` ve `privacy_policy_accepted_version` değerleri `/agreements/active` endpoint'inden alınmalıdır.

---

### ✅ Success Response (201 Created)

```json
{
  "status": "success",
  "code": 201,
  "message": "User registered successfully. Please check your email for verification.",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "user_id": "USR-1234567890ABCDEF",
    "username": "john_doe",
    "email": "john.doe@example.com",
    "is_verified": false
  }
}
```

---

### ❌ Error Responses

#### 400 Bad Request (Validation Error)

```json
{
  "status": "error",
  "code": 400,
  "message": null,
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "error_message": "Password does not meet requirements: ...",
  "error_code": "INVALID_INPUT"
}
```

#### 409 Conflict (User Already Exists)

```json
{
  "status": "error",
  "code": 409,
  "message": null,
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "error_message": "User with this email already exists",
  "error_code": "RESOURCE_ALREADY_EXISTS"
}
```

---

## 2. Send Verification Email

### 📌 Endpoint Bilgileri

- **Method:** `POST`
- **Route:** `{{base_url}}/auth/send-verification-email`
- **Description:** Kullanıcıya email doğrulama linki gönderir

---

### 🔧 Headers

```
Content-Type: application/json
```

**Not:** Bu endpoint authentication gerektirmez (public endpoint).

---

### 🌐 Route

```
POST {{base_url}}/auth/send-verification-email
```

---

### 📝 Path Variables

Bu endpoint path variable kullanmaz.

---

### 📨 Request Body

```json
{
  "user_id": "USR-1234567890ABCDEF",
  "email": "john.doe@example.com"
}
```

**Body Parametreleri:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_id` | string | ✅ Yes | Kullanıcı ID'si |
| `email` | string | ✅ Yes | Doğrulama email'inin gönderileceği adres |

---

### ✅ Success Response (200 OK)

```json
{
  "status": "success",
  "code": 200,
  "message": "Verification email sent successfully. Please check your inbox.",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "user_id": "USR-1234567890ABCDEF",
    "username": "john_doe",
    "email": "john.doe@example.com",
    "is_verified": false
  }
}
```

---

## 3. Verify Email

### 📌 Endpoint Bilgileri

- **Method:** `POST`
- **Route:** `{{base_url}}/auth/verify-email`
- **Description:** Email adresini doğrulama token'ı ile doğrular

---

### 🔧 Headers

```
Content-Type: application/json
```

**Not:** Bu endpoint authentication gerektirmez (public endpoint).

---

### 🌐 Route

```
POST {{base_url}}/auth/verify-email
```

---

### 📝 Path Variables

Bu endpoint path variable kullanmaz.

---

### 📨 Request Body

```json
{
  "verification_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Body Parametreleri:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `verification_token` | string | ✅ Yes | Email doğrulama token'ı (email linkinden) |

---

### ✅ Success Response (200 OK)

```json
{
  "status": "success",
  "code": 200,
  "message": "Email verified successfully. Welcome!",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "user_id": "USR-1234567890ABCDEF",
    "username": "john_doe",
    "email": "john.doe@example.com",
    "is_verified": true
  }
}
```

---

## 4. Login

### 📌 Endpoint Bilgileri

- **Method:** `POST`
- **Route:** `{{base_url}}/auth/login`
- **Description:** Kullanıcı girişi yapar ve access/refresh token döner

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
POST {{base_url}}/auth/login
```

---

### 📝 Path Variables

Bu endpoint path variable kullanmaz.

---

### 📨 Request Body

```json
{
  "email_or_username": "john.doe@example.com",
  "password": "SecurePass123!"
}
```

**Body Parametreleri:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `email_or_username` | string | ✅ Yes | Email adresi veya kullanıcı adı |
| `password` | string | ✅ Yes | Şifre |

---

### ✅ Success Response (200 OK)

```json
{
  "status": "success",
  "code": 200,
  "message": "Login successful",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "user_id": "USR-1234567890ABCDEF",
    "username": "john_doe",
    "email": "john.doe@example.com",
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

**Önemli:** `access_token` değerini diğer authenticated endpoint'lerde `Authorization: Bearer <access_token>` header'ı olarak kullanın.

---

### ❌ Error Responses

#### 401 Unauthorized (Invalid Credentials)

```json
{
  "status": "error",
  "code": 401,
  "message": null,
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "error_message": "Invalid credentials",
  "error_code": "INVALID_CREDENTIALS"
}
```

---

## 5. Logout

### 📌 Endpoint Bilgileri

- **Method:** `POST`
- **Route:** `{{base_url}}/auth/logout`
- **Description:** Mevcut oturumu kapatır ve access token'ı iptal eder

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

**Not:** Bu endpoint authentication gerektirir (Bearer token).

---

### 🌐 Route

```
POST {{base_url}}/auth/logout
```

---

### 📝 Path Variables

Bu endpoint path variable kullanmaz.

---

### 📨 Request Body

Bu endpoint request body kullanmaz.

---

### ✅ Success Response (200 OK)

```json
{
  "status": "success",
  "code": 200,
  "message": "Logged out successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "success": true,
    "message": "Session logged out successfully"
  }
}
```

---

### ❌ Error Responses

#### 401 Unauthorized (Invalid Token)

```json
{
  "status": "error",
  "code": 401,
  "message": null,
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "error_message": "Invalid session",
  "error_code": "TOKEN_INVALID"
}
```

---

## 6. Logout All

### 📌 Endpoint Bilgileri

- **Method:** `POST`
- **Route:** `{{base_url}}/auth/logout-all`
- **Description:** Tüm aktif oturumları kapatır ve tüm token'ları iptal eder

---

### 🔧 Headers

```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

**Not:** Bu endpoint authentication gerektirir (Bearer token).

---

### 🌐 Route

```
POST {{base_url}}/auth/logout-all
```

---

### 📝 Path Variables

Bu endpoint path variable kullanmaz.

---

### 📨 Request Body

Bu endpoint request body kullanmaz.

---

### ✅ Success Response (200 OK)

```json
{
  "status": "success",
  "code": 200,
  "message": "Logged out from all sessions successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "success": true,
    "sessions_revoked": 3
  }
}
```

---

## 7. Refresh Token

### 📌 Endpoint Bilgileri

- **Method:** `POST`
- **Route:** `{{base_url}}/auth/refresh`
- **Description:** Refresh token kullanarak yeni access ve refresh token alır

---

### 🔧 Headers

```
Content-Type: application/json
```

**Not:** Bu endpoint authentication gerektirmez (refresh token ile çalışır).

---

### 🌐 Route

```
POST {{base_url}}/auth/refresh
```

---

### 📝 Path Variables

Bu endpoint path variable kullanmaz.

---

### 📨 Request Body

```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Body Parametreleri:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `refresh_token` | string | ✅ Yes | JWT refresh token |

---

### ✅ Success Response (200 OK)

```json
{
  "status": "success",
  "code": 200,
  "message": "Token refreshed successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "user_id": "USR-1234567890ABCDEF",
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

---

### ❌ Error Responses

#### 401 Unauthorized (Invalid/Expired Refresh Token)

```json
{
  "status": "error",
  "code": 401,
  "message": null,
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "error_message": "Invalid or expired refresh token",
  "error_code": "TOKEN_INVALID"
}
```

---

## 🧪 Test Senaryoları

### Senaryo 1: Tam Kullanıcı Kayıt ve Doğrulama Akışı

1. **Agreement bilgilerini al:**
   ```
   GET {{base_url}}/agreements/active?agreement_type=terms&locale=tr-TR
   GET {{base_url}}/agreements/active?agreement_type=privacy_policy&locale=tr-TR
   ```

2. **Kullanıcı kaydı:**
   ```
   POST {{base_url}}/auth/register
   Body: { "username": "test_user", "email": "test@example.com", ... }
   ```

3. **Email doğrulama gönder (opsiyonel):**
   ```
   POST {{base_url}}/auth/send-verification-email
   Body: { "user_id": "USR-...", "email": "test@example.com" }
   ```

4. **Email doğrula:**
   ```
   POST {{base_url}}/auth/verify-email
   Body: { "verification_token": "..." }
   ```

5. **Giriş yap:**
   ```
   POST {{base_url}}/auth/login
   Body: { "email_or_username": "test@example.com", "password": "..." }
   ```

---

### Senaryo 2: Token Yenileme

1. **Token yenile:**
   ```
   POST {{base_url}}/auth/refresh
   Body: { "refresh_token": "..." }
   ```

2. **Yeni token'ları kullan:**
   ```
   Authorization: Bearer <new_access_token>
   ```

---

### Senaryo 3: Çıkış Yapma

1. **Tek oturumdan çıkış:**
   ```
   POST {{base_url}}/auth/logout
   Headers: Authorization: Bearer {{access_token}}
   ```

2. **Tüm oturumlardan çıkış:**
   ```
   POST {{base_url}}/auth/logout-all
   Headers: Authorization: Bearer {{access_token}}
   ```

---

## 📝 Postman/Bruno Collection Örneği

### Environment Variables

```json
{
  "base_url": "http://localhost:8000",
  "access_token": "",
  "refresh_token": "",
  "user_id": "",
  "client_ip": "192.168.1.1",
  "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}
```

### Collection Structure

```
Authentication Routes
├── Register User
├── Send Verification Email
├── Verify Email
├── Login
├── Logout
├── Logout All
└── Refresh Token
```

---

## 🔗 İlgili Endpoint'ler

- **GET /agreements/active** - Kayıt öncesi sözleşme versiyonlarını almak için
- **POST /workspaces** - Kayıt ve doğrulama sonrası workspace oluşturmak için

---

## 📌 Notlar

1. **Register** endpoint'i için `terms_accepted_version` ve `privacy_policy_accepted_version` değerleri `/agreements/active` endpoint'inden alınmalıdır.
2. **Login** sonrası dönen `access_token` değeri diğer authenticated endpoint'lerde kullanılmalıdır.
3. **Refresh Token** endpoint'i access token süresi dolduğunda kullanılmalıdır.
4. **Logout** ve **Logout All** endpoint'leri authentication gerektirir.
5. Email doğrulama token'ı email'deki link'ten alınır.

---

**Son Güncelleme:** 2024  
**Versiyon:** 1.0

