# SiberSelma — Proje Rehberi

Bu dosya her session başında otomatik okunur. Projeye yeni başlarken önce bunu, sonra `docs/wiki/Index.md` ve `wiki_schema.md` dosyalarını oku.

## Proje Nedir?

SiberSelma, Gemini, Claude ve diğer LLM'lere siber güvenlik bilgisi kazandıran açık kaynaklı bir **MCP (Model Context Protocol) sunucusudur.** `docs/wiki/` klasöründeki 737+ siber güvenlik dokümanını SQLite FTS5 ile indeksler ve tool olarak sunar.

**GitHub:** https://github.com/tasdeleno/SiberSelma

---

## Mevcut Dosya Yapısı

```
server.py       → MCP sunucusu (FastMCP), 14 tool tanımlı
ingest.py       → docs/wiki/*.md dosyalarını wiki.db'ye indeksler
wiki.db         → FTS5 arama veritabanı (.gitignore'da, ingest.py ile oluşur)
wiki_schema.md  → Wiki yazım kuralları (Obsidian formatı)
docs/wiki/      → 737+ siber güvenlik markdown dosyası
cheatsheets/    → OWASP cheat sheet koleksiyonu
```

---

## Tool'ların Durumu

### Temel Tool'lar

| Tool | Açıklama |
|------|----------|
| `search_cyber_wiki(query)` | FTS5 ile wiki'de tam metin arama (AND + OR fallback) |
| `get_remediation_plan(vuln)` | Wiki'den zafiyet çözüm planı getirir |
| `analyze_project_vulnerabilities(dir)` | .py/.js/.ts dosyalarında 17 tehlikeli pattern tarayan SAST tarayıcı |
| `run_basic_pentest(target)` | HTTP header, cookie, form, sunucu bilgisi güvenlik analizi |
| `check_security_headers(url)` | 10 güvenlik header kontrolü + skor + bilgi sızıntısı tespiti |
| `check_dependencies(file)` | NVD API ile bağımlılık CVE taraması (CVSS skorlarıyla) |
| `find_exposed_secrets(directory)` | 12 pattern ile hardcode secret tarama + .env git kontrolü |
| `generate_security_report(url, directory)` | Tüm tool'ları çalıştırıp kapsamlı güvenlik raporu üretir |

### Harici API Tool'ları

| Tool | API | Açıklama |
|------|-----|----------|
| `find_subdomains(domain)` | crt.sh | SSL loglarından subdomain keşfi |
| `check_history(url)` | Wayback Machine | Eski versiyonlarda açık endpoint/config taraması |
| `check_threat(ip_or_domain)` | AlienVault OTX | IP/domain tehdit geçmişi, pulse sayısı |
| `get_attack_techniques(vuln)` | MITRE ATT&CK | Zafiyet için saldırgan taktik ve teknikleri |
| `check_breach(email)` | Have I Been Pwned | Mail veri ihlali kontrolü (HIBP_API_KEY gerekir) |
| `fetch_security_news(n)` | THN + BleepingComputer | RSS → `docs/wiki/news/` otomatik kayıt |

---

## Kullanım Örnekleri

Gemini CLI'da herhangi bir konuşmada:

```
# Wiki'de arama
@SiberSelma search_cyber_wiki "XSS"
@SiberSelma search_cyber_wiki "SQL Injection bypass"

# Zafiyet çözüm planı
@SiberSelma get_remediation_plan "IDOR"

# Proje güvenlik taraması
@SiberSelma analyze_project_vulnerabilities "/proje/yolu"

# Kapsamlı güvenlik raporu
@SiberSelma generate_security_report "https://example.com" "/proje/yolu"

# Subdomain keşfi
@SiberSelma find_subdomains "example.com"
```

---

## Wiki Yazım Kuralları

Yeni bir wiki dosyası oluştururken `wiki_schema.md` kurallarını uygula:
- Her dosyanın başında **Özet**, **Kütüphaneler**, **Bağlantılar** bölümleri olmalı
- Obsidian link formatı kullan: `[[Index]]`, `[[Server_Core]]`
- `python ingest.py` çalıştırmadan wiki.db güncellenmez

---

## Gemini CLI Bağlantı Kurulumu

`~/.gemini/settings.json` (Windows: `%USERPROFILE%\.gemini\settings.json`) dosyasına ekle:

**Windows:**
```json
{
  "mcpServers": {
    "SiberSelma": {
      "command": "C:\\Users\\kullanici\\AppData\\Local\\Programs\\Python\\Python314\\python.exe",
      "args": ["C:\\SiberSelma\\server.py"]
    }
  }
}
```

**macOS / Linux:**
```json
{
  "mcpServers": {
    "SiberSelma": {
      "command": "python3",
      "args": ["/home/kullanici/SiberSelma/server.py"]
    }
  }
}
```

> **Önemli (Windows):** Repoyu `Masaüstü` gibi Türkçe karakter içeren dizine klonlama. JSON bu karakterleri bozuk kodlar (`MasaÃ¼stÃ¼`) ve sunucu başlatılamaz. `C:\SiberSelma\` gibi bir yol kullan.

---

## Kullanım Testi

Server'ı test etmek için:
```bash
python ingest.py          # wiki.db güncelle
python server.py          # MCP sunucuyu başlat
```

Gemini CLI'da:
```
/mcp list                 # SiberSelma'nın bağlı olduğunu doğrula
```
