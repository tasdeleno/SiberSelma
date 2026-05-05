"""
SiberSelma Wiki Kaynak Çekici
Faz 5: Yeni wiki kaynaklarını GitHub'dan indirir, docs/wiki/ altına kaydeder.
Kullanım: python fetch_wiki_sources.py
"""

import os
import re
import json
import urllib.request
import urllib.error
import ssl

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WIKI_DIR = os.path.join(BASE_DIR, "docs", "wiki")

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


def fetch_text(url: str, timeout: int = 15) -> str | None:
    req = urllib.request.Request(url, headers={"User-Agent": "SiberSelma/1.0"})
    try:
        resp = urllib.request.urlopen(req, timeout=timeout, context=ctx)
        return resp.read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"  [!] Hata: {url} — {e}")
        return None


def fetch_github_dir(owner: str, repo: str, path: str = "", branch: str = "main") -> list[dict]:
    """GitHub API ile bir dizindeki dosya listesini getirir."""
    api = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    if branch != "main":
        api += f"?ref={branch}"
    req = urllib.request.Request(api, headers={"User-Agent": "SiberSelma/1.0", "Accept": "application/vnd.github.v3+json"})
    try:
        resp = urllib.request.urlopen(req, timeout=15, context=ctx)
        return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"  [!] GitHub API hatasi: {e}")
        return []


def save_md(content: str, dest_path: str):
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(content)


def fetch_owasp_api_security():
    """OWASP API Security Top 10 (2023)"""
    print("\n[1/4] OWASP API Security Top 10 indiriliyor...")
    dest_dir = os.path.join(WIKI_DIR, "owasp-api-security")
    os.makedirs(dest_dir, exist_ok=True)

    base_raw = "https://raw.githubusercontent.com/OWASP/API-Security/master/editions/2023/en"
    files = [
        ("0x00-header.md", "0x00-header.md"),
        ("0x01-about-owasp.md", "0x01-about-owasp.md"),
        ("0xa1-broken-object-level-authorization.md", "API1-Broken-Object-Level-Authorization.md"),
        ("0xa2-broken-authentication.md", "API2-Broken-Authentication.md"),
        ("0xa3-broken-object-property-level-authorization.md", "API3-Broken-Object-Property-Level-Authorization.md"),
        ("0xa4-unrestricted-resource-consumption.md", "API4-Unrestricted-Resource-Consumption.md"),
        ("0xa5-broken-function-level-authorization.md", "API5-Broken-Function-Level-Authorization.md"),
        ("0xa6-unrestricted-access-to-sensitive-business-flows.md", "API6-Unrestricted-Access-to-Sensitive-Business-Flows.md"),
        ("0xa7-server-side-request-forgery.md", "API7-Server-Side-Request-Forgery.md"),
        ("0xa8-security-misconfiguration.md", "API8-Security-Misconfiguration.md"),
        ("0xa9-improper-inventory-management.md", "API9-Improper-Inventory-Management.md"),
        ("0xaa-unsafe-consumption-of-apis.md", "API10-Unsafe-Consumption-of-APIs.md"),
    ]

    count = 0
    for src_name, dest_name in files:
        url = f"{base_raw}/{src_name}"
        content = fetch_text(url)
        if content:
            save_md(content, os.path.join(dest_dir, dest_name))
            count += 1
            print(f"  [+] {dest_name}")

    print(f"  => {count} dosya indirildi -> docs/wiki/owasp-api-security/")
    return count


def fetch_owasp_secure_coding():
    """OWASP Secure Coding Practices Quick Reference"""
    print("\n[2/4] OWASP Secure Coding Practices indiriliyor...")
    dest_dir = os.path.join(WIKI_DIR, "owasp-secure-coding")
    os.makedirs(dest_dir, exist_ok=True)

    # GitHub API ile dosya listesini al
    items = fetch_github_dir("OWASP", "secure-coding-practices-quick-reference-guide", "", "master")
    count = 0
    for item in items:
        if item.get("type") == "file" and item.get("name", "").endswith(".md"):
            content = fetch_text(item["download_url"])
            if content:
                save_md(content, os.path.join(dest_dir, item["name"]))
                count += 1
                print(f"  [+] {item['name']}")

    # Alt dizinleri de tara
    for item in items:
        if item.get("type") == "dir":
            sub_items = fetch_github_dir("OWASP", "secure-coding-practices-quick-reference-guide", item["path"], "master")
            for sub in sub_items:
                if sub.get("type") == "file" and sub.get("name", "").endswith(".md"):
                    content = fetch_text(sub["download_url"])
                    if content:
                        save_md(content, os.path.join(dest_dir, item["name"] + "_" + sub["name"]))
                        count += 1
                        print(f"  [+] {item['name']}/{sub['name']}")

    print(f"  => {count} dosya indirildi -> docs/wiki/owasp-secure-coding/")
    return count


