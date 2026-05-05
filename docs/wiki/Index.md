# SiberSelma MCP Projesi İndeks Haritası

**Özet:** SiberSelma, yapay zeka asistanlarına (Claude Code, Antigravity vb.) siber güvenlik ve pentest yetenekleri kazandıran açık kaynaklı bir MCP (Model Context Protocol) sunucusudur.
**Kütüphaneler:** FastMCP, Python.
**Bağlantılar:** [[Server_Core]], [[Data_Structure]]

## Proje Modülleri ve Bileşenleri

1. **Ana Sunucu Katmanı**
   - [[Server_Core]]: Sunucunun başlatılması ve FastMCP entegrasyonu.

2. **Araçlar (Tools)**
   - [[Tool_Search_Wiki]]: Siber güvenlik wiki verilerini tarayan araç.
   - [[Tool_Project_Analysis]]: (Geliştirme Aşamasında) SAST / Kod analizi aracı.
   - [[Tool_Pentest]]: (Geliştirme Aşamasında) Hedef sistemlere yönelik aktif tarama ve hack/pentest modülü.

3. **Veri Mimarisi**
   - [[Data_Structure]]: Obsidian tabanlı `docs/wiki` klasörü ve ingest mekanizması yapısı.

4. **Pentest Otomasyon Ajanı (PentestGPT)**
   - [[PentestGPT_Overview]]: Proje özeti, özellikler, USENIX Security 2024 publikasyonu
   - [[PentestGPT_Architecture]]: 5-layer mimari (entry, core, interface, prompts, benchmark)
   - [[PentestGPT_Agent]]: LLM wrapper, flag detection, logging
   - [[PentestGPT_Controller]]: 5-state FSM, pause/resume, lifecycle management
   - [[PentestGPT_Events]]: EventBus, pub/sub decoupling
   - [[PentestGPT_Session]]: File-based persistence, resume support
   - [[PentestGPT_Interface]]: CLI/TUI entry, Textual app, keyboard shortcuts
   - [[PentestGPT_Tools]]: Tool framework, extensible architecture
   - [[PentestGPT_SystemPrompt]]: CTF methodology, flag patterns, fallback strategies
   - [[PentestGPT_Benchmarks]]: XBOW validation (104 zafiyet), 15+ kategoriler
   - [[PentestGPT_Performance]]: December 2025 run results (86.5% başarı, $1.11 avg)
   - [[PentestGPT_BenchmarkRunner]]: Standalone orchestrator, CLI, Docker
   - [[PentestGPT_RealWorldTests]]: Kioptrix, DeathNote, Hackable pentest case studies
   - [[PentestGPT_Design_v0.15]]: Legacy multi-LLM architecture
   - [[PentestGPT_Architecture_Patterns]]: Design decisions, trade-offs, extensibility
   - [[PentestGPT_Backend]]: Claude SDK wrapper, framework-agnostic interface
   - [[PentestGPT_Demo]]: Installation, demo videos, quick start

> Bu harita, `wiki_schema.md` kurallarına göre INGEST operasyonu ile otomatik olarak güncellenir. Son Güncelleme: 2026-05-05.
