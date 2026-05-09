# Changelog

Tüm önemli değişiklikler bu dosyada takip edilir. Format [Keep a Changelog](https://keepachangelog.com/) standardına dayanır.

## [Unreleased]

### Altyapı
- **NVD + Wayback HTTP cache** — `_cache_get/_cache_set` bütün dış API tool'larında aktif.
- **Hata mesajı dili standardizasyonu** — Türkçe karakter kullanımı bütün dosyalarda tutarlı.
- **Web UI tüm 17 tool** — `web_ui.py` bütün MCP tool'larını sergiliyor (int field desteği dahil).
- **GitHub Actions CI** — `.github/workflows/ci.yml` Python 3.11 + 3.12 matrix; pytest + ingest smoke test.
- **Dockerfile** — multi-stage build, distroless nonroot final image, 8765 + 8766 expose.
- **`.dockerignore`** — venv, cache, tests, secret artefakt'lar.

### Eklendi
- **CLI modu** — `python server.py --tool <name> --<arg>=<val>` ile MCP olmadan tool çağırma.
- **JSON rapor çıktısı** — `generate_security_report(..., output_format="json")` ile yapılandırılmış çıktı.
- **NVD CPE-based sorgu** — `keywordSearch` yerine `cpeName` / `virtualMatchString`; paket sürümü `==1.2.3`'ten parse edilip CVE eşleşmesinde kullanılıyor.
- **HTTP cache layer** — SQLite tabanlı 24h TTL cache (OTX, crt.sh için aktif). `.cache/http_cache.db`.
- **`batch_scan_attack_surface`** tool'u — Subdomain keşfi + her birine güvenlik header taraması, zayıf skorları öne çıkarır.
- **`run_nuclei_scan`** tool'u — Lokal nuclei çalıştırır, JSONL parse, severity gruplaması.
- **`run_zap_baseline`** tool'u — OWASP ZAP daemon API'sini kullanarak baseline tarama.
- **Otomatik CVE → wiki** — `SIBERSELMA_AUTO_CVE_SCAN=1` env ile server başlangıcında `requirements.txt` NVD'ye sorulur, ilk kez görülen CVE'ler `docs/wiki/cve/CVE-XXXX-YYYYY.md` olarak yazılır (arkaplan thread).
- **Web UI** — `python web_ui.py` ile `http://localhost:8766` üzerinden minimalist arayüz.
- **Faz 5 wiki kaynakları** — `OWASP_API_Top10_2023.md`, `Secure_Coding_Practices.md`, `Cloud_Security_AWS_GCP_Azure.md`, `Docker_Container_Security.md`.

## [2026-05-09] — Bug temizleme & güvenlik sertleştirme

### Düzeltildi
- `find_subdomains` URL prefix bug (`lstrip` → `removeprefix`).
- `check_threat` OTX API key okunmuyordu; `ALIENVAULT_OTX_KEY` env desteği eklendi.
- Cookie HttpOnly tespiti güvenilmezdi (`str(ck)` yerine `has_nonstandard_attr`); SameSite kontrolü de eklendi.
- API server path traversal'a açıktı; `_safe_path` + `SIBERSELMA_ALLOWED_PATHS` whitelist eklendi.
- `generate_security_report` özet konumu `sections[:5]` sabit indeksiyle kırılgandı; `header_lines` ayrımıyla düzeltildi.
- SAST `venv/` (noktasız) klasörünü atlamıyordu; tüm yaygın klasörler segment-based skip ile kapsandı.
- Tekrar eden `import re as _re` global `re`'ye dönüştü.

### Eklendi
- TLS doğrulama default açık (`_ssl_ctx`); `SIBERSELMA_INSECURE_TLS=1` ile opt-out.
- API server Bearer token auth (`SIBERSELMA_API_TOKEN`).
- NVD rate limit handling + `NVD_API_KEY` env desteği.
- MITRE ATT&CK 24h filesystem cache (`.cache/mitre_enterprise_attack.json`).
- HIBP `Retry-After` header okuma.
- `find_exposed_secrets` Shannon entropy filtresi (entropy < 2.5 placeholder elenir).
- `find_exposed_secrets` wiki/payload klasörlerini atlıyor (false-positive azaltma).
- `tests/test_patterns.py` — 19 pytest testi (SAST + secret regex'leri).
- `logging` modülüne geçiş (stderr).
- `fetch_security_news` `feedparser` kullanımına geçti.

### Kaldırıldı
- `requirements.txt`'ten kullanılmayan `markdown`, `python-dotenv`.
- Boş klasörler: `ai/`, `networking/`, `misc/`.
- `ensure_wiki_dir` örnek dosya yazma (FTS5'e ingest etmediği için yanıltıcıydı).

## [2026-05-06] — Faz 4 tamamlandı

### Eklendi
- HIBP, MITRE ATT&CK, AlienVault OTX, crt.sh, Wayback Machine, RSS news entegrasyonları.

## [2026-05-05] — Faz 1-2-3 tamamlandı

### Eklendi
- `analyze_project_vulnerabilities`, `run_basic_pentest`, `check_security_headers`, `check_dependencies`, `find_exposed_secrets`, `generate_security_report` tool'ları.
- FTS5 AND→OR fallback.
