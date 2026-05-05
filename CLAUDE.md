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
- [x] `analyze_project_vulnerabilities`: `.py/.js/.ts` dosyalarında 17 tehlikeli pattern tarar, wiki referansı ekler (2026-05-05)
- [x] `run_basic_pentest`: HTTP isteği ile header/cookie/form/sunucu bilgisi analizi yapar, wiki referansı ekler (2026-05-05)
- [x] FTS5 arama iyileştirmesi: AND sonuç vermezse OR fallback eklendi (2026-05-05)

### Yeni Tool'lar (Öncelik Sırasıyla)
- [x] `check_security_headers(url)`: 10 güvenlik header kontrolü, skor hesaplama, bilgi sızıntısı tespiti (2026-05-05)
- [x] `check_dependencies(file)`: NVD API ile requirements.txt/package.json CVE taraması, CVSS skorlarıyla (2026-05-05)
  - [ ] **Otomatik CVE taraması:** `server.py` her başladığında `requirements.txt`'i okuyup NVD API'sine sorsun, yeni CVE varsa `docs/wiki/cve/CVE-XXXX-XXXXX.md` olarak otomatik oluştursun, ardından `ingest.py` çalıştırılsın
- [x] `generate_security_report(url, directory)`: Tüm tool'ları sırayla çalıştırır, kritik/yüksek/orta özetli rapor üretir, `security_report_YYYY-MM-DD.md` olarak kaydeder (2026-05-06)
- [x] `find_exposed_secrets(directory)`: 12 secret pattern, .env git kontrolü, otomatik redaction (2026-05-05)

### Harici API Entegrasyonları (Öncelik Sırasıyla)
- [x] **Have I Been Pwned API** — `check_breach(email)`: HIBP_API_KEY ortam değişkeni ile çalışır, key yoksa yönlendirme mesajı verir (2026-05-06)
- [x] **MITRE ATT&CK** — `get_attack_techniques(vuln)`: enterprise-attack STIX JSON'dan canlı sorgu yapar (2026-05-06)
- [x] **AlienVault OTX API** — `check_threat(ip_or_domain)`: pulse/itibar/ülke/ASN bilgisi, key opsiyonel (2026-05-06)
- [x] **crt.sh** — `find_subdomains(domain)`: SSL sertifika loglarından subdomain keşfi (2026-05-06)
- [x] **Wayback Machine API** — `check_history(url)`: snapshot sorgusu + hassas yol taraması (2026-05-06)
- [x] **RSS Otomasyonu** — `fetch_security_news(max_items)`: THN + BleepingComputer feed → `docs/wiki/news/` (2026-05-06)

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
