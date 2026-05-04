# SiberSelma — Proje Rehberi

Bu dosya her session başında otomatik okunur. Projeye yeni başlarken önce bunu, sonra `docs/wiki/Index.md` ve `wiki_schema.md` dosyalarını oku.

## Proje Nedir?

SiberSelma, Claude ve diğer LLM'lere siber güvenlik bilgisi kazandıran bir **MCP (Model Context Protocol) sunucusudur.** `docs/wiki/` klasöründeki 736 siber güvenlik dokümanını SQLite FTS5 ile indeksler ve tool olarak sunar.

**GitHub:** https://github.com/tasdeleno/SiberSelma

---

## Mevcut Dosya Yapısı

```
server.py       → MCP sunucusu (FastMCP), 4 tool tanımlı
ingest.py       → docs/wiki/*.md dosyalarını wiki.db'ye indeksler
wiki.db         → FTS5 arama veritabanı (.gitignore'da, ingest.py ile oluşur)
wiki_schema.md  → Wiki yazım kuralları (Obsidian formatı)
docs/wiki/      → 736 siber güvenlik markdown dosyası
cheatsheets/    → OWASP cheat sheet koleksiyonu
```

---

## Tool'ların Durumu

| Tool | Durum | Açıklama |
|------|-------|----------|
| `search_cyber_wiki(query)` | ✅ Çalışıyor | FTS5 ile wiki'de arama |
| `get_remediation_plan(vuln)` | ✅ Çalışıyor | Wiki'den çözüm önerisi |
| `analyze_project_vulnerabilities(dir)` | 🔜 Placeholder | SAST kod analizi yapacak |
| `run_basic_pentest(target)` | 🔜 Placeholder | Web sitesi taraması yapacak |

---

## Yapılanlar

- [x] `ingest.py`: `docs/wiki/` içindeki 736 `.md` dosyasını SQLite FTS5'e indeksler
- [x] `server.py`: FastMCP ile 4 tool tanımlandı; `WIKI_DIR` hatası `cyber-wiki` → `docs/wiki` olarak düzeltildi
- [x] `wiki.db` orphan analizi: 736 dosyanın tamamı FTS5 ile erişilebilir
- [x] `claude_desktop_config.json` güncellendi — Claude Desktop'ta `@SiberSelma` çalışıyor
- [x] README güncellendi, GitHub'a push edildi (`master` branch)

---

## Yapılacaklar

### Mevcut Tool'ları Tamamla
- [ ] `analyze_project_vulnerabilities`: Dizindeki `.py`, `.js`, `.ts` dosyalarını tarayarak `eval`, `exec`, `innerHTML` gibi tehlikeli fonksiyonları tespit et; sonuçları `search_cyber_wiki` ile eşleştir
- [ ] `run_basic_pentest`: Verilen URL'e HTTP isteği at, header'ları, formları, cookie'leri analiz et; wiki'deki pattern'lerle karşılaştır
- [ ] FTS5 arama iyileştirmesi: Şu an tam phrase match çalışıyor, `"SQL Injection parameterized"` gibi multi-token sorgular boş döndürüyor — tokenizer veya AND logic ekle

### Yeni Tool'lar (Öncelik Sırasıyla)
- [ ] `check_security_headers(url)`: Siteye istek at, `CSP`, `X-Frame-Options`, `HSTS`, `Permissions-Policy` gibi güvenlik header'larının eksiklerini listele
- [ ] `check_dependencies(file)`: `requirements.txt` / `package.json` / `pom.xml` alıp bağımlılıkları bilinen CVE'lerle karşılaştır (OWASP A06)
  - **Otomatik CVE taraması:** `server.py` her başladığında `requirements.txt`'i okuyup NVD API'sine sorsun (`https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch=<paket>`), yeni CVE varsa `docs/wiki/cve/CVE-XXXX-XXXXX.md` olarak otomatik oluştursun, ardından `ingest.py` çalıştırılsın — kullanıcı hiçbir şey yapmadan wiki.db güncel kalsın
- [ ] `generate_security_report(target)`: `analyze_project_vulnerabilities` + `run_basic_pentest` çıktısını birleştirip markdown pentest raporu üret
- [ ] `find_exposed_secrets(directory)`: Kodda hardcode API key, token, şifre ara; `.env` dosyasının commit'e girip girmediğini kontrol et

### Yeni Wiki Kaynakları (Öncelik Sırasıyla)
- [ ] **OWASP API Security Top 10** — `https://github.com/OWASP/API-Security` — REST/GraphQL API kullananlar için 10 kritik zafiyet
- [ ] **OWASP Secure Coding Practices** — `https://github.com/OWASP/secure-coding-practices-quick-reference-guide` — `analyze_project_vulnerabilities` için referans
- [ ] **Cloud Güvenliği** — `https://github.com/aquasecurity/cloudsploit` — AWS/GCP/Azure misconfiguration kontrolleri
- [ ] **Docker Bench Security** — `https://github.com/docker/docker-bench-security` — Container deployment güvenliği
- [ ] **Kendi Türkçe notları** — Gerçek test deneyimlerini `docs/wiki/` altına Türkçe yaz, `ingest.py` ile indeksle

---

## Wiki Yazım Kuralları

Yeni bir wiki dosyası oluştururken `wiki_schema.md` kurallarını uygula:
- Her dosyanın başında **Özet**, **Kütüphaneler**, **Bağlantılar** bölümleri olmalı
- Obsidian link formatı kullan: `[[Index]]`, `[[Server_Core]]`
- `python ingest.py` çalıştırmadan wiki.db güncellenmez

---

## Kullanım Testi

Server'ı test etmek için:
```bash
python ingest.py          # wiki.db güncelle
python server.py          # MCP sunucuyu başlat
```

Claude Desktop'ta:
```
@SiberSelma search_cyber_wiki "XSS"
@SiberSelma get_remediation_plan "IDOR"
```
