# Sunucu Çekirdeği (Server Core)

**Özet:** Projenin ana giriş noktası olan `server.py` dosyasını temsil eder. `FastMCP` kullanılarak sunucu ayağa kaldırılır ve standart I/O üzerinden asistanlarla haberleşir.
**Kütüphaneler:** mcp, os, glob.
**Bağlantılar:** [[Index]], [[Tool_Search_Wiki]], [[Tool_Project_Analysis]], [[Tool_Pentest]]

## Detaylar

Sunucu, doğrudan `FastMCP("SiberSelma")` ile başlatılır.
Ana görevi:

- `docs/wiki` klasörünün varlığını doğrulamak (Bkz: [[Data_Structure]]).
- Tanımlanan siber güvenlik araçlarını (Tools) asistanlara standart bir formatta sunmak.
- Asistandan gelen JSON-RPC formatındaki MCP çağrılarını ilgili fonksiyonlara yönlendirmek.

## Gelecek Planları

- FTS5 veritabanı entegrasyonu tamamlandığında, canlı okuma mekanizması bu modülden çıkarılıp SQLite tabanlı hızlı arama eklenecek.