def fetch_cloud_security():
    """AWS/GCP/Azure güvenlik kontrol listesi — CloudSploit checklist'leri"""
    print("\n[3/4] Cloud Guvenlik kontrolleri indiriliyor...")
    dest_dir = os.path.join(WIKI_DIR, "cloud-security")
    os.makedirs(dest_dir, exist_ok=True)

    # CloudSploit plugin listesi (AWS örneği)
    cloud_guides = [
        ("AWS Güvenlik Kontrol Listesi", "https://raw.githubusercontent.com/aquasecurity/cloudsploit/master/docs/aws/README.md"),
        ("GCP Güvenlik Kontrol Listesi", "https://raw.githubusercontent.com/aquasecurity/cloudsploit/master/docs/google/README.md"),
        ("Azure Güvenlik Kontrol Listesi", "https://raw.githubusercontent.com/aquasecurity/cloudsploit/master/docs/azure/README.md"),
    ]

    count = 0
    for title, url in cloud_guides:
        content = fetch_text(url)
        if content:
            fname = title.lower().replace(" ", "_").replace("/", "") + ".md"
            save_md(content, os.path.join(dest_dir, fname))
            count += 1
            print(f"  [+] {fname}")

    # Eğer README'ler boşsa elle oluştur
    if count == 0:
        print("  Cloud README'leri bulunamadi, temel kontrol listesi olusturuluyor...")
        cloud_checklist = """# Cloud Guvenlik Kontrol Listesi

## AWS Kritik Kontroller
- S3 bucket'lari public erisime kapali olmali
- IAM kullanicilari icin MFA zorunlu olmali
- Root account gunluk kullanimdan uzak tutulmali
- CloudTrail tum region'larda aktif olmali
- Security Groups en az ayricalik prensibine gore konfigüre edilmeli
- RDS veritabanlari public erisime kapali olmali
- Encryption at-rest ve in-transit aktif olmali

## GCP Kritik Kontroller
- Service Account anahtar rotasyonu yapilmali
- VPC Flow Logs aktif olmali
- Cloud Audit Logs etkinlestirilmeli
- Container imajlari vulnerability taramasindan gecmeli

## Azure Kritik Kontroller
- Azure Security Center Standard tier aktif olmali
- Azure AD'de MFA zorunlu olmali
- Storage Account'lar HTTPS-only olmali
- Key Vault ile secret yonetimi yapilmali
- Network Security Group kurallari en az ayricalik ile konfigüre edilmeli

## Referanslar
- [[OWASP Cloud Security]]
- CIS Benchmarks: https://www.cisecurity.org/cis-benchmarks
"""
        save_md(cloud_checklist, os.path.join(dest_dir, "cloud_security_checklist.md"))
        count = 1

    print(f"  => {count} dosya -> docs/wiki/cloud-security/")
    return count


