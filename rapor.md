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
- [ ] **NVD `keywordSearch` false-positive** — `server.py:525` CPE-based sorguya geç (`cpeName=cpe:2.3:a:...`).
- [x] **NVD rate limit handling** — `NVD_API_KEY` env desteği + paketler arası sleep (key'siz 6.5s, key ile 0.7s) (2026-05-09)
- [x] **MITRE ATT&CK her çağrıda 30+ MB indiriyor** — `.cache/` altında 24h TTL ile cache'lendi (2026-05-09)
- [x] **`generate_security_report` özet konumu kırılgan** — `header_lines` ayrıldı, özet doğru konuma yerleşti (2026-05-09)
- [x] **`fetch_security_news` regex XML parser** — `feedparser` kullanımına geçildi (2026-05-09)

### Küçük
- [x] **`analyze_project_vulnerabilities` venv skip eksik** — split-edilen path segmentlerinde `venv`/`.venv`/`.git`/`dist`/`build` kontrolü (2026-05-09)
- [x] **Tekrar eden `import re as _re`** — global `re` kullanımına geçildi (2026-05-09)
- [x] **`requirements.txt` ölü bağımlılıklar** — `markdown`, `python-dotenv` kaldırıldı (2026-05-09)
- [ ] **`ensure_wiki_dir` örnek dosyası yanıltıcı** — yazıyor ama FTS5'e ingest etmiyor.
- [ ] **`find_exposed_secrets` wiki örneklerini kapsıyor** — `PayloadsAllTheThings` taraması devasa false-positive üretiyor.

---

## 📋 Eksikler

- [x] **Test klasörü yok** — `tests/test_patterns.py` eklendi, 19 test geçiyor (2026-05-09)
- [x] **Logging yok** — `__main__` bloğu `logging` modülüne (stderr) geçti (2026-05-09)
- [ ] **Otomatik CVE → wiki** — `server.py` her başladığında `requirements.txt`'i NVD'ye sorsun, yeni CVE'leri `docs/wiki/cve/CVE-XXXX-XXXXX.md` olarak yazsın.
- [ ] **Faz 5 wiki kaynakları** — OWASP API Top 10, Secure Coding Practices, CloudSploit, Docker Bench eklenmemiş.
- [ ] **Hata mesajı dili tutarsız** — bazı modüller Türkçe karakterli, bazıları ASCII'ye düşmüş; standartlaştır.
- [ ] **Rapor JSON çıktısı yok** — `generate_security_report` sadece markdown üretiyor.
- [x] **HIBP `Retry-After` header'ı okunmuyor** — 429'da Retry-After değeri raporlanıyor (2026-05-09)
- [ ] **GEMINI.md ve setup.ps1 README'de yok** — Gemini CLI kullanımı dökümante edilmemiş.
- [ ] **Boş `ai/` ve `networking/` klasörleri** — sil ya da amaç yaz.

---

## 🚀 Geliştirme Önerileri

### Kalite
- [x] **Pytest klasörü kur** — `tests/test_patterns.py` ile `DANGEROUS_PATTERNS` ve `SECRET_PATTERNS` regex testleri (2026-05-09)
- [ ] **SQLite cache layer** — NVD, MITRE, OTX, Wayback yanıtları için 24h TTL. Tablo: `(tool, key, response, fetched_at)`. (Kısmen: MITRE filesystem cache ile çözüldü)
- [ ] **CPE-based NVD sorgusu** — paket sürümünü `pkg==1.2.3`'ten çıkar.

### Güvenlik
- [x] **TLS doğrulama default açık** + `SIBERSELMA_INSECURE_TLS=1` ile opt-out (2026-05-09)
- [x] **API server path whitelist** — `SIBERSELMA_ALLOWED_PATHS` env, `SIBERSELMA_API_TOKEN` Bearer auth (2026-05-09)
- [x] **`find_exposed_secrets`'a Shannon entropy filtresi** — entropy < 2.5 ise atla, private key/DB string'lerde bypass (2026-05-09)

### Yeni Özellikler
- [ ] **CLI modu** — `python server.py --tool pentest --url ...` (MCP olmadan).
- [ ] **Toplu tarama tool'u** — `find_subdomains` çıktısını `check_security_headers`'a pipe eden batch.
- [ ] **OWASP ZAP / Nuclei entegrasyonu** — `run_basic_pentest`'i gerçek tarayıcıyla besle.
- [ ] **Web UI** — FastAPI + HTMX ile raporları tarayıcıda göster.

### Repo Hijyeni
- [ ] **README'ye Gemini CLI bölümü** ekle.
- [x] **Boş klasörleri sil** — `ai/`, `networking/`, `misc/` silindi (2026-05-09)
- [x] **`requirements.txt`'i temizle** — `markdown`, `python-dotenv` çıkarıldı (2026-05-09)
- [x] **`.gitignore` güncellendi** — `.cache/`, `security_report_*.md` eklendi (2026-05-09)
- [ ] **`CHANGELOG.md`** aç — Faz tarihleri CLAUDE.md'de var.

---

## Bu Oturumda Tamamlanan (2026-05-09)

**19 madde tamamlandı:**

### Buglar (10)
1. `find_subdomains` URL prefix → `removeprefix()`
2. `check_threat` OTX env key + 401/403 ayrıştırma
3. Cookie HttpOnly + SameSite tespiti
4. API server path traversal koruması (`_safe_path`)
5. NVD rate limit + `NVD_API_KEY` env desteği
6. MITRE ATT&CK 24h filesystem cache
7. SAST venv/build/dist skip
8. TLS doğrulama default açık (`_ssl_ctx` + opt-out)
9. `generate_security_report` özet konum bug fix (`header_lines`)
10. `fetch_security_news` `feedparser`'a geçiş

### Eksikler (3)
11. `tests/test_patterns.py` — 19 pytest testi
12. `logging` modülüne geçiş (stderr)
13. HIBP `Retry-After` header okuma

### Güvenlik (2)
14. API server Bearer auth + path whitelist
15. `find_exposed_secrets` Shannon entropy filtresi

### Hijyen (4)
16. `requirements.txt` temizliği (`markdown`, `python-dotenv` çıktı, `feedparser` geldi)
17. `.gitignore`: `.cache/`, `security_report_*.md`
18. `import re as _re` tekrarları temizlendi
19. Boş klasörler silindi (`ai/`, `networking/`, `misc/`)

---

## Kalan Öncelikli Yol Haritası

1. **NVD CPE migration** → false-positive çözümü (en yüksek ROI)
2. **Otomatik CVE → wiki** (CLAUDE.md Faz 5)
3. **Faz 5 wiki kaynakları** (OWASP API Top 10 vs.)
4. **CLI modu** (`--tool` flag)
5. **README'ye Gemini CLI bölümü**
