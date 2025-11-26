# Agreement Routes - Test Kılavuzu

## 📋 Genel Bilgiler

- **Base URL:** `{{base_url}}`
- **Prefix:** `/agreements`
- **Authentication:** Gerekli değil (Public endpoint)
- **Content-Type:** `application/json`

---

## 1. Get Active Agreement

### 📌 Endpoint Bilgileri

- **Method:** `GET`
- **Route:** `{{base_url}}/agreements/active`
- **Description:** Aktif sözleşme versiyonunu getirir (Terms of Service veya Privacy Policy)

---

### 🔧 Headers

```
Content-Type: application/json
```

**Not:** Bu endpoint authentication gerektirmez (public endpoint).

---

### 🌐 Route

```
GET {{base_url}}/agreements/active
```

---

### 📝 Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `agreement_type` | string | ✅ Yes | - | Agreement tipi (`terms` veya `privacy_policy`) |
| `locale` | string | ❌ No | `tr-TR` | Locale kodu |

**Query Parameter Örnekleri:**

```
?agreement_type=terms&locale=tr-TR
?agreement_type=privacy_policy&locale=tr-TR
?agreement_type=terms&locale=en-US
```

---

### 📦 Path Variables

Bu endpoint path variable kullanmaz.

---

### 📨 Request Body

Bu endpoint request body kullanmaz (GET request).

---

### ✅ Success Response (200 OK)

```json
{
  "status": "success",
  "code": 200,
  "message": "Active agreement retrieved successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "id": "AGR-1234567890ABCDEF",
    "agreement_type": "terms",
    "version": "1.0.0",
    "locale": "tr-TR",
    "title": "Kullanım Şartları",
    "content": "Kullanım şartları içeriği...",
    "is_active": true,
    "effective_date": "2024-01-01T00:00:00Z",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

---

### ❌ Error Responses

#### 404 Not Found

```json
{
  "status": "error",
  "code": 404,
  "message": null,
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "error_message": "No active agreement found for type terms and locale tr-TR",
  "error_code": "RESOURCE_NOT_FOUND"
}
```

#### 422 Unprocessable Entity (Validation Error)

```json
{
  "status": "error",
  "code": 422,
  "message": null,
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "error_message": "Request validation failed",
  "error_code": "VALIDATION_ERROR"
}
```

---

## 🧪 Test Senaryoları

### Senaryo 1: Terms of Service (Türkçe)

**Request:**
```
GET {{base_url}}/agreements/active?agreement_type=terms&locale=tr-TR
```

**Expected Response:** 200 OK - Terms of Service bilgileri

---

### Senaryo 2: Privacy Policy (Türkçe)

**Request:**
```
GET {{base_url}}/agreements/active?agreement_type=privacy_policy&locale=tr-TR
```

**Expected Response:** 200 OK - Privacy Policy bilgileri

---

### Senaryo 3: Terms of Service (İngilizce)

**Request:**
```
GET {{base_url}}/agreements/active?agreement_type=terms&locale=en-US
```

**Expected Response:** 200 OK - Terms of Service bilgileri (İngilizce)

---

### Senaryo 4: Geçersiz Agreement Type

**Request:**
```
GET {{base_url}}/agreements/active?agreement_type=invalid_type&locale=tr-TR
```

**Expected Response:** 404 Not Found

---

### Senaryo 5: Locale Parametresi Olmadan (Default)

**Request:**
```
GET {{base_url}}/agreements/active?agreement_type=terms
```

**Expected Response:** 200 OK - Default locale (tr-TR) kullanılır

---

### Senaryo 6: Agreement Type Parametresi Eksik

**Request:**
```
GET {{base_url}}/agreements/active
```

**Expected Response:** 422 Unprocessable Entity - Validation error

---

## 📝 Postman/Bruno Collection Örneği

### Postman Collection JSON

```json
{
  "info": {
    "name": "Agreement Routes",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Get Active Agreement - Terms",
      "request": {
        "method": "GET",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "url": {
          "raw": "{{base_url}}/agreements/active?agreement_type=terms&locale=tr-TR",
          "host": ["{{base_url}}"],
          "path": ["agreements", "active"],
          "query": [
            {
              "key": "agreement_type",
              "value": "terms"
            },
            {
              "key": "locale",
              "value": "tr-TR"
            }
          ]
        }
      }
    },
    {
      "name": "Get Active Agreement - Privacy Policy",
      "request": {
        "method": "GET",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "url": {
          "raw": "{{base_url}}/agreements/active?agreement_type=privacy_policy&locale=tr-TR",
          "host": ["{{base_url}}"],
          "path": ["agreements", "active"],
          "query": [
            {
              "key": "agreement_type",
              "value": "privacy_policy"
            },
            {
              "key": "locale",
              "value": "tr-TR"
            }
          ]
        }
      }
    }
  ],
  "variable": [
    {
      "key": "base_url",
      "value": "http://localhost:8000",
      "type": "string"
    }
  ]
}
```

---

## 🔗 İlgili Endpoint'ler

Bu endpoint genellikle şu endpoint'lerden önce kullanılır:

1. **POST /auth/register** - Kullanıcı kaydı sırasında `terms_accepted_version` ve `privacy_policy_accepted_version` parametreleri için

---

## 📌 Notlar

1. Bu endpoint **public** bir endpoint'tir, authentication gerektirmez.
2. Kullanıcı kaydı sırasında bu endpoint'ten alınan `id` değerleri `terms_accepted_version` ve `privacy_policy_accepted_version` olarak kullanılır.
3. `agreement_type` parametresi sadece `terms` veya `privacy_policy` değerlerini kabul eder.
4. `locale` parametresi opsiyoneldir, belirtilmezse default olarak `tr-TR` kullanılır.

---

**Son Güncelleme:** 2024  
**Versiyon:** 1.0

