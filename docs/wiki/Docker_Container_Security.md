# Docker / Container Security (Docker Bench + CIS)

## Ozet

Docker Bench Security ve CIS Docker Benchmark'in en yaygin uyarilari. Kontroller `docker-bench-security` script'i ile otomatize edilebilir.

## Kutuphaneler / Araclar

- [docker-bench-security](https://github.com/docker/docker-bench-security) — CIS benchmark script'i
- [Trivy](https://github.com/aquasecurity/trivy) — image scanning
- [Snyk Container](https://snyk.io/product/container-vulnerability-management/)
- [Falco](https://falco.org/) — runtime security
- [grype](https://github.com/anchore/grype) — vulnerability scanner

## Image Build

- [ ] **Minimal base image** — `alpine`, `distroless`, `scratch` (Debian/Ubuntu yerine)
- [ ] **Multi-stage build** — build artefakti final image'a gitmiyor
- [ ] **USER non-root** — `USER 1000:1000` (default root tehlikeli)
- [ ] **No secrets in layers** — `ARG` ve `ENV` ile secret koyma; `--secret` mount kullan (BuildKit)
- [ ] **`.dockerignore`** — `.git`, `.env`, `node_modules` cikarilmis

```dockerfile
# Iyi ornek
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .

FROM gcr.io/distroless/nodejs20-debian12
WORKDIR /app
COPY --from=build /app /app
USER 1000
CMD ["index.js"]
```

## Image Tarama

```bash
trivy image --severity HIGH,CRITICAL my-app:latest
grype my-app:latest
```

CI/CD pipeline'da fail-on-severity ayarla:
```yaml
- run: trivy image --exit-code 1 --severity CRITICAL my-app:${{ github.sha }}
```

## Runtime / docker run

- [ ] `--read-only` filesystem (yazilabilir alan icin `--tmpfs /tmp`)
- [ ] `--cap-drop=ALL` + sadece gerekli `--cap-add`
- [ ] `--security-opt no-new-privileges`
- [ ] `--pids-limit 100` — fork bomba korumasi
- [ ] `--memory=512m --cpus=1` — resource limit
- [ ] `--user 1000:1000` — root ile calistirma

```bash
docker run \
  --read-only \
  --tmpfs /tmp \
  --cap-drop=ALL \
  --security-opt no-new-privileges \
  --pids-limit 100 \
  --memory 512m \
  --user 1000:1000 \
  my-app:latest
```

## Docker Daemon

- [ ] `dockerd --userns-remap` — UID/GID izolasyonu
- [ ] TLS + client cert authentication (TCP socket'a expose etme!)
- [ ] `auditd` ile `/var/lib/docker`, `/etc/docker` izleniyor
- [ ] Log driver: `json-file` yerine `journald`/`syslog` (rotation otomatik)
- [ ] `live-restore` acik (`/etc/docker/daemon.json`)

## Docker Socket Tehlikesi

`/var/run/docker.sock`'i container'a mount etmek root yetkisi vermek demek:
```bash
# YANLIS — host'a tam erisim
docker run -v /var/run/docker.sock:/var/run/docker.sock my-app

# DOGRU — sadece okuma gerekiyorsa proxy kullan
docker run my-app  # ve TCP API'yi RBAC'li proxy uzerinden cagir
```

## Compose / Orkestrasyon

```yaml
services:
  app:
    image: my-app:1.0
    read_only: true
    tmpfs:
      - /tmp
    user: "1000:1000"
    cap_drop:
      - ALL
    security_opt:
      - no-new-privileges:true
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '1'
```

## Kubernetes (Pod Security)

```yaml
apiVersion: v1
kind: Pod
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 2000
    seccompProfile:
      type: RuntimeDefault
  containers:
  - name: app
    image: my-app:1.0
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop: ["ALL"]
    resources:
      limits:
        memory: 512Mi
        cpu: 1
```

## Yaygin CVE Pattern'leri

- **CVE-2019-5736 (runc):** runc binary'sini overwrite ederek host escape
- **CVE-2024-21626 (runc):** working directory leak ile container escape
- **CapNETRAW + RAW socket:** ARP spoofing icerden
- **`docker cp` kullanim hatasi:** host'a malicious symlink

## Baglantilar

- [Docker Bench for Security](https://github.com/docker/docker-bench-security)
- [CIS Docker Benchmark](https://www.cisecurity.org/benchmark/docker)
- [[Cloud_Security_AWS_GCP_Azure]]
- [[Index]]
