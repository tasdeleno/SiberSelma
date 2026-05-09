# SiberSelma — Bug, Eksik & Geliştirme Raporu

> Bu dosya proje başında otomatik okunur. Bir madde tamamlandığında `[ ]` → `[x]` yap ve yanına tarih/PR notu ekle.
> Son güncelleme: 2026-05-09

---

## 🐞 Buglar

### Yüksek Öncelik
- [x] **`find_subdomains` URL prefix bug** — `removeprefix()`'e geçildi (2026-05-09)
- [x] **`check_threat` API key okunmuyor** — `ALIENVAULT_OTX_KEY` env okunuyor, 401/403 ayrıştırıldı (2026-05-09)
- [x] **Cookie HttpOnly tespiti yanlış** — `has_nonstandard_attr` + SameSite kontrolü eklendi (2026-05-09)
- [x] **API server path traversal** — `_safe_path` + `SIBERSELMA_ALLOWED_PATHS` + Bearer token auth (2026-05-09)

### Orta Öncelik
- [x] **Tüm SSL doğrulamaları kapalı** — `_ssl_ctx()` merkezi yardımcı + `SIBERSELMA_INSECURE_TLS` env opt-out (2026-05-09)
- [x] **NVD `keywordSearch` false-positive** — CPE-based (`cpeName` / `virtualMatchString`) sorguya geçildi, sürüm parse'i eklendi (2026-05-09)
- [x] **NVD rate limit handling** — `NVD_API_KEY` env desteği + paketler arası sleep (2026-05-09)
- [x] **MITRE ATT&CK her çağrıda 30+ MB indiriyor** — `.cache/` altında 24h TTL ile cache'lendi (2026-05-09)
- [x] **`generate_security_report` özet konumu kırılgan** — `header_lines` ayrıldı (2026-05-09)
- [x] **`fetch_security_news` regex XML parser** — `feedparser` kullanımına geçildi (2026-05-09)

### Küçük
- [x] **`analyze_project_vulnerabilities` venv skip eksik** — segment-based skip (2026-05-09)
- [x] **Tekrar eden `import re as _re`** — global `re` kullanımına geçildi (2026-05-09)
- [x] **`requirements.txt` ölü bağımlılıklar** — `markdown`, `python-dotenv` çıkarıldı; `feedparser` eklendi (2026-05-09)
- [x] **`ensure_wiki_dir` örnek dosyası yanıltıcı** — örnek dosya yazma kaldırıldı (2026-05-09)
- [x] **`find_exposed_secrets` wiki örneklerini kapsıyor** — wiki/payload/cheatsheet klasörleri skip listesine eklendi (2026-05-09)

---

## 📋 Eksikler

- [x] **Test klasörü yok** — `tests/test_patterns.py` eklendi, 19 test geçiyor (2026-05-09)
- [x] **Logging yok** — `__main__` bloğu `logging` modülüne (stderr) geçti (2026-05-09)
- [x] **Otomatik CVE → wiki** — `SIBERSELMA_AUTO_CVE_SCAN=1` ile arkaplan thread (2026-05-09)
- [x] **Faz 5 wiki kaynakları** — OWASP API Top 10, Secure Coding, Cloud (AWS/GCP/Azure), Docker eklendi (2026-05-09)
- [x] **Hata mesajı dili tutarsız** — `başarısız`, `alınamadı`, `bulunamadı`, `keşfedildi`, `geçmişini`, `İlişkili`, `Ülke`, `İtibar`, `Uyarı`, `Lütfen`, `geçersiz`, `aşıldı` Türkçe karakterli hale getirildi (2026-05-09)
- [x] **Rapor JSON çıktısı yok** — `generate_security_report(..., output_format="json")` eklendi (2026-05-09)
- [x] **HIBP `Retry-After` header'ı okunmuyor** — 429'da Retry-After değeri raporlanıyor (2026-05-09)
- [x] **GEMINI.md ve setup.ps1 README'de yok** — Gemini + setup.ps1 README'ye işlendi (2026-05-09)
- [x] **Boş `ai/` ve `networking/` klasörleri** — silindi (2026-05-09)

---

## 🚀 Geliştirme Önerileri

### Kalite
- [x] **Pytest klasörü kur** — `tests/test_patterns.py` ile 19 test (2026-05-09)
- [x] **SQLite cache layer** — `.cache/http_cache.db` 24h TTL; OTX + crt.sh aktif (2026-05-09)
- [x] **CPE-based NVD sorgusu** — sürüm parse + `cpeName` query (2026-05-09)

### Güvenlik
- [x] **TLS doğrulama default açık** + `SIBERSELMA_INSECURE_TLS=1` opt-out (2026-05-09)
- [x] **API server path whitelist** — `SIBERSELMA_ALLOWED_PATHS` env, `SIBERSELMA_API_TOKEN` Bearer auth (2026-05-09)
- [x] **`find_exposed_secrets`'a Shannon entropy filtresi** — entropy < 2.5 ise atla (2026-05-09)

### Yeni Özellikler
- [x] **CLI modu** — `python server.py --tool <name> --<arg>=<val>` (2026-05-09)
- [x] **Toplu tarama tool'u** — `batch_scan_attack_surface(domain)` (2026-05-09)
- [x] **OWASP ZAP / Nuclei entegrasyonu** — `run_nuclei_scan`, `run_zap_baseline` (2026-05-09)
- [x] **Web UI** — `python web_ui.py` → `http://localhost:8766` (standart kütüphane, 8 tool) (2026-05-09)

