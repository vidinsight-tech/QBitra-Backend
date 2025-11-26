# Workspace Plans Routes - Test Kılavuzu

## 📋 Genel Bilgiler

- **Base URL:** `{{base_url}}`
- **Prefix:** `/workspace-plans`
- **Authentication:** Gerekli değil (Public endpoint)
- **Content-Type:** `application/json`

---

## 1. Get API Limits

### 📌 Endpoint Bilgileri

- **Method:** `GET`
- **Route:** `{{base_url}}/workspace-plans/api-limits`
- **Description:** Tüm workspace plan'larının API rate limit'lerini getirir

---

### 🔧 Headers

```
Content-Type: application/json
```

**Not:** Bu endpoint authentication gerektirmez (public endpoint).

---

### 🌐 Route

```
GET {{base_url}}/workspace-plans/api-limits
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
  "message": "API limits retrieved successfully",
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "PLN-1234567890ABCDEF": {
      "limits": {
        "minute": 100,
        "hour": 1000,
        "day": 10000
      }
    },
    "PLN-FEDCBA0987654321": {
      "limits": {
        "minute": 500,
        "hour": 5000,
        "day": 50000
      }
    },
    "PLN-ABCDEF1234567890": {
      "limits": {
        "minute": 1000,
        "hour": 10000,
        "day": 100000
      }
    }
  }
}
```

**Response Yapısı:**

| Key | Type | Description |
|-----|------|-------------|
| `plan_id` | string | Plan ID'si (key olarak) |
| `limits` | object | Rate limit değerleri |
| `limits.minute` | integer | Dakika başına istek limiti |
| `limits.hour` | integer | Saat başına istek limiti |
| `limits.day` | integer | Gün başına istek limiti |

**Mevcut Plan'lar (Örnek):**
- **Freemium Plan:** Düşük limitler (100/min, 1000/hour, 10000/day)
- **Pro Plan:** Orta limitler (500/min, 5000/hour, 50000/day)
- **Enterprise Plan:** Yüksek limitler (1000/min, 10000/hour, 100000/day)

---

### ❌ Error Responses

#### 500 Internal Server Error

```json
{
  "status": "error",
  "code": 500,
  "message": null,
  "traceId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T00:00:00Z",
  "error_message": "Internal server error",
  "error_code": "INTERNAL_ERROR"
}
```

---

## 🧪 Test Senaryoları

### Senaryo 1: API Limit Bilgilerini Alma

1. **API limit'leri al:**
   ```
   GET {{base_url}}/workspace-plans/api-limits
   ```

2. **Response'u kontrol et:**
   - Tüm plan'ların limit'lerini içermeli
   - Her plan için minute, hour, day limit'leri olmalı

---

### Senaryo 2: Rate Limit Kontrolü İçin Kullanım

1. **API limit'leri al:**
   ```
   GET {{base_url}}/workspace-plans/api-limits
   ```

2. **Workspace plan'ını kontrol et:**
   ```
   GET {{base_url}}/workspaces/{{workspace_id}}
   ```

3. **Plan ID'ye göre limit'leri bul:**
   - Workspace'in plan_id'sini al
   - API limits response'undan ilgili plan'ın limit'lerini bul
   - Rate limit middleware bu limit'leri kullanır

---

## 📝 Postman/Bruno Collection Örneği

### Environment Variables

```json
{
  "base_url": "http://localhost:8000"
}
```

### Collection Structure

```
Workspace Plans Routes
└── Get API Limits
```

---

## 🔗 İlgili Endpoint'ler

- **GET /workspaces/{{workspace_id}}** - Workspace bilgilerini almak için (plan_id içerir)
- **GET /workspaces/{{workspace_id}}/limits** - Workspace'in mevcut limit'lerini ve kullanımını görmek için
- **POST /workspaces/{{workspace_id}}/api-keys** - API key oluştururken rate limit'ler için referans

---

## 📌 Notlar

1. **Public Endpoint:**
   - Bu endpoint authentication gerektirmez
   - Herkes API limit bilgilerini görebilir
   - Rate limit middleware bu bilgileri kullanır

2. **Rate Limit Kullanımı:**
   - API key ile yapılan request'lerde workspace plan'ına göre rate limit uygulanır
   - Plan bazlı limitler bu endpoint'ten alınır
   - Rate limit middleware (`RateLimitMiddleware`) bu bilgileri kullanır

3. **Plan Limit Yapısı:**
   - Her plan için 3 seviyeli limit vardır: minute, hour, day
   - Limit'ler dakika/saat/gün başına istek sayısı olarak belirlenir
   - Limit aşıldığında HTTP 429 (Too Many Requests) hatası döner

4. **Plan ID Format:**
   - Plan ID'leri `PLN-[16 haneli hexadecimal]` formatındadır
   - Örnek: `PLN-1234567890ABCDEF`

5. **Limit Değerleri:**
   - Limit değerleri workspace plan seed data'sında tanımlanır
   - Plan güncellendiğinde limit'ler de güncellenir
   - Bu endpoint her zaman güncel limit'leri döner

6. **Rate Limit Middleware:**
   - `RateLimitMiddleware` bu endpoint'ten plan limit'lerini alır
   - API key ile yapılan request'lerde workspace plan'ına göre limit uygulanır
   - Redis üzerinden rate limit tracking yapılır

---

## 🎯 Kullanım Senaryoları

### Senaryo 1: Rate Limit Kontrolü

```javascript
// 1. API limit'leri al
const limitsResponse = await fetch('{{base_url}}/workspace-plans/api-limits');
const limits = await limitsResponse.json();

// 2. Workspace plan'ını al
const workspaceResponse = await fetch('{{base_url}}/workspaces/{{workspace_id}}', {
  headers: { 'Authorization': 'Bearer {{access_token}}' }
});
const workspace = await workspaceResponse.json();

// 3. Plan limit'lerini bul
const planLimits = limits.data[workspace.data.plan_id];
console.log(`Minute limit: ${planLimits.limits.minute}`);
console.log(`Hour limit: ${planLimits.limits.hour}`);
console.log(`Day limit: ${planLimits.limits.day}`);
```

### Senaryo 2: Plan Karşılaştırma

```javascript
// Tüm plan'ların limit'lerini karşılaştır
const limitsResponse = await fetch('{{base_url}}/workspace-plans/api-limits');
const limits = await limitsResponse.json();

Object.entries(limits.data).forEach(([planId, planData]) => {
  console.log(`Plan ${planId}:`);
  console.log(`  Minute: ${planData.limits.minute}`);
  console.log(`  Hour: ${planData.limits.hour}`);
  console.log(`  Day: ${planData.limits.day}`);
});
```

---

**Son Güncelleme:** 2024  
**Versiyon:** 1.0

