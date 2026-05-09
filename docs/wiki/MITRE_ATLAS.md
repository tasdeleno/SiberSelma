# MITRE ATLAS — Adversarial Threat Landscape for AI Systems

## Özet
ATLAS, MITRE'nin ATT&CK çatısının yapay zekâ sistemlerine uyarlanmış sürümüdür. ML/LLM hattına özgü taktik (Tactic) ve teknikleri (Technique) ID şemasıyla (`AML.T####`) listeler ve gerçek dünya vakalarını (case studies) bunlara bağlar. OWASP LLM Top 10 *risk* listesidir; ATLAS *davranış* (TTP) sözlüğüdür — birlikte kullanıldığında raporlama hem zafiyete hem de saldırgan adımına bağlanabilir.

## Taktik Kategorileri
1. **Reconnaissance** — Hedef ML modelinin türü, eğitim veri kaynağı, API arayüzü hakkında bilgi toplama.
2. **Resource Development** — Adversarial veri seti, proxy model, jailbreak prompt havuzu hazırlama.
3. **Initial Access** — Hugging Face supply-chain, exposed inference endpoint, RAG corpus injection.
4. **ML Model Access** — Model query (black-box), white-box ağırlık ele geçirme, embedding API kötüye kullanımı.
5. **Execution** — `AML.T0050` LLM Plugin Compromise, `AML.T0053` LLM Prompt Injection ile arbitrary tool çağrısı.
6. **Persistence** — Backdoor model, vektör DB içine kalıcı zehirli embedding, fine-tune ile gizli trigger.
7. **Defense Evasion** — Adversarial perturbation, prompt obfuscation, base64/unicode jailbreak.
8. **Discovery** — System prompt extraction, model card sızdırma, training data membership inference.
9. **Collection** — Çıktıdan hassas veri toplama, embedding inversion ile orijinal metin geri çıkarma.
10. **ML Attack Staging** — Model evasion, transfer attack, poisoned proxy ile substitute training.
11. **Exfiltration** — Çıktı kanalı üzerinden veri kaçırma (steganography in tokens), API loglarına sızma.
12. **Impact** — Brand damage, financial fraud, integrity bozma, hizmet reddi (token DoS).

## Sık Atıfta Bulunulan Teknikler
| ID | Teknik | İlgili OWASP LLM |
|----|--------|------------------|
| AML.T0051 | LLM Prompt Injection: Direct | LLM01 |
| AML.T0054 | LLM Jailbreak | LLM01 |
| AML.T0057 | LLM Data Leakage | LLM02, LLM07 |
| AML.T0010 | ML Supply Chain Compromise | LLM03 |
| AML.T0020 | Poison Training Data | LLM04 |
| AML.T0050 | Command and Scripting Interpreter (Plugin) | LLM05, LLM06 |
| AML.T0048 | External Harms | LLM06 |
| AML.T0024 | Exfiltration via ML Inference API | LLM02, LLM10 |

## Bağlantılar
- Resmi: https://atlas.mitre.org/
- Matris (taktik × teknik): https://atlas.mitre.org/matrices/ATLAS
- Case studies: https://atlas.mitre.org/studies
- STIX feed: https://github.com/mitre-atlas/atlas-data
- [[OWASP_LLM_Top10]]
- [[Index]]
