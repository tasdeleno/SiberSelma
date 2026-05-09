# SiberSelma — Proje Rehberi

Bu dosya her session başında otomatik okunur. Projeye yeni başlarken önce bunu, sonra `rapor.md` (bug/eksik/geliştirme takibi), `docs/wiki/Index.md` ve `wiki_schema.md` dosyalarını oku.

> **Önemli:** `rapor.md` projedeki açık bug, eksik ve geliştirme önerilerinin checklist'idir. Bir madde tamamlandığında `[ ]` → `[x]` yap, yanına tarihi ekle ve gerekirse CLAUDE.md "Yapılanlar/Yapılacaklar" bölümünü güncelle.

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
- [x] **OWASP API Security Top 10** — özet+link dosyası (2026-05-09)
- [x] **OWASP Secure Coding Practices** — özet+link dosyası (2026-05-09)
- [x] **Cloud Güvenliği** (AWS/GCP/Azure) — özet+link dosyası (2026-05-09)
- [x] **Docker Bench Security** — özet+link dosyası (2026-05-09)
- [x] **OWASP LLM Top 10 (2025)** — özet+link dosyası (2026-05-10)
- [x] **MITRE ATLAS** — özet+link dosyası, AML.T → OWASP LLM eşlemesi (2026-05-10)
- [ ] **Kendi Türkçe notları** — Gerçek test deneyimlerini `docs/wiki/` altına Türkçe yaz, `ingest.py` ile indeksle

### Faz 6 Tool'ları (2026-05-10)
- [x] `check_email_auth(domain)` — SPF/DMARC/DKIM
- [x] `check_tls(host)` — protokol/cipher/sertifika + eski TLS probe
- [x] `check_subdomain_takeover(subdomain)` — CNAME + 16 servis fingerprint
- [x] `check_cors(url)` — Origin yansıma + null + creds
- [x] `analyze_llm_app(directory)` — OWASP LLM Top 10 desenleri

### Uzun Vadeli (sonraki fazlar)
- [ ] Active Directory tool seti (Kerberoast/AS-REP, BloodHound parser)
- [ ] Mobile static analysis (APK/IPA)
- [ ] Compliance mapping (ISO 27001 / KVKK / PCI-DSS kontrol madde eşleşmesi)

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
