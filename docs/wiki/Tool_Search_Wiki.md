# Wiki Arama ve Çözüm Araçları (Tool Search Wiki)

**Özet:** `search_cyber_wiki` ve `get_remediation_plan` MCP araçlarını içerir. Temel amacı LLM için `docs/wiki` klasöründeki notları tarayıp bilgiyi bağlam olarak sunmaktır.
**Kütüphaneler:** Python built-in (`glob`, `os`).
**Bağlantılar:** [[Index]], [[Server_Core]], [[Data_Structure]]

## Detaylar

Şu anki implementasyonda (v1), `glob` kütüphanesi kullanılarak `.md` uzantılı dosyalar gerçek zamanlı okunmaktadır.
Öne çıkan araçlar:

1. `search_cyber_wiki(query: str)`: Aranılan terimi (Örn: XSS) dosya içinde veya isminde arar.
2. `get_remediation_plan(vulnerability_name: str)`: Aynı arama altyapısını kullanarak zafiyet ismine çözüm bulur.

## Sorunlar ve Planlar

- Dosya sayısı 460'ın üzerinde olduğunda performans sorunları yaşanır.
- Bunun önüne geçmek için **SQLite FTS5 tabanlı bir Ingest/Index sistemi** entegre edilmesi planlanmaktadır (İmplementasyon planı onaylandıktan sonra bu wiki güncellenecektir).
