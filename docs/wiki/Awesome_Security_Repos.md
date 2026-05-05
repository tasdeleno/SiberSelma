# Awesome Security Repos

## Özet

Siber güvenlik araçları, kütüphaneleri ve kaynakları hakkında yüksek kaliteli GitHub repo'ların derlenmiş listesi. Statik kod analizi (SAST), bulut güvenliği, pentest araçları, recon framework'ler, bug bounty kaynakları ve Active Directory güvenliği kapsar. 60+ araç ve framework tarafından temsil edilir.

## Kütüphaneler

- **GitHub Repos** (açık kaynak araçlar)
- **Pentest & Bug Bounty Tools** (siber güvenlik test araçları)
- **Cloud Security Frameworks** (AWS, Azure, GCP)
- **Active Directory Tools** (AD pentesting)
- **Container & DevSecOps** (CI/CD güvenliği)

## Bağlantılar

- [[PayloadsAllTheThings]]
- [[Search_Cyber_Wiki]]
- [[OWASP_Cheat_Sheets]]
- [[SAST_Tools]]

---

## Source Code Analysis (SAST)

Kaynak kod analizi ve statik güvenlik kontrolü araçları.

1. **Semgrep** — `https://github.com/returntocorp/semgrep`
   - Hafif statik analiz, pek çok dil desteği, kaynak kodunda pattern arama
   - Kullanım: Kod zafiyetlerini otomatik tespit et

2. **RegexPassive** — `https://github.com/hahwul/RegexPassive`
   - Güvenlik pasif taraması için regex pattern koleksiyonu
   - Kullanım: Web uygulamalarında yüksek riskli pattern'leri tespit et

3. **Secure Codebox** — `https://github.com/secureCodeBox/secureCodeBox`
   - Sürekli güvenli delivery için, kutudan çıkıyor (out-of-the-box) çözüm
   - Kullanım: Otomatik güvenlik taraması CI/CD pipeline'ında

4. **Graudit** — `https://github.com/wireghoul/graudit`
   - Grep tabanlı kaba kod denetimi aracı
   - Kullanım: Tehlikeli fonksiyon çağrılarını (eval, exec vs.) tespit et

5. **Dependency-Track** — `https://github.com/DependencyTrack/dependency-track`
   - Komponent analizi platformu, yazılım tedarik zinciri riskini tanımla
   - Kullanım: [[check_dependencies]] tool'u için reference

---

## Wordlist ve Payload'lar

Fuzz testing, brute force ve exploit payload'ları.

1. **PayloadsAllTheThings** — `https://github.com/swisskyrepo/PayloadsAllTheThings`
   - Web uygulama güvenliği ve pentest/CTF için payload ve bypass teknikleri
   - Kullanım: [[Search_Cyber_Wiki]] ile XSS, SQL Injection, SSRF payload'larını bul

2. **OneListForAll** — `https://github.com/six2dez/OneListForAll`
   - Web fuzzing için Rockyou benzeri wordlist
   - Kullanım: Brute force ve dictionary saldırıları

---

## Bulut Güvenliği (Cloud Security)

AWS, Azure, GCP ve multi-cloud güvenlik audit araçları.

1. **Prowler** — `https://github.com/prowler-cloud/prowler`
   - AWS güvenlik best practice kontrolleri, 240+ kural (CIS, PCI-DSS, ISO27001, GDPR, HIPAA)
   - Kullanım: AWS hesaplarında configuration audit ve incident response

2. **PurplePanda** — `https://github.com/carlospolop/PurplePanda`
   - Bulutlar arasında privilege escalation path'lerini tespit et
   - Kullanım: Multi-cloud ortamlarında lateral movement riski analiz

3. **S3Scanner** — `https://github.com/sa7mon/S3Scanner`
   - Açık S3 bucket'larını tara ve içeriğini dump et
   - Kullanım: [[run_basic_pentest]] tool'u için S3 enum reference

4. **ScoutSuite** — `https://github.com/nccgroup/ScoutSuite`
   - Multi-cloud (AWS, Azure, GCP) güvenlik denetim aracı
   - Kullanım: Farklı cloud provider'larda misconfiguration tespit

---

## Hacking Araçları (Hacking Tools)

Pentest, exploit ve offensive security araçları.

1. **Tornado** — `https://github.com/samet-g/tornado`
   - Tor Network üzerinden anonim reverse shell (port forwarding olmadan)
   - Kullanım: Penetration test sırasında gizli komut yürütme

2. **Hakoriginfinder** — `https://github.com/hakluke/hakoriginfinder`
   - Reverse proxy arkasındaki origin server'ı keşfet, WAF bypass
   - Kullanım: [[run_basic_pentest]] sırasında gerçek IP keşfi

3. **Nemesis** — `https://github.com/machinexa2/Nemesis`
   - URL scanner: recon, vulnerabilities, secrets, malware scan
   - Kullanım: [[find_exposed_secrets]] için reference

4. **JWT Tool** — `https://github.com/ticarpi/jwt_tool`
   - JSON Web Token test, crack ve exploit toolkit
   - Kullanım: JWT zafiyetlerini [[Search_Cyber_Wiki]] ile araştır

5. **log4j-scan** — `https://github.com/fullhunt/log4j-scan`
   - Log4j RCE (CVE-2021-44228) otomatik scanner
   - Kullanım: log4j zafiyetine karşı hızlı tarama

