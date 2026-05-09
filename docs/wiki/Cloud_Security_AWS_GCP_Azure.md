# Cloud Misconfiguration Hizli Referans (AWS / GCP / Azure)

## Ozet

CloudSploit, Prowler, ScoutSuite gibi araclarin tarayip raporladigi tipik cloud misconfiguration'lar. Yeni bir cloud projesi devraldiginda once buradan bak.

## Kutuphaneler / Araclar

- **AWS:** [Prowler](https://github.com/prowler-cloud/prowler), [CloudSploit](https://github.com/aquasecurity/cloudsploit), AWS Config, GuardDuty
- **GCP:** [G-Scout](https://github.com/nccgroup/G-Scout), Forseti, GCP Security Command Center
- **Azure:** [ScoutSuite](https://github.com/nccgroup/ScoutSuite), Azure Defender, Microsoft Sentinel
- **Multi-cloud:** [CloudCustodian](https://cloudcustodian.io/), [Cartography](https://github.com/lyft/cartography)

## AWS

### IAM
- [ ] Root account MFA aktif
- [ ] Root access key YOK
- [ ] IAM policy `"Action": "*"` + `"Resource": "*"` kombinasyonu yok
- [ ] Access key 90+ gunluk → rotate
- [ ] Inline policy yerine managed policy

### S3
- [ ] Public read/write ACL yok (`s3:GetObject` herkese acik degil)
- [ ] Bucket policy `"Principal": "*"` yok
- [ ] Server-side encryption (SSE-S3 veya SSE-KMS) acik
- [ ] Versioning + MFA Delete kritik bucket'larda
- [ ] Block Public Access — account level acik

### EC2 / VPC
- [ ] Security group 0.0.0.0/0 ile 22/3389 acik DEGIL
- [ ] EBS volume encryption acik
- [ ] EC2 Instance Metadata Service v2 (IMDSv2) zorunlu
- [ ] VPC Flow Logs acik

### RDS
- [ ] Public erisim KAPALI
- [ ] Encryption at rest acik
- [ ] Automated backup + retention >= 7 gun
- [ ] Deletion protection acik

### Lambda
- [ ] Runtime guncel (deprecated runtime kullanilmiyor)
- [ ] Environment variable'larda secret yok → Secrets Manager
- [ ] X-Ray tracing acik
- [ ] Reserved concurrency ile kontrolsuz scale onleniyor

### CloudTrail
- [ ] Tum region'larda acik
- [ ] Log file validation acik
- [ ] CloudWatch Logs'a stream + alarm

## GCP

### IAM
- [ ] Owner role minimal kullanici
- [ ] Service account key 90+ gun → rotate
- [ ] Audit log Data Access acik (default sadece Admin Activity)

### GCS (Cloud Storage)
- [ ] `allUsers` veya `allAuthenticatedUsers` reader/writer YOK
- [ ] Uniform bucket-level access acik (ACL devre disi)
- [ ] CMEK (Customer Managed Encryption Keys) kritik bucket'larda

### GCE
- [ ] OS Login zorunlu (SSH key metadata yerine)
- [ ] Default network silindi
- [ ] Firewall rule 0.0.0.0/0 ile 22/3389 yok
- [ ] Disk encryption (CMEK)

### Cloud SQL
- [ ] Public IP YOK (Private Service Connect veya Cloud SQL Proxy)
- [ ] SSL zorunlu (`require_ssl=true`)
- [ ] Backup acik

## Azure

### IAM (Azure AD / Entra ID)
- [ ] Privileged role'lere PIM (Privileged Identity Management) ile JIT
- [ ] Conditional Access: MFA, named locations, risk-based
- [ ] Guest user inceleme

### Storage Account
- [ ] "Allow Blob public access" KAPALI
- [ ] Secure transfer (HTTPS only) acik
- [ ] Minimum TLS 1.2

### VM
- [ ] NSG 0.0.0.0/0 ile 22/3389 yok → Bastion veya JIT
- [ ] Disk encryption (Azure Disk Encryption / SSE)
- [ ] Microsoft Defender for Servers Plan 2

### Key Vault
- [ ] Soft delete + purge protection acik
- [ ] RBAC (eski "access policy" yerine)
- [ ] Network access restricted

## Container / Kubernetes (CKS)

- [ ] Image scanning (Trivy, Snyk, Anchore) CI'da zorunlu
- [ ] Read-only root filesystem
- [ ] runAsNonRoot: true
- [ ] PodSecurityStandards: restricted
- [ ] NetworkPolicy default-deny + selective allow
- [ ] Secret encryption at rest (etcd encryption provider)

## Baglantilar

- [Prowler AWS Checks](https://docs.prowler.com/checks/aws/)
- [CIS Benchmarks](https://www.cisecurity.org/cis-benchmarks)
- [[Secure_Coding_Practices]]
- [[Index]]