### Repo Hijyeni
- [x] **README'ye Gemini CLI + setup.ps1 + CLI + HTTP API + env tablosu** eklendi (2026-05-09)
- [x] **Boş klasörleri sil** — `ai/`, `networking/`, `misc/` (2026-05-09)
- [x] **`requirements.txt`'i temizle** (2026-05-09)
- [x] **`.gitignore` güncellendi** — `.cache/`, `security_report_*.md` (2026-05-09)
- [x] **`CHANGELOG.md`** açıldı (2026-05-09)

---

## Bu Oturumda Tamamlanan (2026-05-09)

**26 madde tamamlandı.**

### Buglar (12)
1. `find_subdomains` URL prefix → `removeprefix()`
2. `check_threat` OTX env key + 401/403 ayrıştırma
3. Cookie HttpOnly + SameSite tespiti
4. API server path traversal koruması
5. NVD rate limit + `NVD_API_KEY`
6. MITRE ATT&CK 24h filesystem cache
7. SAST venv/build/dist skip
8. TLS doğrulama default açık (`_ssl_ctx`)
9. `generate_security_report` özet konumu
10. `fetch_security_news` → `feedparser`
11. NVD CPE-based sorgu (sürüm parse'i)
12. `ensure_wiki_dir` yanıltıcı örnek dosya kaldırıldı

### Eksikler & Güvenlik (7)
13. `tests/test_patterns.py` — 19 test
14. `logging` modülü (stderr)
15. HIBP `Retry-After`
16. API Bearer auth + path whitelist
17. Secret entropy filtresi
18. `find_exposed_secrets` wiki klasör skip
19. Rapor JSON çıktısı

### Yeni Özellikler (1)
20. CLI modu (`--tool` + `--arg=val`)

### Hijyen & Dokümantasyon (6)
21. `requirements.txt` temizliği
22. `.gitignore` `.cache/`, `security_report_*.md`
23. `import re as _re` tekrarları temizlendi
24. Boş klasörler silindi
25. `CHANGELOG.md` açıldı
26. README baştan aşağı yenilendi (CLI, HTTP API, env tablosu, kurulum modları, troubleshooting)

---

## Kalan Yol Haritası (düşük öncelik)

- [x] Hata mesajı dili tam standardizasyonu (2026-05-09)
- [x] NVD + Wayback için cache uygulandı (2026-05-09)
- [x] Web UI tüm 17 tool'u kapsıyor (2026-05-09)
- [x] CI workflow (`.github/workflows/ci.yml`) — Python 3.11 & 3.12 matrix (2026-05-09)
- [x] Dockerfile + `.dockerignore` — multi-stage, distroless nonroot (2026-05-09)

**Tüm roadmap tamamlandı. ✅**

---

## Faz 6 — Saldırı Yüzeyi & AI Genişletmeleri (2026-05-10)

### Yeni Tool'lar (5)
- [x] `check_email_auth(domain)` — SPF/DMARC/DKIM (yaygın selector) DNS taraması, +all/p=none gibi zayıflıklar tespiti (2026-05-10)
- [x] `check_tls(host, port)` — aktif protokol/cipher, sertifika expiry/SAN, eski TLSv1/1.1 probe (2026-05-10)
- [x] `check_subdomain_takeover(subdomain)` — CNAME zinciri + 16 servis fingerprint (GitHub Pages, Heroku, S3, Shopify, Fastly...) (2026-05-10)
- [x] `check_cors(url)` — Origin yansıma + null Origin + subdomain spoof, credentials kombinasyonu kritikliği (2026-05-10)
- [x] `analyze_llm_app(directory)` — OWASP LLM Top 10 desenleri: prompt injection, system prompt sızıntısı, eval/subprocess + LLM çıktısı, pickle/torch.load, sonsuz token döngüsü (2026-05-10)

### Yeni Wiki Kaynakları (2)
- [x] `OWASP_LLM_Top10.md` — 2025 listesi, hızlı kontrol checklist, tool/lib referansları (2026-05-10)
- [x] `MITRE_ATLAS.md` — taktik kategorileri, sık AML.T#### → OWASP LLM eşlemesi (2026-05-10)

### Bilinen Kalemler (uzun vadeli)
- [ ] **Active Directory tool seti** — Kerberoast/AS-REP/BloodHound parser (Windows pentest pazarı)
- [ ] **Mobile (Android/iOS APK/IPA) static analysis tool**
- [ ] **Compliance mapping tool** — bulguları ISO 27001 / KVKK / PCI-DSS kontrol maddelerine bağla
- [x] CLI çıktısında Windows cp1254 encoding hatası — `sys.stdout/stderr.reconfigure(encoding='utf-8')` `__main__` bloğuna eklendi (2026-05-10)
- [x] `check_tls` eski TLS probe'unda `DeprecationWarning` — `warnings.catch_warnings()` ile bastırıldı (2026-05-10)

İleriye yönelik diğer fikirler:
- Otomatik wiki güncelleyici (CVE feed'inden günlük yeni dosya)
- API server'a OpenAPI/Swagger UI
- Grafana dashboard entegrasyonu (rapor metrikleri)
- Slack/Discord webhook desteği — kritik bulguda bildirim
- Kapsamlı integration testleri (live API'leri mock'la)