6. **tplmap** — `https://github.com/epinna/tplmap`
   - Server-Side Template Injection (SSTI) ve kod injection tespit/exploit
   - Kullanım: SSTI zafiyetlerini test et ve exploita dönüştür

---

## Recon Framework'ler

Otomatik keşif ve recon framework'leri.

1. **reconFTW** — `https://github.com/six2dez/reconftw`
   - Domain üzerinde otomatik recon, en iyi araçlarla tarama
   - Kullanım: [[run_basic_pentest]] başında kapsamlı target enum

2. **reNgine** — `https://github.com/yogeshojha/rengine`
   - Web uygulamaları için otomatik recon framework, engine'ler, veri korelasyonu
   - Kullanım: Sürekli monitoring ve vulnerability discovery

---

## Bug Bounty & Penetration Testing

Bug bounty hunting ve pentest kaynakları.

1. **Inventory** — `https://github.com/trickest/inventory`
   - Public bug bounty program'larındaki asset inventory
   - Kullanım: Hangi şirketlerin program'ı olduğunu bul

2. **HowToHunt** — `https://github.com/KathanP19/HowToHunt`
   - Zafiyet hunting için tutorial'lar ve yapılacaklar
   - Kullanım: Bug bounty stratejisi geliştir

3. **Keyhacks** — `https://github.com/streaak/keyhacks`
   - Sızdırılan API key'leri doğrulama yolları
   - Kullanım: [[find_exposed_secrets]] ile geçerli credential'ları test et

4. **TruffleHog** — `https://github.com/trufflesecurity/truffleHog`
   - GitHub repo'larında credential'ları bul
   - Kullanım: [[analyze_project_vulnerabilities]] sırasında secret scanning

5. **Awesome Grep** — `https://github.com/cipher387/awesome-grep`
   - GREP modifikasyonları ve alternatif araçlar
   - Kullanım: Wiki'de pattern arama için (grep-based)

6. **byp4xx** — `https://github.com/lobuhi/byp4xx`
   - HTTP 4xx (403, 401) bypass için Python script
   - Kullanım: [[run_basic_pentest]] sırasında access control bypass

---

## Kontrol Listeleri (Checklists)

Güvenlik denetimi ve pentesting kontrol listeleri.

1. **Web Application Pentest Checklist** — `https://github.com/e11i0t4lders0n/Web-Application-Pentest-Checklist`
   - Kapsamlı web pentest kontrol listesi
   - Kullanım: [[generate_security_report]] oluştururken adımları takip et

2. **OWASP ASVS** — `https://github.com/OWASP/ASVS`
   - Application Security Verification Standard, 4 maturity level
   - Kullanım: [[Search_Cyber_Wiki]] ile OWASP standartları araştır

---

## Cheat Sheet'ler

Hızlı referans ve cheat sheet'ler.

1. **Android Cheat Sheet & Mindmap** — `https://github.com/six2dez/pentest-book`
   - Android pentesting için hızlı referans
   - Kullanım: Android security testing

2. **Mobile App Pentest Cheat Sheet** — `https://github.com/tanprathan/MobileApp-Pentest-Cheatsheet`
   - Mobile application penetration testing özeti
   - Kullanım: [[analyze_project_vulnerabilities]] sırasında mobile-specific checks

---

## Vulnerable Labs

Güvenlik öğrenme için zafiyet barındıran lab'ler.

1. **Buggyapp** — `https://github.com/rahulkadavil/buggyapp`
   - Zafiyet barındıran Android uygulaması, pentesting pratik için
   - Kullanım: Başlangıç seviyesi Android security learning

---

## Active Directory Güvenliği

Active Directory pentesting ve red team araçları.

1. **AD Pentesting Notes** — `https://github.com/nirajkharel/AD-Pentesting-Notes`
   - Active Directory pentesting notları ve teknikleri
   - Kullanım: AD ortamlarında lateral movement ve privilege escalation

2. **BadBlood** — `https://github.com/davidprowe/BadBlood`
   - Gerçek dünya benzeri AD domain yapısı oluştur
   - Kullanım: AD pentesting lab'ı kurma

---

## Benzeri Projeler

Diğer awesome security collections ve specialized lists.

1. **Awesome Pentest** — `https://github.com/enaqx/awesome-pentest`
   - Penetration testing kaynakları, araçları ve koleksiyonları
   - Kullanım: Pentest toolkit bulma

2. **Awesome Android Security** — `https://github.com/saeidshirazi/awesome-android-security`
   - Android security materyalleri ve kaynakları
   - Kullanım: Mobile security learning

3. **AndroidPentest101** — `https://github.com/dn0m1n8tor/AndroidPentest101`
   - Android pentesting roadmap ve başlangıç rehberi
   - Kullanım: Android testing learning path

4. **Awesome Reversing** — `https://github.com/tylerha97/awesome-reversing`
   - Reverse engineering kaynakları
   - Kullanım: Binary analysis ve malware analysis

5. **Awesome Bug Bounty Tools** — `https://github.com/vavkamil/awesome-bugbounty-tools`
   - Bug bounty hunting araçları koleksiyonu
   - Kullanım: Toolchain kurma

---

**Kaynak:** https://github.com/njmulsqb/Awesome-Security-Repos
