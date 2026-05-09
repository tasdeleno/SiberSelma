# SiberSelma 🕵️‍♀️

<img width="1081" height="2003" alt="Gemini_Generated_Image_ma4otyma4otyma4o" src="https://github.com/user-attachments/assets/1fbbe6d6-fe9d-4ace-9f3b-237ec0d77612" />


**SiberSelma**, Claude / Gemini gibi yapay zeka asistanlarına siber güvenlik bilgisi ve yetenekleri kazandıran açık kaynaklı bir **MCP (Model Context Protocol)** sunucusudur.

İki şey sağlar:
1. **Bilgi tabanı** — 782+ siber güvenlik dokümanını SQLite FTS5 ile indeksler ve aramaya açar.
2. **17 aktif güvenlik tool'u** — SAST, pentest, secret tespiti, CVE/CPE taraması, tehdit istihbaratı, MITRE ATT&CK, OWASP ZAP & nuclei wrapper'ları, batch saldırı yüzeyi taraması ve daha fazlası.

> Her tool dört şekilde kullanılabilir: **MCP** (Claude/Gemini) · **CLI** (terminal) · **HTTP API** (Antigravity, n8n) · **Web UI** (tarayıcı).

[![CI](https://github.com/tasdeleno/SiberSelma/actions/workflows/ci.yml/badge.svg)](https://github.com/tasdeleno/SiberSelma/actions/workflows/ci.yml)

---

## İçindekiler

- [Hızlı Başlangıç](#hızlı-başlangıç)
- [Tool'lar](#toollar)
- [Çalıştırma Modları](#çalıştırma-modları)
- [Konfigürasyon (Env)](#konfigürasyon-env)
- [Kurulum (Detaylı)](#kurulum-detaylı)
- [Docker](#docker)
- [Sık Karşılaşılan Sorunlar](#sık-karşılaşılan-sorunlar)
- [Proje Yapısı](#proje-yapısı)
- [Test & Geliştirme](#test--geliştirme)

---

## Hızlı Başlangıç

```bash
git clone https://github.com/tasdeleno/SiberSelma.git
cd SiberSelma
pip install -r requirements.txt
python ingest.py            # 782 wiki dosyasını indeksle (ilk seferde)
python server.py            # MCP sunucusu (stdio)
```

CLI ile herhangi bir tool'u doğrudan çağır:
```bash
python server.py --tool wiki --query="XSS"
python server.py --tool headers --url=https://example.com
python server.py --tool subdomains --domain=example.com
python server.py --tool batch --domain=example.com         # subdomain → header pipe
python server.py --tool report --url=https://x.com --directory=./project
```

Tarayıcıdan kullanmak için:
```bash
python web_ui.py            # http://localhost:8766
```

HTTP API olarak (Antigravity / n8n / curl):
```bash
python api_server.py        # http://localhost:8765
curl "http://localhost:8765/headers?url=https://example.com"
```

---

## Tool'lar

**17 tool / 5 kategori.** Hepsi MCP, CLI, HTTP API ve Web UI üzerinden çağrılabilir.

### 🔍 Bilgi Tabanı (2)

| Tool | Açıklama |
|------|----------|
| `search_cyber_wiki(query)` | 782 wiki dosyasında FTS5 araması (AND → OR fallback) |
| `get_remediation_plan(vuln)` | Zafiyet için wiki'den çözüm planı |

### 🛡️ Statik & Dinamik Analiz (5)

| Tool | Açıklama |
|------|----------|
| `analyze_project_vulnerabilities(dir)` | `.py/.js/.ts` dosyalarında 17 tehlikeli pattern (SAST) |
| `find_exposed_secrets(dir)` | 12 secret pattern + Shannon entropy filtresi + `.env` git kontrolü |
| `run_basic_pentest(url)` | HTTP header, cookie (HttpOnly/SameSite/Secure), form, sunucu bilgi sızıntısı |
| `check_security_headers(url)` | 10 güvenlik header'ı kontrolü + skor |
| `check_dependencies(file)` | NVD API ile **CPE-based** CVE taraması (paket sürümünden tam eşleşme), 24h cache |

### 🎯 Saldırı Yüzeyi & Aktif Tarama (3)

| Tool | Açıklama |
|------|----------|
| `batch_scan_attack_surface(domain)` | Subdomain keşfi → her birine güvenlik header taraması, zayıf hedefleri öne çıkarır |
| `run_nuclei_scan(target)` | Lokal `nuclei` çalıştırır (yüklü olmalı), JSONL parse + severity gruplaması |
| `run_zap_baseline(target)` | OWASP ZAP daemon API ile passive baseline tarama |

### 🌐 Harici Tehdit İstihbaratı (6)

| Tool | Kaynak | Notlar |
|------|--------|--------|
| `find_subdomains(domain)` | crt.sh SSL logları | 24h cache; key gerektirmez |
| `check_history(url)` | Wayback Machine | Hassas yol arama; 24h cache |
| `check_threat(target)` | AlienVault OTX | 24h cache; key opsiyonel — `ALIENVAULT_OTX_KEY` |
| `get_attack_techniques(vuln)` | MITRE ATT&CK | Filesystem 24h cache |
| `check_breach(email)` | Have I Been Pwned | `HIBP_API_KEY` zorunlu, `Retry-After` aware |
| `fetch_security_news(n)` | THN + BleepingComputer | `feedparser`; `docs/wiki/news/` altına yazar |

### 📋 Orkestrasyon (1)

| Tool | Açıklama |
|------|----------|
| `generate_security_report(url, dir)` | Tüm analiz tool'larını sırayla koşturur, kritik/yüksek/orta özet tablosu üretir |

> `output_format="json"` parametresi ile yapılandırılmış JSON rapor da üretebilir.

### ⚙️ Otomatik Görevler

- **Otomatik CVE → wiki** (`SIBERSELMA_AUTO_CVE_SCAN=1`): Server başlangıcında arkaplan thread'inde `requirements.txt` NVD'ye sorulur, ilk kez görülen CVE'ler `docs/wiki/cve/CVE-XXXX-YYYYY.md` olarak yazılır.
- **HTTP cache layer** (`.cache/http_cache.db`): 24h TTL ile NVD, OTX, crt.sh, Wayback yanıtlarını cacheler — rate-limit ve gecikme problemi büyük ölçüde çözülür.

---

## Çalıştırma Modları

SiberSelma dört farklı modda çalışır.

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

### 4. Web UI (Tarayıcı)

```bash
python web_ui.py            # http://localhost:8766
```

Standart kütüphaneyle yazılmış minimalist arayüz, **17 tool'un tamamını** form üzerinden çağırır. Tool seçimi için üstte chip'ler, sonuç koyu tema bir `<pre>` içinde gösterilir. Ek bağımlılık yok (`feedparser` haricinde).

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
| `SIBERSELMA_AUTO_CVE_SCAN` | `1` ise server başlangıcında otomatik CVE taraması başlatır (arkaplan thread) | `0` |
| `ZAP_API_KEY` | OWASP ZAP daemon API key (opsiyonel) | yok |
| `SIBERSELMA_API_TOKEN` | API server Bearer auth token | yok (auth devre dışı) |

---

## Docker

Multi-stage build (build aşaması: `python:3.12-slim`; final image: `gcr.io/distroless/python3-debian12:nonroot`). Wiki indeksi build sırasında oluşturulur, image hazır gelir.

```bash
# Image'ı build et
docker build -t siberselma .

# 1. MCP server (stdio) — başka bir container'dan veya socket'tan kullan
docker run --rm -i siberselma

# 2. HTTP API
docker run --rm -p 8765:8765 \
  -e SIBERSELMA_API_TOKEN=secret123 \
  siberselma python api_server.py

# 3. Web UI
docker run --rm -p 8766:8766 siberselma python web_ui.py

# 4. Tek seferlik CLI komutu
docker run --rm siberselma python server.py --tool wiki --query="XSS"
```

API key'leri çevre değişkeni olarak geç:
```bash
docker run --rm -p 8765:8765 \
  -e HIBP_API_KEY=... \
  -e NVD_API_KEY=... \
  -e ALIENVAULT_OTX_KEY=... \
  siberselma python api_server.py
```

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
├── server.py               # MCP server + CLI (FastMCP), 17 tool
├── api_server.py           # HTTP API wrapper (Bearer auth + path whitelist)
├── web_ui.py               # Tarayıcı arayüzü (standart kütüphane)
├── ingest.py               # Wiki → SQLite FTS5 indeksleyici (deduplikasyon)
├── wiki.db                 # FTS5 veritabanı (gitignored)
├── requirements.txt        # mcp, httpx, pytest, feedparser
├── setup.ps1               # Windows otomatik kurulum
├── Dockerfile              # multi-stage, distroless nonroot
├── .dockerignore
├── .github/
│   └── workflows/ci.yml    # GitHub Actions: pytest matrix (3.11 + 3.12)
├── tests/
│   └── test_patterns.py    # SAST + secret regex testleri (19 test)
├── docs/
│   └── wiki/               # 782+ siber güvenlik markdown
│       ├── PayloadsAllTheThings/
│       ├── OWASP-CheatSheets/
│       ├── OWASP_API_Top10_2023.md
│       ├── Secure_Coding_Practices.md
│       ├── Cloud_Security_AWS_GCP_Azure.md
│       ├── Docker_Container_Security.md
│       ├── cve/            # auto_cve_scan_to_wiki çıktıları
│       ├── news/           # fetch_security_news çıktıları
│       └── ...
├── .cache/                 # MITRE ATT&CK + http_cache.db (gitignored)
├── CLAUDE.md               # AI session rehberi
├── CHANGELOG.md            # Sürüm notları (Keep a Changelog)
├── rapor.md                # Açık bug/eksik checklist'i
└── wiki_schema.md          # Wiki yazım kuralları
```

---

## Test & Geliştirme

```bash
# Pattern testleri (19 test, ~1 sn)
python -m pytest tests/ -q

# CLI ile her tool denemek
python server.py --tool <name> --<arg>=<value>

# HTTP API ile denemek
python api_server.py
curl "http://localhost:8765/wiki?q=XSS"

# Web UI ile denemek
python web_ui.py
open http://localhost:8766
```

CI **GitHub Actions** üzerinde Python 3.11 + 3.12 matrix'inde otomatik koşar (`.github/workflows/ci.yml`): pytest, syntax-check, ingest smoke test, CLI smoke test.

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
