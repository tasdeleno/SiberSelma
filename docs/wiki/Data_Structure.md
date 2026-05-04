# Veri Mimarisi (Data Structure)

**Özet:** Projenin ihtiyaç duyduğu siber güvenlik notlarının tutulduğu dosya yapısını açıklar. Ana veri kaynağı yerel dizindeki `docs/wiki` klasörüdür.
**Kütüphaneler:** Obsidian (Konsept olarak).
**Bağlantılar:** [[Index]], [[Tool_Search_Wiki]]

## Detaylar

SiberSelma sunucusu, harici API'ler yerine kullanıcının bizzat seçtiği ve indirdiği GitHub siber güvenlik repolarından (Örn: `90DaysOfCyberSecurity`, `RedTeam-Tools`) beslenir.
- Bu repolar `docs/wiki` klasörüne atılır.
- Asistan (Claude), MCP arayüzü sayesinde bu klasörleri bir RAG (Retrieval-Augmented Generation) mekanizması gibi kullanır.

## Entegrasyon
Kullanıcı, bu klasörü kendi Obsidian uygulamasında "Vault" olarak açtığında tüm dosyaları görsel olarak düzenleyebilir, etiketleyebilir.