def create_turkish_notes():
    """Türkçe siber güvenlik notları — temel zafiyet şablonları"""
    print("\n[4/4] Turkce siber guvenlik notlari olusturuluyor...")
    dest_dir = os.path.join(WIKI_DIR, "turkce-notlar")
    os.makedirs(dest_dir, exist_ok=True)

    notes = {
        "XSS_Turkce.md": """# Cross-Site Scripting (XSS) — Türkçe Rehber

## Özet
XSS, kullanicidan gelen girdinin filtrelenmeden sayfaya yansitilmasi sonucu olusur.
Saldirgan, kurbanin tarayicisinda JavaScript calistirabilir.

## Türleri
- **Reflected XSS**: Payload URL'de tasınır, aninda yansir
- **Stored XSS**: Payload veritabanina kaydedilir, her ziyarette calısır
- **DOM XSS**: JavaScript ile DOM manipülasyonu sonucu olusur

## Test Yöntemleri
```
<script>alert(1)</script>
"><img src=x onerror=alert(1)>
javascript:alert(1)
```

## Önleme
- Kullanici girdisini her zaman encode et (HTML entity encoding)
- Content-Security-Policy header'i ekle
- HttpOnly ve Secure cookie flag'leri kullan
- DOMPurify gibi sanitizasyon kütüphanesi kullan

## Wiki Referanslari
- [[XSS Prevention Cheat Sheet]]
- [[Content Security Policy]]
""",
        "SQLi_Turkce.md": """# SQL Injection — Türkçe Rehber

## Özet
Kullanici girdisinin SQL sorgusuna dogrudan eklenmesi sonucu saldirgan,
veritabani sorgularini manipüle edebilir.

## Test Payload'lari
```sql
' OR '1'='1
' OR 1=1--
' UNION SELECT null,null,null--
'; DROP TABLE users--
```

## Kör SQLi Teknikleri
```sql
' AND SLEEP(5)--          -- Time-based blind
' AND 1=1--               -- Boolean-based blind
```

## Önleme
- Parametreli sorgu (Prepared Statement) kullan
- ORM kullan (SQLAlchemy, Hibernate vb.)
- En az ayricalik prensibini uygula (read-only hesap)
- Girdi doğrulaması yap (whitelist)
- WAF kullan

## Wiki Referanslari
- [[SQL Injection Prevention Cheat Sheet]]
- [[Query Parameterization Cheat Sheet]]
""",
        "IDOR_Turkce.md": """# IDOR (Insecure Direct Object Reference) — Türkçe Rehber

## Özet
Kullanicinin yetkisiz nesnelere dogrudan erisim saglamasi.
OWASP API Security Top 10'da API1 olarak yer alir.

## Örnek Senaryo
```
GET /api/users/123/orders   → kendi siparislerim
GET /api/users/124/orders   → baska kullanicinin siparisleri (IDOR!)
```

## Test Yöntemi
1. Kendi hesabinda bir islem yap, ID'yi not al
2. Baska hesap ac, ayni ID ile istek gonder
3. Yanit farkliligini incele

## Önleme
- Her istekte yetki kontrolü yap (ABAC/RBAC)
- Dogrudan ID yerine kriptografik referans kullan (UUID)
- Nesne sahipligini her sorguda dogrula

## Wiki Referanslari
- [[OWASP API Security]]
- [[Access Control Cheat Sheet]]
""",
        "SSRF_Turkce.md": """# SSRF (Server-Side Request Forgery) — Türkçe Rehber

## Özet
Sunucunun dahili veya harici kaynaklara saldirgan adina istek atması.
Bulut ortamlarinda metadata servislerine erisim icin kritik.

## Örnek Saldiri
```
# Bulut metadata erisimi
https://victim.com/fetch?url=http://169.254.169.254/latest/meta-data/
https://victim.com/fetch?url=http://[::ffff:a9fe:a9fe]/latest/meta-data/

# Dahili servis taramasi
https://victim.com/fetch?url=http://internal-service:8080/admin
```

## Önleme
- URL whitelist kullan (izin verilen domain listesi)
- Dahili IP aralikları bloklani (127.0.0.1, 10.x, 172.16-31.x, 192.168.x)
- DNS rebinding'e karsi kontrol ekle
- Yanit icerigini kullaniciya dogrudan yansitma

## Wiki Referanslari
- [[SSRF Prevention Cheat Sheet]]
""",
        "Docker_Guvenlik.md": """# Docker Güvenlik Kontrol Listesi

## Imaj Güvenligi
- Resmi veya güvenilir base image kullan
- Alpine veya distroless image tercih et (küçük saldiri yüzeyi)
- Imaji düzenli taramadan gecir: `docker scan` veya Trivy

## Container Runtime
- Root olmayan kullanici ile calistir: `USER nonroot`
- Read-only filesystem: `--read-only`
- Kapasiteleri sınırla: `--cap-drop ALL --cap-add NET_BIND_SERVICE`
- Privileged modu kullanma: `--privileged` sadece zorunlulukta

## Network
- Gereksiz portlari expose etme
- Custom bridge network kullan
- Host network modundan kacin

## Secret Yonetimi
- ENV ile secret gecirme (docker inspect ile görülür)
- Docker Secrets veya Vault kullan
- .env dosyalarini imaja kopyalama

## Referanslar
- Docker Bench Security: https://github.com/docker/docker-bench-security
- CIS Docker Benchmark
""",
    }

    count = 0
    for fname, content in notes.items():
        dest = os.path.join(dest_dir, fname)
        if not os.path.exists(dest):
            save_md(content, dest)
            count += 1
            print(f"  [+] {fname}")
        else:
            print(f"  [~] Atildi (mevcut): {fname}")

    print(f"  => {count} dosya -> docs/wiki/turkce-notlar/")
    return count


def main():
    print("=" * 60)
    print("SiberSelma Faz 5 — Wiki Kaynak Genisletme")
    print("=" * 60)

    total = 0
    total += fetch_owasp_api_security()
    total += fetch_owasp_secure_coding()
    total += fetch_cloud_security()
    total += create_turkish_notes()

    print(f"\n{'='*60}")
    print(f"TAMAMLANDI: {total} dosya eklendi/guncellendi")
    print("Simdi 'python ingest.py' calistirarak wiki.db'yi guncelle.")
    print("=" * 60)


if __name__ == "__main__":
    main()
