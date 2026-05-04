# SiberSelma 🕵️‍♀️

SiberSelma, Claude ve diğer yapay zeka asistanlarına siber güvenlik bilgisi kazandıran açık kaynaklı bir **MCP (Model Context Protocol)** sunucusudur. 736'dan fazla siber güvenlik dokümanını indeksleyerek asistanın sorularınızı wiki tabanlı bir bilgi bankasıyla yanıtlamasını sağlar.

---

## Ne Yapar?

| Tool | Açıklama | Durum |
|------|----------|-------|
| `search_cyber_wiki` | 736 wiki dosyasında tam metin arama | ✅ Aktif |
| `get_remediation_plan` | Zafiyet için wiki'den çözüm planı getirir | ✅ Aktif |
| `analyze_project_vulnerabilities` | Proje kodlarını statik analiz eder (SAST) | 🔜 Yakında |
| `run_basic_pentest` | Hedef URL/IP üzerinde temel pentest taraması | 🔜 Yakında |

---

## Kurulum

### 1. Repoyu Klonla

```bash
git clone https://github.com/kullanici-adi/SiberSelma.git
cd SiberSelma
```

### 2. Sanal Ortam Kur ve Bağımlılıkları Yükle

```bash
python -m venv venv

# Windows
.\venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Wiki Dosyalarını İndeksle

`docs/wiki/` klasöründeki tüm `.md` dosyaları SQLite FTS5 ile indekslenir:

```bash
python ingest.py
```

Başarılı çıktı:
```
'docs\wiki' içerisindeki dosyalar taranıyor ve indeksleniyor...
Başarıyla 736 adet markdown (.md) dosyası SQLite FTS5 ile indekslendi!
```

---

## Claude Desktop'a Bağlama

`%APPDATA%\Claude\claude_desktop_config.json` dosyasını açıp şu satırları ekle:

```json
{
  "mcpServers": {
    "SiberSelma": {
      "command": "python",
      "args": ["C:\\tam\\yol\\SiberSelma\\server.py"]
    }
  }
}
```

> macOS/Linux için `args` içinde `/tam/yol/SiberSelma/server.py` yaz.

Dosyayı kaydedip **Claude Desktop'ı yeniden başlat.**

---

## Kullanım

Claude Desktop açıkken herhangi bir konuşmada aşağıdaki gibi kullanabilirsin:

### Wiki'de Arama

```
@SiberSelma search_cyber_wiki "XSS"
@SiberSelma search_cyber_wiki "SQL Injection bypass"
@SiberSelma search_cyber_wiki "SSRF cloud metadata"
```

### Zafiyet Çözüm Planı

```
@SiberSelma get_remediation_plan "IDOR"
@SiberSelma get_remediation_plan "CSRF"
@SiberSelma get_remediation_plan "SQL Injection"
```

### Örnek Çıktı

```
=== Kaynak: README.md ===
# Server-Side Request Forgery

SSRF is a vulnerability in which an attacker forces a server to
perform requests on their behalf...

=== Kaynak: SSRF_Prevention_Cheat_Sheet.md ===
## Mitigation
- Validate and sanitize all user-supplied URLs
- Use allowlists for permitted domains...
```

---

## Wiki Kaynakları

`docs/wiki/` içinde şu kaynaklar indekslenmiştir:

- **PayloadsAllTheThings** — 60+ zafiyet tipi için payload ve exploit örnekleri
- **OWASP Cheat Sheets** — SQL Injection, XSS, CSRF ve daha fazlası için önleme rehberleri
- **h4cker** — Web, bulut, AI güvenliği, red team, DFIR
- **Awesome Asset Discovery** — Keşif ve OSINT araçları
- **90 Days of Cybersecurity** — Temelden ileri seviyeye öğrenme yolu
- **Awesome ML for Cybersecurity** — Siber güvenlikte makine öğrenmesi kaynakları

---

## Proje Yapısı

```
SiberSelma/
├── server.py        # MCP sunucusu (FastMCP)
├── ingest.py        # Wiki dosyalarını SQLite'a indeksler
├── wiki.db          # FTS5 arama veritabanı (ingest.py ile oluşur)
├── requirements.txt
└── docs/
    └── wiki/        # 736+ siber güvenlik markdown dosyası
        ├── PayloadsAllTheThings/
        ├── h4cker-master/
        ├── cheatsheets/
        └── ...
```

---

## Katkı

Katkıda bulunmak için:

1. Bu repoyu fork'la
2. `docs/wiki/` klasörüne yeni markdown dosyaları ekle
3. `python ingest.py` ile yeniden indeksle
4. Pull request gönder

---

## Lisans

MIT License
