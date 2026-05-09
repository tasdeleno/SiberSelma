# SiberSelma 🕵️‍♀️

**SiberSelma**, Claude / Gemini gibi yapay zeka asistanlarına siber güvenlik bilgisi ve yetenekleri kazandıran açık kaynaklı bir **MCP (Model Context Protocol)** sunucusudur.

İki şey sağlar:
1. **Bilgi tabanı** — 737+ siber güvenlik dokümanını SQLite FTS5 ile indeksler ve aramaya açar.
2. **Aktif güvenlik tool'ları** — SAST tarama, pentest, secret tespiti, CVE kontrolü, tehdit istihbaratı ve daha fazlası.

> Her tool MCP üzerinden Claude/Gemini'ye, **HTTP API** olarak Antigravity vb. araçlara, **CLI** olarak da terminale açıktır.

---

## İçindekiler

- [Hızlı Başlangıç](#hızlı-başlangıç)
- [Tool'lar](#toollar)
- [Çalıştırma Modları](#çalıştırma-modları)
- [Konfigürasyon (Env)](#konfigürasyon-env)
- [Kurulum (Detaylı)](#kurulum-detaylı)
- [Sık Karşılaşılan Sorunlar](#sık-karşılaşılan-sorunlar)
- [Proje Yapısı](#proje-yapısı)
- [Test & Geliştirme](#test--geliştirme)

---

## Hızlı Başlangıç

```bash
git clone https://github.com/tasdeleno/SiberSelma.git
cd SiberSelma
pip install -r requirements.txt
python ingest.py            # 737 wiki dosyasını indeksle
python server.py            # MCP sunucusu (stdio)
```

Bir tool'u doğrudan terminalden test et:
```bash
python server.py --tool wiki --query="XSS"
python server.py --tool headers --url=https://example.com
python server.py --tool subdomains --domain=example.com
```

---

## Tool'lar

### 🔍 Bilgi Tabanı

| Tool | Açıklama |
|------|----------|
| `search_cyber_wiki(query)` | 737 wiki dosyasında FTS5 araması (AND → OR fallback) |
| `get_remediation_plan(vuln)` | Zafiyet için wiki'den çözüm planı |

### 🛡️ Statik & Dinamik Analiz

| Tool | Açıklama |
|------|----------|
| `analyze_project_vulnerabilities(dir)` | `.py/.js/.ts` dosyalarında 17 tehlikeli pattern (SAST) |
| `find_exposed_secrets(dir)` | 12 secret pattern + Shannon entropy filtresi + `.env` git kontrolü |
| `run_basic_pentest(url)` | HTTP header, cookie (HttpOnly/SameSite/Secure), form, sunucu bilgi sızıntısı |
| `check_security_headers(url)` | 10 güvenlik header'ı kontrolü + skor |
| `check_dependencies(file)` | NVD API ile **CPE-based** CVE taraması (paket sürümünden tam eşleşme) |

### 🌐 Harici Tehdit İstihbaratı

| Tool | Kaynak | Notlar |
|------|--------|--------|
| `find_subdomains(domain)` | crt.sh SSL logları | Key gerektirmez |
| `check_history(url)` | Wayback Machine | Hassas yol arama |
| `check_threat(target)` | AlienVault OTX | Key opsiyonel — `ALIENVAULT_OTX_KEY` |
| `get_attack_techniques(vuln)` | MITRE ATT&CK | 24h lokal cache |
| `check_breach(email)` | Have I Been Pwned | `HIBP_API_KEY` zorunlu |
| `fetch_security_news(n)` | THN + BleepingComputer | `feedparser`; `docs/wiki/news/` altına yazar |

### 📋 Orkestrasyon

| Tool | Açıklama |
|------|----------|
| `generate_security_report(url, dir)` | Tüm analiz tool'larını sırayla koşturur, kritik/yüksek/orta özet tablosu üretir |

> `output_format="json"` parametresi ile yapılandırılmış JSON rapor da üretebilir.

---

## Çalıştırma Modları

SiberSelma üç farklı modda çalışır.

### 1. MCP Server (Claude/Gemini için)

```bash
python server.py
```
stdio üzerinden MCP istemcisine bağlanır. Konfigürasyon detayları için aşağıdaki [Kurulum](#kurulum-detaylı) bölümüne bak.

### 2. CLI (Tek tool, doğrudan terminal)

```bash
python server.py --tool <name> --<arg>=<value>
```

Örnekler:
```bash
python server.py --tool sast --directory_path=./my-project
python server.py --tool report --url=https://example.com --directory=./my-project
python server.py --tool breach --email=user@example.com
python server.py --tool attack --vulnerability="SQL Injection"
```

### 3. HTTP API (Antigravity, n8n, Web UI vb.)

```bash
python api_server.py
```
`http://localhost:8765` üzerinden REST endpoint'leri açar:

| Endpoint | Parametre |
|----------|-----------|
| `/wiki` | `?q=XSS` |
| `/pentest` | `?url=https://x.com` |
| `/headers` | `?url=https://x.com` |
| `/sast` | `?dir=...` |
| `/secrets` | `?dir=...` |
| `/deps` | `?file=requirements.txt` |
| `/report` | `?url=...&dir=...` |
| `/subdomains` | `?domain=x.com` |
| `/history` | `?url=...` |

> **Güvenlik:** Yerel dosya sistemi taraması yapan endpoint'ler (`/sast`, `/secrets`, `/deps`, `/report`) yalnızca `SIBERSELMA_ALLOWED_PATHS` env'inde tanımlı kökler altında çalışır. Default: proje kökü. `SIBERSELMA_API_TOKEN` tanımlıysa Bearer auth zorunlu olur.

---

## Konfigürasyon (Env)

Tüm tool'lar opsiyonel ortam değişkenleriyle yapılandırılabilir:

| Değişken | Etki | Default |
|----------|------|---------|
| `HIBP_API_KEY` | Have I Been Pwned API key (zorunlu — yoksa `check_breach` çalışmaz) | yok |
| `ALIENVAULT_OTX_KEY` | OTX API key (opsiyonel) | yok |
| `NVD_API_KEY` | NVD CVE API key (rate limit'i 5→50 req/30s yapar) | yok |
| `SIBERSELMA_INSECURE_TLS` | `1` ise TLS doğrulamasını kapatır (self-signed pentest hedefleri için) | `0` (TLS açık) |
| `SIBERSELMA_ALLOWED_PATHS` | API server için izinli kök dizinler (`;` ile ayrılır) | proje kökü |
| `SIBERSELMA_API_TOKEN` | API server Bearer auth token | yok (auth devre dışı) |

---

## Kurulum (Detaylı)

### Bağımlılıklar

```bash
# Hangi Python ile çalıştıracaksanız onunla kurun (config'deki yola dikkat!)
python -m pip install -r requirements.txt
```

`requirements.txt`: `mcp`, `httpx`, `pytest`, `feedparser`.

### Wiki İndeksleme

`docs/wiki/` altındaki tüm `.md` dosyaları SQLite FTS5'e yazılır:
```bash
python ingest.py
```

Yeni dosya ekledikten / sildikten sonra tekrar çalıştır — script deduplikasyon yapar (yeni ekler, silineni atar, mevcut dosyaları günceller).

### Claude Desktop

`%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "SiberSelma": {
      "command": "C:\\Path\\To\\python.exe",
      "args": ["C:\\SiberSelma\\server.py"],
      "env": {
        "HIBP_API_KEY": "...",
        "NVD_API_KEY": "..."
      }
    }
  }
}
```

### Gemini CLI

`%USERPROFILE%\.gemini\settings.json` (veya `~/.gemini/settings.json`):

```json
{
  "mcpServers": {
    "SiberSelma": {
      "command": "python",
      "args": ["/path/to/SiberSelma/server.py"]
    }
  }
}
```

Doğrulama:
```bash
/mcp list
@SiberSelma search_cyber_wiki "XSS"
```

### Otomatik Kurulum (Windows)

```powershell
.\setup.ps1
```
Claude Desktop ve Gemini CLI config'lerini otomatik oluşturur.

> **Önerilen kurulum yolu:** `C:\SiberSelma\` (Türkçe karakter içeren yollardan kaçının — JSON config'lerde encoding sorunları çıkar).

---

## Kullanım Örnekleri

### Claude/Gemini İçinden

```
@SiberSelma search_cyber_wiki "SSRF cloud metadata"
@SiberSelma get_remediation_plan "IDOR"
@SiberSelma check_security_headers "https://example.com"
@SiberSelma find_exposed_secrets "C:\projeler\api"
@SiberSelma generate_security_report "https://example.com" "C:\projeler\api"
```

Doğal dille:
```
SiberSelma'yı kullanarak https://mysite.com için kapsamlı güvenlik raporu üret,
proje dizini /home/user/mysite olsun.
```

### Kapsamlı Rapor Çıktısı

`generate_security_report` 5 analiz çalıştırır ve özet üretir:

```markdown
# Güvenlik Raporu — 2026-05-09

## Özet
| Seviye | Sayı |
|--------|------|
| 🔴 Kritik | 2 |
| 🟠 Yüksek | 3 |
| 🟡 Orta  | 5 |

### Öncelikli Düzeltme Adımları
1. Hardcoded secret ve CVE bulunan bağımlılıkları acilen temizle
2. SAST yüksek riskli pattern'leri düzelt
3. Eksik HTTP güvenlik header'larını ekle

## 1. Web Uygulama Analizi …
## 2. Statik Kod Analizi (SAST) …
## 3. HTTP Güvenlik Header'ları …
## 4. Bağımlılık CVE Analizi …
## 5. Hardcoded Secret Tarama …
```

Rapor `security_report_YYYY-MM-DD.md` olarak proje köküne kaydedilir. JSON sürümü için `output_format="json"`.

---

## Sık Karşılaşılan Sorunlar

### "No such file or directory" — Türkçe karakter

JSON config dosyaları `ü/ç/ş` karakterlerini bozuk kodlayabilir. Repoyu `C:\SiberSelma\` gibi ASCII bir dizine taşıyın.

### "Connection closed" / MCP error -32000

Sunucu başladıktan hemen kapanıyor — genellikle paket eksikliği. Terminalde manuel çalıştırarak hatayı görün:
```bash
python server.py
```
`ModuleNotFoundError` görürseniz `pip install -r requirements.txt`'i config'deki Python ile çalıştırın.

### `wiki.db` yok / sonuç dönmüyor

`wiki.db` `.gitignore`'da. İlk kurulumda ve wiki güncellemesi sonrası `python ingest.py` çalıştırın.

### NVD CVE taraması yavaş

API key'siz NVD limiti 30 sn'de 5 istek. `NVD_API_KEY` env tanımlandığında 50 req/30s'ye yükselir ve `check_dependencies` çok daha hızlı tamamlanır.

### Self-signed sertifikalı pentest hedefi

Default TLS doğrulaması açık. Pentest sırasında yanlış sertifikalı hedef için:
```bash
SIBERSELMA_INSECURE_TLS=1 python server.py --tool pentest --target=https://test.local
```

---

## Proje Yapısı

```
SiberSelma/
├── server.py               # MCP server + CLI (FastMCP)
├── api_server.py           # HTTP API wrapper (Bearer auth + path whitelist)
├── ingest.py               # Wiki → SQLite FTS5 indeksleyici
├── wiki.db                 # FTS5 veritabanı (gitignored)
├── requirements.txt
├── setup.ps1               # Windows otomatik kurulum
├── tests/
│   └── test_patterns.py    # SAST + secret regex testleri
├── docs/
│   └── wiki/               # 737+ siber güvenlik markdown
│       ├── PayloadsAllTheThings/
│       ├── OWASP-CheatSheets/
│       ├── news/           # fetch_security_news çıktıları
│       └── ...
├── .cache/                 # MITRE ATT&CK cache (gitignored)
├── CLAUDE.md               # AI session rehberi
├── CHANGELOG.md            # Sürüm notları
├── rapor.md                # Açık bug/eksik checklist'i
└── wiki_schema.md          # Wiki yazım kuralları
```

---

## Test & Geliştirme

```bash
# Pattern testleri (19 test)
python -m pytest tests/ -q

# CLI ile her tool denemek
python server.py --tool <name> --<arg>=<value>

# HTTP API ile denemek
python api_server.py
curl "http://localhost:8765/wiki?q=XSS"
```

Açık iş kalemleri için [`rapor.md`](./rapor.md) ve sürüm notları için [`CHANGELOG.md`](./CHANGELOG.md).

### Wiki Katkısı

```bash
# Yeni markdown dosyası ekle
echo "# Yeni Konu..." > docs/wiki/yeni_konu.md

# Yeniden indeksle
python ingest.py
```

`wiki_schema.md`'deki yazım kurallarına uy: **Özet**, **Kütüphaneler**, **Bağlantılar** bölümleri ve `[[Index]]` formatlı linkler.

---

## Lisans

MIT License — `LICENSE` dosyasına bakın.
