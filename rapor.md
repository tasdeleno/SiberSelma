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
- [ ] **Otomatik CVE → wiki** — `server.py` her başladığında `requirements.txt`'i NVD'ye sorsun, yeni CVE'leri `docs/wiki/cve/CVE-XXXX-XXXXX.md` olarak yazsın.
- [ ] **Faz 5 wiki kaynakları** — OWASP API Top 10, Secure Coding Practices, CloudSploit, Docker Bench eklenmemiş.
- [ ] **Hata mesajı dili tutarsız** — bazı modüller Türkçe karakterli, bazıları ASCII'ye düşmüş; standartlaştır.
- [x] **Rapor JSON çıktısı yok** — `generate_security_report(..., output_format="json")` eklendi (2026-05-09)
- [x] **HIBP `Retry-After` header'ı okunmuyor** — 429'da Retry-After değeri raporlanıyor (2026-05-09)
- [x] **GEMINI.md ve setup.ps1 README'de yok** — Gemini + setup.ps1 README'ye işlendi (2026-05-09)
- [x] **Boş `ai/` ve `networking/` klasörleri** — silindi (2026-05-09)

---

## 🚀 Geliştirme Önerileri

### Kalite
- [x] **Pytest klasörü kur** — `tests/test_patterns.py` ile 19 test (2026-05-09)
- [ ] **SQLite cache layer** — NVD, OTX, Wayback için 24h TTL (Kısmen: MITRE filesystem cache var)
- [x] **CPE-based NVD sorgusu** — sürüm parse + `cpeName` query (2026-05-09)

### Güvenlik
- [x] **TLS doğrulama default açık** + `SIBERSELMA_INSECURE_TLS=1` opt-out (2026-05-09)
- [x] **API server path whitelist** — `SIBERSELMA_ALLOWED_PATHS` env, `SIBERSELMA_API_TOKEN` Bearer auth (2026-05-09)
- [x] **`find_exposed_secrets`'a Shannon entropy filtresi** — entropy < 2.5 ise atla (2026-05-09)

### Yeni Özellikler
- [x] **CLI modu** — `python server.py --tool <name> --<arg>=<val>` (2026-05-09)
- [ ] **Toplu tarama tool'u** — `find_subdomains` çıktısını `check_security_headers`'a pipe eden batch.
- [ ] **OWASP ZAP / Nuclei entegrasyonu** — `run_basic_pentest`'i gerçek tarayıcıyla besle.
- [ ] **Web UI** — FastAPI + HTMX ile raporları tarayıcıda göster.

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

## Kalan Öncelikli Yol Haritası

1. **Otomatik CVE → wiki** (CLAUDE.md Faz 5)
2. **Faz 5 wiki kaynakları** (OWASP API Top 10, Secure Coding Practices, CloudSploit, Docker Bench)
3. **Hata mesajı dili standardizasyonu**
4. **Toplu tarama tool'u** (`find_subdomains` → batch `check_security_headers`)
5. **OWASP ZAP / Nuclei entegrasyonu**
6. **Web UI** (FastAPI + HTMX)
7. **NVD/OTX/Wayback için SQLite cache layer**
