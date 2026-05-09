# OWASP LLM Top 10 (2025)

## Özet
Büyük dil modelleri (LLM) ve agent tabanlı uygulamalardaki en kritik 10 güvenlik riski. Bu liste prompt injection, hassas veri sızıntısı, model tedarik zinciri ve agent yetki suistimaline kadar geniş bir yüzeyi kapsar. SiberSelma kendisi bir MCP/AI uygulaması olduğu için bu liste hem proje içi denetim hem de `analyze_llm_app` aracıyla kullanıcı kodu denetimi için referanstır.

## Kütüphaneler / Araçlar
- `garak` — LLM zafiyet tarayıcısı
- `promptfoo` — prompt güvenlik test framework
- `llm-guard` — input/output filtreleme
- `rebuff` — prompt injection deneme havuzu
- `LangKit` (WhyLabs) — LLM telemetri/güvence

## Top 10 (kısa)
1. **LLM01: Prompt Injection** — Kullanıcı girdisi system prompt'u override eder. Direct ve indirect (RAG/içe alınan içerikten) varyantları var.
2. **LLM02: Sensitive Information Disclosure** — Eğitim verisi, system prompt veya bağlam pencereleri içinden PII/sırların sızması.
3. **LLM03: Supply Chain** — Hugging Face / model hub'lardan zehirli model, lora veya tokenizer indirme.
4. **LLM04: Data and Model Poisoning** — Eğitim/fine-tune verisinin manipülasyonu (backdoor, bias enjeksiyonu).
5. **LLM05: Improper Output Handling** — LLM çıktısının doğrulanmadan `eval`, `exec`, `subprocess`, SQL veya HTML içine geçirilmesi (RCE/XSS).
6. **LLM06: Excessive Agency** — Agent'a aşırı tool yetkisi (dosya silme, ödeme, e-posta gönderme) — onay/sandbox eksikliği.
7. **LLM07: System Prompt Leakage** — System prompt'un kullanıcıya açık olması; gizli iş kuralları/anahtarlar bu prompt'a koyulması.
8. **LLM08: Vector and Embedding Weaknesses** — RAG vektör store'una zehirli doküman, cross-tenant sızıntı, embedding inversion.
9. **LLM09: Misinformation / Overreliance** — Halüsinasyon edilmiş kod/komutun doğrulanmadan üretime alınması.
10. **LLM10: Unbounded Consumption** — Token-based DoS, cüzdan tükenmesi (model wallet drain), context window flooding.

## Hızlı Kontrol Listesi
- [ ] System prompt'ta sır, anahtar, müşteri verisi var mı? → LLM07
- [ ] LLM çıktısı `subprocess`, `exec`, `eval`, `os.system`, `requests.get(url)` içine direkt geçiyor mu? → LLM05
- [ ] Agent tool'ları rate limit / human-in-the-loop / dry-run desteği sunuyor mu? → LLM06
- [ ] RAG'a alınan dokümanlar imzalı/whitelist mi? → LLM01 indirect, LLM08
- [ ] Token harcaması başına kullanıcı limiti var mı? → LLM10
- [ ] `pickle`, `joblib`, `torch.load(weights_only=False)` ile model yükleniyor mu? → LLM03

## Bağlantılar
- Resmi: https://genai.owasp.org/llm-top-10/
- 2025 PDF: https://genai.owasp.org/resource/owasp-top-10-for-llm-applications-2025/
- [[MITRE_ATLAS]] — saldırgan TTP'leri için tamamlayıcı referans
- [[Index]]
