# OWASP Secure Coding Practices Quick Reference

## Ozet

Dile bagimsiz, geliştiriciler icin tek sayfa kontrol listesi. SAST araclarinin (analyze_project_vulnerabilities) referans noktasi.

## Kutuphaneler

- **Input validation:** Pydantic, Joi, validator.js, OWASP Java Encoder
- **Output encoding:** DOMPurify, bleach, sanitize-html
- **Crypto:** libsodium, cryptography (Python), Bouncy Castle
- **Auth:** Authlib, Passport.js, NextAuth, Spring Security

## 1. Input Validation

- Beyaz liste tabanli — sadece izinlileri kabul et
- Tip, uzunluk, format, aralik kontrolu
- Encoding normalize (UTF-8 NFC) → bypass'lari engeller
- File upload: extension + magic byte + boyut limit + ayri storage

## 2. Output Encoding

- Context-aware encoding: HTML, JS, URL, CSS icin farkli
- Template engine'in auto-escape'ini KAPATMA
- innerHTML yerine textContent

## 3. Authentication

- bcrypt/argon2id/scrypt (PBKDF2 minimum, MD5/SHA1 ASLA)
- Salted hash (bcrypt otomatik salt yapar)
- Rate limit + account lockout
- MFA (TOTP, WebAuthn)
- Session ID rotation (login sonrasi yeni ID)

## 4. Session Management

- HttpOnly + Secure + SameSite=Lax/Strict cookie
- 15-30 dk inactivity timeout
- Logout'ta session invalidation (server-side)
- CSRF token (double-submit veya synchronizer pattern)

## 5. Access Control

- Default deny — explicit allow
- Server-side enforcement (client-side kontrol asla yeterli degil)
- ABAC veya RBAC (basit roller yetmiyorsa attribute-based)

## 6. Cryptographic Practices

- AES-256-GCM (CBC degil, ECB asla)
- TLS 1.3 (1.2 minimum, eski sürümler kapali)
- Random secret: `secrets.token_urlsafe(32)`, `crypto.randomBytes(32)`
- Key rotation + key vault (HashiCorp Vault, AWS KMS)

## 7. Error Handling

- Stack trace'i kullaniciya ASLA gosterme → bilgi sızıntisi
- Generic mesaj + log'a detayli yaz
- Try-except'te bare `except:` kullanma

## 8. Data Protection

- PII encrypt at rest (column-level encryption)
- Log'larda kredi karti, parola, token MASK
- Backup'larda encryption + access control

## 9. Communication Security

- HTTPS zorunlu (HSTS preload listesi)
- Certificate pinning (mobil)
- WebSocket: wss://, origin check

## 10. System Configuration

- Production'da debug=False, verbose error=False
- Default credential'lari sil (admin/admin)
- Gerekmeyen servisleri kapat (X-Powered-By, Server header'i sil)

## 11. Database Security

- Parameterized query (string concat ASLA)
- Least privilege DB user (DROP TABLE yetkisi olan user'la connect olma)
- Connection string env'den (kod'da hardcode degil)

## 12. File Management

- Upload extension whitelist + magic byte kontrol
- Dosya adi sanitize: `secure_filename()` veya regex `[^a-zA-Z0-9._-]`
- Web root disinda sakla, served-via signed URL

## 13. Memory Management

- Buffer overflow korumasi (bound check)
- C/C++: `strncpy` yerine `strncpy_s` veya safer alternatif
- Use-after-free: smart pointer (C++), Rust ownership

## Baglantilar

- [Secure Coding Practices Quick Reference Guide v2.1](https://owasp.org/www-project-secure-coding-practices-quick-reference-guide/)
- [[OWASP_API_Top10_2023]]
- [[Index]]
