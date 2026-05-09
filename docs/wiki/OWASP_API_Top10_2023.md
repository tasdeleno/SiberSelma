# OWASP API Security Top 10 (2023)

## Ozet

REST/GraphQL API'lerde en kritik 10 zafiyet kategorisi. Geleneksel OWASP Top 10'dan farkli olarak API'ye ozgu yetkilendirme, rate limit ve veri ifsasi konularina odaklanir.

## Kutuphaneler

- **Authorization:** OPA, Casbin, Pundit (Ruby), Cancancan
- **Rate limit:** redis-cell, express-rate-limit, slowapi (FastAPI), bucket4j (Java)
- **Schema validation:** Pydantic, Joi, ajv, zod, JSON Schema
- **API Gateway:** Kong, Tyk, AWS API Gateway, Apigee

## API1:2023 - Broken Object Level Authorization (BOLA / IDOR)

Endpoint, kullanicinin sadece kendi nesnelerine erisme yetkisi oldugunu kontrol etmiyor.

```python
# YANLIS
@app.get("/orders/{order_id}")
def get_order(order_id: int):
    return db.orders.find(order_id)  # Herhangi birisinin order'i geri donuyor!

# DOGRU
@app.get("/orders/{order_id}")
def get_order(order_id: int, user=Depends(current_user)):
    order = db.orders.find(order_id)
    if order.user_id != user.id:
        raise HTTPException(403)
    return order
```

## API2:2023 - Broken Authentication

JWT secret zayif, refresh token rotation yok, brute force korumasi yok.

```python
# Sik hatalar:
jwt.encode(payload, "secret123", algorithm="HS256")  # Secret tahmin edilebilir
jwt.decode(token, key, algorithms=["none"])           # alg=none kabul ediliyor
```

**Cozum:** RS256 + 256-bit random secret + token rotation + rate limit + MFA.

## API3:2023 - Broken Object Property Level Authorization

Mass assignment ve excessive data exposure birlestirildi.

```python
# YANLIS — kullanici is_admin'i kendisi setleyebilir
user = User(**request.json())

# DOGRU — sadece izinli alanlar
allowed = {"name", "email", "phone"}
user_data = {k: v for k, v in request.json().items() if k in allowed}
```

## API4:2023 - Unrestricted Resource Consumption

Rate limit yok → DoS / mali zarar (cloud provider faturasi).

```python
from slowapi import Limiter
limiter = Limiter(key_func=lambda r: r.client.host)

@app.get("/expensive")
@limiter.limit("5/minute")
def expensive_endpoint(): ...
```

## API5:2023 - Broken Function Level Authorization

Admin endpoint'leri kullanici rolu ile erisilebiliyor (yatay/dikey privilege escalation).

```python
# Decorator-based RBAC
@app.delete("/users/{id}")
@require_role("admin")
def delete_user(id: int): ...
```

## API6:2023 - Unrestricted Access to Sensitive Business Flows

Otomasyona acik kritik akislar (sepet doldurma, kupon kullanma, hesap olusturma).

**Cozum:** CAPTCHA, fingerprinting, davranis analizi (rate limit yetmez).

## API7:2023 - Server Side Request Forgery (SSRF)

Kullanicidan gelen URL'i sunucu uzerinden cek → ic agdaki kaynaklara eris.

```python
# Beyaz liste + redirect kapali + ic IP bloklamasi
import ipaddress
def safe_fetch(url):
    parsed = urllib.parse.urlparse(url)
    ip = socket.gethostbyname(parsed.hostname)
    if ipaddress.ip_address(ip).is_private:
        raise ValueError("Internal IP")
    return requests.get(url, allow_redirects=False, timeout=5)
```

## API8:2023 - Security Misconfiguration

Debug mode acik, default credential'lar, gereksiz HTTP method'lari, eksik header'lar.

## API9:2023 - Improper Inventory Management

Test/staging API'leri internete acik, eski v1 endpoint'i hala canli ama yamali degil.

**Cozum:** OpenAPI spec, API gateway envanteri, otomatik discovery.

## API10:2023 - Unsafe Consumption of APIs

Kendi API'niz baska API'leri tukettiginde, onlardan gelen veriyi sanitize etmiyorsunuz.

## Baglantilar

- [OWASP API Security Top 10](https://owasp.org/API-Security/editions/2023/en/0x11-t10/)
- [[Index]]
- [[xss_ornek]]
