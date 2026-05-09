import os
import re
import glob
import sqlite3
import urllib.request
import urllib.error
import ssl
import json
from http.cookiejar import CookieJar
from mcp.server.fastmcp import FastMCP

# SiberSelma MCP Sunucusunu Başlatıyoruz
mcp = FastMCP("SiberSelma")

# Script dizinine göre mutlak yollar
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WIKI_DIR = os.path.join(BASE_DIR, "docs", "wiki")
DB_PATH = os.path.join(BASE_DIR, "wiki.db")

# TLS doğrulama: default AÇIK. SIBERSELMA_INSECURE_TLS=1 ile devre dışı bırakılabilir.
# (Pentest sırasında self-signed sertifikalı hedefler için opt-out.)
INSECURE_TLS = os.environ.get("SIBERSELMA_INSECURE_TLS", "0") == "1"


def _ssl_ctx():
    """TLS baglamı olusturur. INSECURE_TLS=1 ise dogrulama kapalı."""
    ctx = ssl.create_default_context()
    if INSECURE_TLS:
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    return ctx


# --- HTTP cache layer (SQLite, 24h TTL) ---
CACHE_DB = os.path.join(BASE_DIR, ".cache", "http_cache.db")
CACHE_TTL_SECONDS = 24 * 3600


def _cache_get(tool: str, key: str):
    """Cache'ten oku. None dönerse miss veya expired demek."""
    try:
        os.makedirs(os.path.dirname(CACHE_DB), exist_ok=True)
        with sqlite3.connect(CACHE_DB) as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS http_cache "
                "(tool TEXT, key TEXT, response TEXT, fetched_at REAL, PRIMARY KEY(tool, key))"
            )
            row = conn.execute(
                "SELECT response, fetched_at FROM http_cache WHERE tool=? AND key=?",
                (tool, key),
            ).fetchone()
            if not row:
                return None
            response, fetched_at = row
            import time as _time
            if _time.time() - fetched_at > CACHE_TTL_SECONDS:
                return None
            return response
    except Exception:
        return None


def _cache_set(tool: str, key: str, response: str):
    try:
        os.makedirs(os.path.dirname(CACHE_DB), exist_ok=True)
        import time as _time
        with sqlite3.connect(CACHE_DB) as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS http_cache "
                "(tool TEXT, key TEXT, response TEXT, fetched_at REAL, PRIMARY KEY(tool, key))"
            )
            conn.execute(
                "INSERT OR REPLACE INTO http_cache (tool, key, response, fetched_at) VALUES (?, ?, ?, ?)",
                (tool, key, response, _time.time()),
            )
    except Exception:
        pass

def ensure_wiki_dir():
    """Wiki klasörünün var olduğundan emin olur."""
    if not os.path.exists(WIKI_DIR):
        os.makedirs(WIKI_DIR)

@mcp.tool()
def search_cyber_wiki(query: str) -> str:
    """
    Obsidian (LLM Wiki) içerisindeki siber güvenlik notlarını tarar.

    Args:
        query: Aranacak siber güvenlik terimi veya zafiyet adı (örn: "XSS", "SQL Injection", "nmap")
    """
    if not os.path.exists(DB_PATH):
        return "Hata: Veritabanı bulunamadı. Lütfen önce 'python ingest.py' çalıştırarak dosyaları indeksleyin."

    tokens = re.findall(r'\w+', query)
    if not tokens:
        return f"'{query}' için geçerli arama terimi bulunamadı."

    sql = '''
        SELECT filepath, snippet(wiki_search, 1, '>>', '<<', '...', 64)
        FROM wiki_search
        WHERE wiki_search MATCH ?
        ORDER BY rank
        LIMIT 5
    '''

    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            # Önce AND ile dene
            and_query = " AND ".join(f'"{t}"' for t in tokens)
            c.execute(sql, (and_query,))
            rows = c.fetchall()

            # AND sonuç vermezse OR'a düş
            if not rows and len(tokens) > 1:
                or_query = " OR ".join(f'"{t}"' for t in tokens)
                c.execute(sql, (or_query,))
                rows = c.fetchall()

        if not rows:
            return f"'{query}' için wiki'de sonuç bulunamadı."

        results = []
        for row in rows:
            filepath, snippet_text = row
            results.append(f"=== Kaynak: {os.path.basename(filepath)} ===\n{snippet_text}\n")

        return "\n".join(results)
    except Exception as e:
        return f"Arama sırasında hata oluştu: {str(e)}"

DANGEROUS_PATTERNS = {
    ".py": [
        (r'\beval\s*\(', "eval()", "Code_Injection"),
        (r'\bexec\s*\(', "exec()", "Code_Injection"),
        (r'\bos\.system\s*\(', "os.system()", "Command_Injection"),
        (r'\bos\.popen\s*\(', "os.popen()", "Command_Injection"),
        (r'subprocess\.\w+\(.*shell\s*=\s*True', "subprocess shell=True", "Command_Injection"),
        (r'pickle\.loads?\s*\(', "pickle.load()", "Deserialization"),
        (r'yaml\.load\s*\((?!.*Loader)', "yaml.load() without SafeLoader", "Deserialization"),
        (r'cursor\.execute\s*\(.*[fF]["\']|cursor\.execute\s*\(.*%\s*\(', "SQL string formatting", "SQL_Injection"),
        (r'__import__\s*\(', "__import__()", "Code_Injection"),
        (r'(password|secret|api_key|token)\s*=\s*["\'][^"\']+["\']', "hardcoded credential", "Credentials_Exposure"),
    ],
    ".js": [
        (r'\beval\s*\(', "eval()", "Code_Injection"),
        (r'\.innerHTML\s*=', "innerHTML assignment", "XSS"),
        (r'document\.write\s*\(', "document.write()", "XSS"),
        (r'\$\(\s*["\'].*\+', "jQuery selector injection", "XSS"),
        (r'child_process\.exec\s*\(', "child_process.exec()", "Command_Injection"),
        (r'new\s+Function\s*\(', "new Function()", "Code_Injection"),
        (r'(password|secret|api_key|token)\s*=\s*["\'][^"\']+["\']', "hardcoded credential", "Credentials_Exposure"),
    ],
    ".ts": [],  # .js ile aynı pattern'leri paylaşır
}
DANGEROUS_PATTERNS[".ts"] = DANGEROUS_PATTERNS[".js"]

@mcp.tool()
def analyze_project_vulnerabilities(directory_path: str) -> str:
    """
    Verilen projenin .py, .js, .ts dosyalarını tarayarak tehlikeli fonksiyon kullanımlarını tespit eder.

    Args:
        directory_path: Analiz edilecek projenin yerel sistemdeki tam yolu.
    """
    if not os.path.exists(directory_path):
        return f"Hata: {directory_path} dizini bulunamadı."

    findings = []
    scanned = 0

    for ext, patterns in DANGEROUS_PATTERNS.items():
        for filepath in glob.glob(os.path.join(directory_path, "**", f"*{ext}"), recursive=True):
            skip_markers = ("node_modules", ".venv", "venv", "__pycache__", ".git", "dist", "build")
            if any(marker in filepath.split(os.sep) for marker in skip_markers):
                continue
            scanned += 1
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()
            except OSError:
                continue
            for line_no, line in enumerate(lines, 1):
                for regex, label, vuln_type in patterns:
                    if re.search(regex, line):
                        findings.append({
                            "file": os.path.relpath(filepath, directory_path),
                            "line": line_no,
                            "pattern": label,
                            "type": vuln_type,
                            "code": line.strip()[:120],
                        })

    if not findings:
        return f"{scanned} dosya tarandı, tehlikeli pattern bulunamadı."

    # Wiki'den referans ekle
    vuln_types = set(f["type"] for f in findings)
    wiki_refs = {}
    for vt in vuln_types:
        ref = search_cyber_wiki(vt.replace("_", " "))
        if "sonuç bulunamadı" not in ref:
            wiki_refs[vt] = ref.split("\n")[0]

    out = [f"## SAST Tarama Sonucu — {len(findings)} bulgu, {scanned} dosya tarandı\n"]
    for f in findings[:30]:
        out.append(f"- **{f['type']}** | `{f['file']}:{f['line']}` | {f['pattern']}\n  `{f['code']}`")
    if len(findings) > 30:
        out.append(f"\n... ve {len(findings) - 30} bulgu daha.")

    if wiki_refs:
        out.append("\n### Wiki Referansları")
        for vt, ref in wiki_refs.items():
            out.append(f"- {vt}: {ref}")

    return "\n".join(out)

@mcp.tool()
def get_remediation_plan(vulnerability_name: str) -> str:
    """
    Bulunan bir zafiyetin nasıl kapatılacağına (remediation) dair wiki'den çözüm planı getirir.
    
    Args:
        vulnerability_name: Çözümü aranan zafiyet (örn: "IDOR", "CSRF")
    """
    # Basitçe wiki'de 'çözüm' veya 'remediation' kelimeleriyle arama yap
    return search_cyber_wiki(f"{vulnerability_name} çözüm")

SECURITY_HEADERS = [
    "Content-Security-Policy",
    "X-Frame-Options",
    "X-Content-Type-Options",
    "Strict-Transport-Security",
    "Permissions-Policy",
    "Referrer-Policy",
    "X-XSS-Protection",
]

@mcp.tool()
def run_basic_pentest(target: str) -> str:
    """
    Verilen URL'e HTTP isteği atarak header, cookie, form ve temel güvenlik analizini yapar.

    Args:
        target: Analiz edilecek web sitesi URL'i (örn: "https://example.com")
    """
    if not target.startswith(("http://", "https://")):
        target = "https://" + target

    ctx = _ssl_ctx()

    cookie_jar = CookieJar()
    opener = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(cookie_jar),
        urllib.request.HTTPSHandler(context=ctx),
    )

    req = urllib.request.Request(target, headers={"User-Agent": "SiberSelma/1.0"})
    try:
        resp = opener.open(req, timeout=10)
    except urllib.error.HTTPError as e:
        resp = e
    except Exception as e:
        return f"Bağlantı hatası: {e}"

    headers = dict(resp.headers)
    body = ""
    try:
        raw = resp.read()
        body = raw.decode("utf-8", errors="ignore")[:50000]
    except Exception:
        pass

    out = [f"## Temel Pentest Raporu — {target}\n"]

    # 1) HTTP durum
    out.append(f"**HTTP Durum:** {resp.status} {resp.reason if hasattr(resp, 'reason') else ''}")

    # 2) Güvenlik header analizi
    missing = []
    present = []
    for h in SECURITY_HEADERS:
        val = headers.get(h)
        if val:
            present.append(f"  - {h}: `{val}`")
        else:
            missing.append(h)

    out.append("\n### Güvenlik Header'ları")
    if present:
        out.append("**Mevcut:**")
        out.extend(present)
    if missing:
        out.append(f"**Eksik ({len(missing)}):** " + ", ".join(f"`{h}`" for h in missing))

    # 3) Cookie analizi
    cookies = list(cookie_jar)
    if cookies:
        out.append(f"\n### Cookie'ler ({len(cookies)})")
        for ck in cookies:
            flags = []
            if not ck.secure:
                flags.append("Secure YOK")
            if not ck.has_nonstandard_attr("HttpOnly") and not ck.has_nonstandard_attr("httponly"):
                flags.append("HttpOnly YOK")
            samesite = ck._rest.get("SameSite") or ck._rest.get("samesite") if hasattr(ck, "_rest") else None
            if not samesite:
                flags.append("SameSite YOK")
            warning = f" ⚠ {', '.join(flags)}" if flags else ""
            value_preview = (ck.value or "")[:20]
            out.append(f"  - `{ck.name}={value_preview}...`{warning}")

    # 4) Form tespiti
    forms = re.findall(r'<form[^>]*action=["\']([^"\']*)["\'][^>]*>', body, re.IGNORECASE)
    if forms:
        out.append(f"\n### Formlar ({len(forms)})")
        for action in forms[:10]:
            out.append(f"  - action=`{action}`")

    # 5) Server bilgisi
    server = headers.get("Server", "")
    powered = headers.get("X-Powered-By", "")
    if server or powered:
        out.append(f"\n### Sunucu Bilgisi (bilgi sızıntısı)")
        if server:
            out.append(f"  - Server: `{server}`")
        if powered:
            out.append(f"  - X-Powered-By: `{powered}`")

    # 6) HTTPS kontrolü
    if target.startswith("http://"):
        out.append("\n⚠ **Site HTTP üzerinden erişiliyor — şifreleme yok!**")

    # Wiki referansları
    wiki_terms = []
    if missing:
        wiki_terms.append("security headers")
    if any(not ck.secure for ck in cookies):
        wiki_terms.append("cookie security")
    if target.startswith("http://"):
        wiki_terms.append("HTTPS TLS")

    if wiki_terms:
        out.append("\n### Wiki Referansları")
        for term in wiki_terms:
            ref = search_cyber_wiki(term)
            if "sonuç bulunamadı" not in ref:
                out.append(f"- {term}: {ref.split(chr(10))[0]}")

    return "\n".join(out)

HEADER_RECOMMENDATIONS = {
    "Content-Security-Policy": "XSS ve veri enjeksiyonu saldırılarını önler. Önerilen: `default-src 'self'`",
    "X-Frame-Options": "Clickjacking saldırılarını önler. Önerilen: `DENY` veya `SAMEORIGIN`",
    "X-Content-Type-Options": "MIME-type sniffing'i önler. Önerilen: `nosniff`",
    "Strict-Transport-Security": "HTTPS kullanımını zorunlu kılar. Önerilen: `max-age=31536000; includeSubDomains`",
    "Permissions-Policy": "Tarayıcı özelliklerini (kamera, mikrofon vb.) kısıtlar.",
    "Referrer-Policy": "Referrer bilgi sızıntısını kontrol eder. Önerilen: `strict-origin-when-cross-origin`",
    "X-XSS-Protection": "Eski tarayıcılarda XSS filtresi. Önerilen: `1; mode=block`",
    "X-Permitted-Cross-Domain-Policies": "Flash/PDF cross-domain politikasını kontrol eder. Önerilen: `none`",
    "Cross-Origin-Opener-Policy": "Cross-origin pencere iletişimini kısıtlar. Önerilen: `same-origin`",
    "Cross-Origin-Resource-Policy": "Cross-origin kaynak paylaşımını kısıtlar. Önerilen: `same-origin`",
}

@mcp.tool()
def check_security_headers(url: str) -> str:
    """
    Bir web sitesinin HTTP güvenlik header'larını kontrol eder ve eksikleri raporlar.

    Args:
        url: Kontrol edilecek web sitesi URL'i (örn: "https://example.com")
    """
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    ctx = _ssl_ctx()

    req = urllib.request.Request(url, headers={"User-Agent": "SiberSelma/1.0"})
    try:
        resp = urllib.request.urlopen(req, timeout=10, context=ctx)
    except urllib.error.HTTPError as e:
        resp = e
    except Exception as e:
        return f"Bağlantı hatası: {e}"

    headers = dict(resp.headers)

    out = [f"## Güvenlik Header Raporu — {url}\n"]
    missing = []
    present = []

    for header, recommendation in HEADER_RECOMMENDATIONS.items():
        val = headers.get(header)
        if val:
            present.append(f"  - **{header}**: `{val}`")
        else:
            missing.append(f"  - **{header}**: {recommendation}")

    score = len(present) * 100 // len(HEADER_RECOMMENDATIONS)
    out.append(f"**Güvenlik Skoru:** {score}/100 ({len(present)}/{len(HEADER_RECOMMENDATIONS)} header mevcut)\n")

    if present:
        out.append(f"### Mevcut Header'lar ({len(present)})")
        out.extend(present)

    if missing:
        out.append(f"\n### Eksik Header'lar ({len(missing)})")
        out.extend(missing)

    # Tehlikeli header'lar
    dangerous = []
    if headers.get("Server"):
        dangerous.append(f"  - `Server: {headers['Server']}` — sunucu versiyonu ifşa ediliyor")
    if headers.get("X-Powered-By"):
        dangerous.append(f"  - `X-Powered-By: {headers['X-Powered-By']}` — framework ifşa ediliyor")
    if headers.get("X-AspNet-Version"):
        dangerous.append(f"  - `X-AspNet-Version: {headers['X-AspNet-Version']}` — .NET versiyonu ifşa ediliyor")

    if dangerous:
        out.append("\n### Bilgi Sızıntısı Yapan Header'lar")
        out.extend(dangerous)

    ref = search_cyber_wiki("security headers HTTP")
    if "sonuç bulunamadı" not in ref:
        out.append(f"\n### Wiki Referansı\n{ref.split(chr(10))[0]}")

    return "\n".join(out)


def _shannon_entropy(s: str) -> float:
    """Bir string için Shannon entropy değerini hesaplar (bit/karakter)."""
    if not s:
        return 0.0
    from math import log2
    freq = {}
    for ch in s:
        freq[ch] = freq.get(ch, 0) + 1
    n = len(s)
    return -sum((c / n) * log2(c / n) for c in freq.values())


SECRET_PATTERNS = [
    (r'(?:password|passwd|pwd)\s*[=:]\s*["\'][^"\']{3,}["\']', "Hardcoded password"),
    (r'(?:api_?key|apikey|api_?secret)\s*[=:]\s*["\'][^"\']{8,}["\']', "Hardcoded API key"),
    (r'(?:secret_?key|secret)\s*[=:]\s*["\'][^"\']{8,}["\']', "Hardcoded secret key"),
    (r'(?:access_?token|auth_?token|bearer)\s*[=:]\s*["\'][^"\']{8,}["\']', "Hardcoded token"),
    (r'(?:aws_access_key_id)\s*[=:]\s*["\']?AKIA[0-9A-Z]{16}', "AWS Access Key"),
    (r'(?:aws_secret_access_key)\s*[=:]\s*["\']?[A-Za-z0-9/+=]{40}', "AWS Secret Key"),
    (r'ghp_[A-Za-z0-9]{36}', "GitHub Personal Access Token"),
    (r'glpat-[A-Za-z0-9\-]{20,}', "GitLab Personal Access Token"),
    (r'sk-[A-Za-z0-9]{32,}', "OpenAI/Stripe Secret Key"),
    (r'xox[bpras]-[A-Za-z0-9\-]+', "Slack Token"),
    (r'-----BEGIN (?:RSA |EC |DSA )?PRIVATE KEY-----', "Private Key"),
    (r'(?:mysql|postgres|mongodb)://[^\s"\']+:[^\s"\']+@', "Database connection string with credentials"),
]

@mcp.tool()
def find_exposed_secrets(directory: str) -> str:
    """
    Kod dosyalarında hardcoded API key, token, şifre ve private key arar. .env dosyasının git'e eklenip eklenmediğini kontrol eder.

    Args:
        directory: Taranacak proje dizininin tam yolu.
    """
    if not os.path.exists(directory):
        return f"Hata: {directory} dizini bulunamadı."

    findings = []
    scanned = 0
    scan_extensions = {".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".go", ".rb", ".php", ".yaml", ".yml", ".toml", ".cfg", ".ini", ".conf", ".env", ".sh", ".bat", ".ps1"}
    skip_dirs = {
        "node_modules", ".venv", "venv", "__pycache__", ".git", "dist", "build", ".tox",
        # Wiki/cheatsheet/payload koleksiyonları — örnek payload'lar false-positive üretir
        "PayloadsAllTheThings", "OWASP-CheatSheets", "cheatsheets",
        "PentestGPT-main", "RedTeam-Tools-main", "Reverse-Engineering-main",
        "Awesome-Asset-Discovery-master", "90DaysOfCyberSecurity-main",
    }

    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for fname in files:
            ext = os.path.splitext(fname)[1].lower()
            if ext not in scan_extensions and fname not in {".env", ".env.local", ".env.production"}:
                continue
            filepath = os.path.join(root, fname)
            scanned += 1
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()
            except OSError:
                continue
            for line_no, line in enumerate(lines, 1):
                if line.strip().startswith("#") or line.strip().startswith("//"):
                    continue
                for regex, label in SECRET_PATTERNS:
                    m = re.search(regex, line, re.IGNORECASE)
                    if not m:
                        continue
                    # Tırnaklar arası değerin entropy'sini kontrol et — örnek/dummy'leri ele
                    val_match = re.search(r'["\']([^"\']{4,})["\']', m.group(0))
                    if val_match:
                        val = val_match.group(1)
                        # Çok düşük entropy = "password", "changeme", "your_key_here" gibi placeholder
                        # Private key ve özel pattern'lerde bu kontrol atlanır
                        if "PRIVATE KEY" not in label and "Database" not in label:
                            if _shannon_entropy(val) < 2.5:
                                continue
                    findings.append({
                        "file": os.path.relpath(filepath, directory),
                        "line": line_no,
                        "type": label,
                        "snippet": re.sub(r'["\'][^"\']{4,}["\']', '"***REDACTED***"', line.strip()[:120]),
                    })

    # .env git kontrolü
    env_warnings = []
    gitignore_path = os.path.join(directory, ".gitignore")
    env_in_gitignore = False
    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r", encoding="utf-8", errors="ignore") as f:
            gitignore_content = f.read()
        env_in_gitignore = ".env" in gitignore_content

    env_files = glob.glob(os.path.join(directory, ".env*"))
    if env_files and not env_in_gitignore:
        env_warnings.append("`.env` dosyası mevcut ama `.gitignore`'da yok — git'e commit edilmiş olabilir!")

    out = [f"## Secret Tarama Raporu — {scanned} dosya tarandı\n"]

    if env_warnings:
        out.append("### .env Uyarıları")
        for w in env_warnings:
            out.append(f"  - {w}")

    if findings:
        out.append(f"\n### Bulunan Secret'lar ({len(findings)})")
        for f in findings[:30]:
            out.append(f"- **{f['type']}** | `{f['file']}:{f['line']}`\n  `{f['snippet']}`")
        if len(findings) > 30:
            out.append(f"\n... ve {len(findings) - 30} bulgu daha.")
    else:
        out.append("Hardcoded secret bulunamadı.")

    ref = search_cyber_wiki("credentials exposure secrets")
    if "sonuç bulunamadı" not in ref:
        out.append(f"\n### Wiki Referansı\n{ref.split(chr(10))[0]}")

    return "\n".join(out)


NVD_API_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"

def _parse_requirements_txt(filepath):
    """requirements.txt'i (paket, sürüm) çiftleri olarak döndürür. Sürüm yoksa None."""
    packages = []
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.split("#", 1)[0].strip()
            if not line or line.startswith("-"):
                continue
            # name==1.2.3, name>=1.2, name~=1.2 vb.
            m = re.match(r'^([A-Za-z0-9_\-\.]+)\s*(?:==|>=|<=|~=|!=)?\s*([0-9][0-9A-Za-z\.\-+]*)?', line)
            if m:
                packages.append((m.group(1), m.group(2)))
    return packages


def _parse_package_json(filepath):
    """package.json'ı (paket, sürüm) çiftleri olarak döndürür."""
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        data = json.load(f)
    packages = []
    for section in ("dependencies", "devDependencies"):
        deps = data.get(section, {})
        for name, ver in deps.items():
            # ^1.2.3 / ~1.2.3 / 1.2.3 — operator'leri sıyır
            clean = re.sub(r'^[\^~><=\s]+', '', str(ver)).strip() or None
            packages.append((name, clean))
    return packages

@mcp.tool()
def check_dependencies(file_path: str) -> str:
    """
    requirements.txt veya package.json dosyasındaki bağımlılıkları NVD API ile bilinen CVE'lere karşı kontrol eder.

    Args:
        file_path: requirements.txt veya package.json dosyasının tam yolu.
    """
    if not os.path.exists(file_path):
        return f"Hata: {file_path} dosyası bulunamadı."

    fname = os.path.basename(file_path).lower()
    if fname == "requirements.txt":
        packages = _parse_requirements_txt(file_path)
    elif fname == "package.json":
        try:
            packages = _parse_package_json(file_path)
        except json.JSONDecodeError:
            return "Hata: package.json geçerli JSON değil."
    else:
        return "Hata: Desteklenen dosya tipleri: requirements.txt, package.json"

    if not packages:
        return "Dosyada bağımlılık bulunamadı."

    import time
    ctx = _ssl_ctx()

    nvd_key = os.environ.get("NVD_API_KEY", "")
    # NVD limiti: API key'siz 30 sn'de 5 istek; key ile 30 sn'de 50 istek.
    sleep_between = 0.7 if nvd_key else 6.5

    out = [f"## Bağımlılık CVE Raporu — {len(packages)} paket kontrol ediliyor\n"]
    vuln_count = 0
    checked = 0
    errors = 0

    for idx, pkg_entry in enumerate(packages[:20]):
        if isinstance(pkg_entry, tuple):
            pkg_name, pkg_ver = pkg_entry
        else:
            pkg_name, pkg_ver = pkg_entry, None
        if idx > 0:
            time.sleep(sleep_between)
        try:
            # CPE-based query (sürüm varsa) — keyword'den çok daha az false-positive üretir
            if pkg_ver:
                cpe = f"cpe:2.3:a:*:{pkg_name.lower()}:{pkg_ver}:*:*:*:*:*:*:*"
                api_url = f"{NVD_API_URL}?cpeName={urllib.request.quote(cpe)}&resultsPerPage=5"
            else:
                # Sürüm yok → virtualMatchString ile ürün adına göre dene
                vms = f"cpe:2.3:a:*:{pkg_name.lower()}:*:*:*:*:*:*:*:*"
                api_url = f"{NVD_API_URL}?virtualMatchString={urllib.request.quote(vms)}&resultsPerPage=5"

            headers = {"User-Agent": "SiberSelma/1.0"}
            if nvd_key:
                headers["apiKey"] = nvd_key
            req = urllib.request.Request(api_url, headers=headers)
            resp = urllib.request.urlopen(req, timeout=15, context=ctx)
            data = json.loads(resp.read().decode("utf-8"))
            checked += 1

            total = data.get("totalResults", 0)
            label = f"{pkg_name}=={pkg_ver}" if pkg_ver else pkg_name
            if total > 0:
                vuln_count += 1
                out.append(f"\n### {label} — {total} CVE bulundu")
                for vuln in data.get("vulnerabilities", [])[:3]:
                    cve = vuln.get("cve", {})
                    cve_id = cve.get("id", "?")
                    desc_list = cve.get("descriptions", [])
                    desc = next((d["value"] for d in desc_list if d.get("lang") == "en"), "")[:150]
                    metrics = cve.get("metrics", {})
                    score = "?"
                    for metric_key in ("cvssMetricV31", "cvssMetricV30", "cvssMetricV2"):
                        if metric_key in metrics and metrics[metric_key]:
                            score = metrics[metric_key][0].get("cvssData", {}).get("baseScore", "?")
                            break
                    out.append(f"  - **{cve_id}** (CVSS: {score}) — {desc}")
        except Exception:
            errors += 1
            continue

    summary = f"\n---\n**Özet:** {checked}/{len(packages[:20])} paket kontrol edildi, {vuln_count} pakette CVE bulundu"
    if errors:
        summary += f", {errors} paket kontrol edilemedi (API hatası)"
    if len(packages) > 20:
        summary += f"\n⚠ İlk 20 paket kontrol edildi, toplam {len(packages)} paket var"
    out.insert(1, summary)

    return "\n".join(out)


from datetime import datetime

@mcp.tool()
def generate_security_report(url: str, directory: str, output_format: str = "markdown") -> str:
    """
    Tüm güvenlik tool'larını sırayla çalıştırarak kapsamlı bir güvenlik raporu üretir ve
    security_report_YYYY-MM-DD.md (veya .json) dosyasına kaydeder.

    Args:
        url: Analiz edilecek web sitesi URL'i (örn: "https://example.com")
        directory: Analiz edilecek proje dizininin tam yolu
        output_format: "markdown" (default) veya "json"
    """
    date_str = datetime.now().strftime("%Y-%m-%d")
    ext = "json" if output_format == "json" else "md"
    report_path = os.path.join(BASE_DIR, f"security_report_{date_str}.{ext}")

    header_lines = []
    sections = []
    critical = 0
    high = 0
    medium = 0

    header_lines.append(f"# Güvenlik Raporu — {date_str}")
    header_lines.append(f"**Hedef URL:** {url}  ")
    header_lines.append(f"**Proje Dizini:** {directory}  ")
    header_lines.append(f"**Oluşturulma:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
    header_lines.append("---\n")

    # 1) Temel Pentest
    sections.append("## 1. Web Uygulama Analizi")
    try:
        pentest_result = run_basic_pentest(url)
        sections.append(pentest_result)
        # Basit bulgu sayacı
        if "Eksik" in pentest_result:
            m = re.search(r'Eksik \((\d+)\)', pentest_result)
            if m:
                medium += int(m.group(1))
    except Exception as e:
        sections.append(f"Hata: {e}")

    sections.append("\n---\n")

    # 2) SAST Kod Analizi
    sections.append("## 2. Statik Kod Analizi (SAST)")
    try:
        sast_result = analyze_project_vulnerabilities(directory)
        sections.append(sast_result)
        m = re.search(r'(\d+) bulgu', sast_result)
        if m:
            count = int(m.group(1))
            high += count // 2
            medium += count - count // 2
    except Exception as e:
        sections.append(f"Hata: {e}")

    sections.append("\n---\n")

    # 3) Güvenlik Header'ları
    sections.append("## 3. HTTP Güvenlik Header'ları")
    try:
        header_result = check_security_headers(url)
        sections.append(header_result)
        m = re.search(r'Eksik Header.*?(\d+)', header_result)
        if m:
            medium += int(m.group(1))
    except Exception as e:
        sections.append(f"Hata: {e}")

    sections.append("\n---\n")

    # 4) Bağımlılık CVE Kontrolü
    sections.append("## 4. Bağımlılık CVE Analizi")
    dep_file = None
    for candidate in ["requirements.txt", "package.json"]:
        candidate_path = os.path.join(directory, candidate)
        if os.path.exists(candidate_path):
            dep_file = candidate_path
            break

    if dep_file:
        try:
            dep_result = check_dependencies(dep_file)
            sections.append(dep_result)
            m = re.search(r'(\d+) pakette CVE', dep_result)
            if m:
                critical += int(m.group(1))
        except Exception as e:
            sections.append(f"Hata: {e}")
    else:
        sections.append("requirements.txt veya package.json bulunamadı.")

    sections.append("\n---\n")

    # 5) Secret Tarama
    sections.append("## 5. Hardcoded Secret Tarama")
    try:
        secret_result = find_exposed_secrets(directory)
        sections.append(secret_result)
        m = re.search(r'Bulunan Secret.*?(\d+)', secret_result)
        if m:
            critical += int(m.group(1))
    except Exception as e:
        sections.append(f"Hata: {e}")

    sections.append("\n---\n")

    # Özet bölümü (raporun başına ekle)
    summary_lines = [
        "## Özet",
        f"| Seviye | Sayı |",
        f"|--------|------|",
        f"| 🔴 Kritik | {critical} |",
        f"| 🟠 Yüksek | {high} |",
        f"| 🟡 Orta | {medium} |",
        "",
        "### Öncelikli Düzeltme Adımları",
    ]
    if critical > 0:
        summary_lines.append("1. Hardcoded secret ve CVE bulunan bağımlılıkları acilen temizle")
    if high > 0:
        summary_lines.append("2. SAST bulgularındaki yüksek riskli kod pattern'lerini düzelt")
    if medium > 0:
        summary_lines.append("3. Eksik HTTP güvenlik header'larını ekle")
    summary_lines.append("\n---\n")

    # Özeti başlık ile bölümler arasına yerleştir
    full_report = "\n".join(header_lines + summary_lines + sections)

    if output_format == "json":
        report_obj = {
            "date": date_str,
            "target_url": url,
            "project_dir": directory,
            "summary": {"critical": critical, "high": high, "medium": medium},
            "sections": {
                "pentest": sections[1] if len(sections) > 1 else "",
                "sast": sections[3] if len(sections) > 3 else "",
                "headers": sections[5] if len(sections) > 5 else "",
                "dependencies": sections[7] if len(sections) > 7 else "",
                "secrets": sections[9] if len(sections) > 9 else "",
            },
        }
        try:
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(report_obj, f, ensure_ascii=False, indent=2)
            return json.dumps(report_obj, ensure_ascii=False, indent=2) + f"\n\n---\nRapor kaydedildi: {report_path}"
        except OSError as e:
            return json.dumps(report_obj, ensure_ascii=False, indent=2) + f"\n\n---\nUyarı: Rapor dosyaya kaydedilemedi ({e})"

    try:
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(full_report)
        return f"{full_report}\n\n---\n**Rapor kaydedildi:** `{report_path}`"
    except OSError as e:
        return f"{full_report}\n\n---\nUyarı: Rapor dosyaya kaydedilemedi ({e})"


@mcp.tool()
def find_subdomains(domain: str) -> str:
    """
    crt.sh SSL sertifika loglarını kullanarak bir domain'in subdomain'lerini keşfeder.

    Args:
        domain: Taranacak domain (örn: "example.com")
    """
    domain = domain.strip().removeprefix("https://").removeprefix("http://").split("/")[0]
    url = f"https://crt.sh/?q=%.{urllib.request.quote(domain)}&output=json"

    cached = _cache_get("crtsh", domain)
    if cached:
        try:
            data = json.loads(cached)
        except Exception:
            data = None
    else:
        data = None

    if data is None:
        ctx = _ssl_ctx()
        req = urllib.request.Request(url, headers={"User-Agent": "SiberSelma/1.0"})
        try:
            resp = urllib.request.urlopen(req, timeout=15, context=ctx)
            raw = resp.read().decode("utf-8")
            data = json.loads(raw)
            _cache_set("crtsh", domain, raw)
        except Exception as e:
            return f"crt.sh sorgusu basarisiz: {e}"

    subdomains = set()
    for entry in data:
        name = entry.get("name_value", "")
        for sub in name.split("\n"):
            sub = sub.strip().lstrip("*.")
            if sub.endswith(domain) and sub != domain:
                subdomains.add(sub)

    if not subdomains:
        return f"'{domain}' icin subdomain bulunamadi."

    sorted_subs = sorted(subdomains)
    out = [f"## Subdomain Kesfedildi — {domain} ({len(sorted_subs)} adet)\n"]
    for s in sorted_subs[:50]:
        out.append(f"  - `{s}`")
    if len(sorted_subs) > 50:
        out.append(f"\n... ve {len(sorted_subs) - 50} subdomain daha.")

    ref = search_cyber_wiki("subdomain enumeration OSINT")
    if "sonuc bulunamadi" not in ref:
        out.append(f"\n### Wiki Referansi\n{ref.split(chr(10))[0]}")

    return "\n".join(out)


@mcp.tool()
def check_history(url: str) -> str:
    """
    Wayback Machine API ile bir URL'nin gecmis snapshot'larini sorgular; eski endpoint veya konfigurasyon dosyasi olup olmadigini arastirir.

    Args:
        url: Sorgulanacak URL (örn: "https://example.com/admin")
    """
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    api_url = f"https://archive.org/wayback/available?url={urllib.request.quote(url, safe=':/')}"
    ctx = _ssl_ctx()

    req = urllib.request.Request(api_url, headers={"User-Agent": "SiberSelma/1.0"})
    try:
        resp = urllib.request.urlopen(req, timeout=15, context=ctx)
        data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return f"Wayback Machine sorgusu basarisiz: {e}"

    snapshot = data.get("archived_snapshots", {}).get("closest", {})
    out = [f"## Wayback Machine — {url}\n"]

    if not snapshot or not snapshot.get("available"):
        out.append("Bu URL icin arsiv kaydı bulunamadi.")
    else:
        ts = snapshot.get("timestamp", "")
        archive_url = snapshot.get("url", "")
        date_fmt = f"{ts[:4]}-{ts[4:6]}-{ts[6:8]} {ts[8:10]}:{ts[10:12]}" if len(ts) >= 12 else ts
        out.append(f"**En yakin snapshot:** {date_fmt}")
        out.append(f"**Arsiv URL:** {archive_url}")

        # Hassas yollari kontrol et
        sensitive_paths = [".env", "config", "backup", "admin", ".git", "wp-config", "phpinfo", ".htaccess", "database"]
        flagged = [p for p in sensitive_paths if p in url.lower()]
        if flagged:
            out.append(f"\n**Dikkat:** URL hassas yol iceriyor: {', '.join(flagged)}")
            out.append("Bu yolun arsivde aciga cikmis icerik barindirip barindirmadigini manuel kontrol et.")

    # Birden fazla yolu toplu sorgula
    common_sensitive = [".env", ".git/config", "backup.zip", "wp-config.php", "phpinfo.php", "admin/", "robots.txt"]
    base = url.rstrip("/")
    base_domain = "/".join(base.split("/")[:3])
    found_paths = []

    for path in common_sensitive:
        check_url = f"https://archive.org/wayback/available?url={urllib.request.quote(base_domain + '/' + path, safe=':/')}"
        try:
            r = urllib.request.urlopen(
                urllib.request.Request(check_url, headers={"User-Agent": "SiberSelma/1.0"}),
                timeout=8, context=ctx
            )
            d = json.loads(r.read().decode("utf-8"))
            snap = d.get("archived_snapshots", {}).get("closest", {})
            if snap.get("available"):
                found_paths.append((path, snap.get("url", "")))
        except Exception:
            continue

    if found_paths:
        out.append(f"\n### Arsivde Bulunan Hassas Yollar ({len(found_paths)})")
        for path, archive in found_paths:
            out.append(f"  - `/{path}` → {archive}")

    return "\n".join(out)


@mcp.tool()
def run_nuclei_scan(target: str, severity: str = "medium,high,critical", timeout_sec: int = 120) -> str:
    """
    nuclei tarayicisini lokal olarak calistirir (yuklu olmasi gerekir).
    nuclei kurulumu: https://github.com/projectdiscovery/nuclei

    Args:
        target: Taranacak URL
        severity: Virgulle ayrilmis seviye listesi (info, low, medium, high, critical)
        timeout_sec: Taramanin maksimum suresi (saniye)
    """
    import shutil
    import subprocess

    if not shutil.which("nuclei"):
        return (
            "nuclei bulunamadi. Kurulum:\n"
            "  go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest\n"
            "  veya: https://github.com/projectdiscovery/nuclei/releases"
        )

    if not target.startswith(("http://", "https://")):
        target = "https://" + target

    cmd = ["nuclei", "-u", target, "-silent", "-jsonl", "-severity", severity, "-timeout", "10"]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_sec)
    except subprocess.TimeoutExpired:
        return f"nuclei zaman asimina ugradi ({timeout_sec}s)."
    except Exception as e:
        return f"nuclei calistirilamadi: {e}"

    findings = []
    for line in (proc.stdout or "").splitlines():
        try:
            obj = json.loads(line)
            findings.append({
                "template": obj.get("template-id") or obj.get("templateID", ""),
                "severity": obj.get("info", {}).get("severity", ""),
                "name": obj.get("info", {}).get("name", ""),
                "matched": obj.get("matched-at") or obj.get("matched", ""),
            })
        except Exception:
            continue

    out = [f"## Nuclei Tarama — {target}\n"]
    if not findings:
        out.append("Hicbir bulgu yok.")
        if proc.returncode != 0 and proc.stderr:
            out.append(f"\nstderr: {proc.stderr[:500]}")
        return "\n".join(out)

    by_sev = {}
    for f in findings:
        by_sev.setdefault(f["severity"], []).append(f)

    out.append(f"**Toplam bulgu:** {len(findings)}\n")
    for sev in ("critical", "high", "medium", "low", "info"):
        if sev not in by_sev:
            continue
        out.append(f"### {sev.upper()} ({len(by_sev[sev])})")
        for f in by_sev[sev][:10]:
            out.append(f"  - **{f['name']}** ({f['template']}) → `{f['matched']}`")

    return "\n".join(out)


@mcp.tool()
def run_zap_baseline(target: str, zap_url: str = "http://localhost:8080") -> str:
    """
    OWASP ZAP'in baslattigi REST API'yi kullanarak baseline (passive) tarama yapar.
    ZAP'in arkaplanda calismasi gerekir: zap.sh -daemon -port 8080 -config api.disablekey=true

    Args:
        target: Taranacak URL
        zap_url: ZAP API endpoint'i (varsayilan: http://localhost:8080)
    """
    if not target.startswith(("http://", "https://")):
        target = "https://" + target

    ctx = _ssl_ctx()
    api_key = os.environ.get("ZAP_API_KEY", "")
    api_suffix = f"&apikey={urllib.request.quote(api_key)}" if api_key else ""

    spider_url = f"{zap_url}/JSON/spider/action/scan/?url={urllib.request.quote(target)}{api_suffix}"
    alerts_url = f"{zap_url}/JSON/core/view/alerts/?baseurl={urllib.request.quote(target)}{api_suffix}"

    try:
        req = urllib.request.Request(spider_url, headers={"User-Agent": "SiberSelma/1.0"})
        urllib.request.urlopen(req, timeout=10, context=ctx).read()
    except Exception as e:
        return f"ZAP API'ye baglanilamadi ({zap_url}): {e}\nZAP'in -daemon modunda calistigindan emin olun."

    # Spider'in bitmesini bekle
    import time as _time
    _time.sleep(5)

    try:
        req = urllib.request.Request(alerts_url, headers={"User-Agent": "SiberSelma/1.0"})
        resp = urllib.request.urlopen(req, timeout=15, context=ctx)
        data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return f"ZAP alerts alinamadi: {e}"

    alerts = data.get("alerts", [])
    if not alerts:
        return f"## ZAP Baseline — {target}\n\nHicbir uyari yok."

    by_risk = {}
    for a in alerts:
        risk = a.get("risk", "Informational")
        by_risk.setdefault(risk, []).append(a)

    out = [f"## ZAP Baseline Tarama — {target}\n", f"**Toplam uyari:** {len(alerts)}\n"]
    for risk in ("High", "Medium", "Low", "Informational"):
        if risk not in by_risk:
            continue
        out.append(f"### {risk} ({len(by_risk[risk])})")
        for a in by_risk[risk][:8]:
            out.append(f"  - **{a.get('name', '?')}** → `{a.get('url', '')[:80]}`")

    return "\n".join(out)


@mcp.tool()
def batch_scan_attack_surface(domain: str, max_subdomains: int = 10) -> str:
    """
    Bir domain'in subdomain'lerini kesfeder, her birini security header taramasindan gecirir
    ve toplu sonuc raporu uretir.

    Args:
        domain: Kok domain (orn: "example.com")
        max_subdomains: Header taramasi yapilacak maksimum subdomain sayisi (varsayilan: 10)
    """
    domain = domain.strip().removeprefix("https://").removeprefix("http://").split("/")[0]
    sub_result = find_subdomains(domain)

    # find_subdomains ciktisindan subdomain'leri cikar
    found = re.findall(r'`([a-zA-Z0-9\.\-]+\.' + re.escape(domain) + r')`', sub_result)
    if not found:
        return f"## Toplu Saldiri Yuzeyi Taramasi — {domain}\n\nSubdomain bulunamadi.\n\n{sub_result}"

    targets = list(dict.fromkeys(found))[:max_subdomains]

    out = [f"## Toplu Saldiri Yuzeyi Taramasi — {domain}\n"]
    out.append(f"**Kesfedilen subdomain:** {len(found)} (header taramasi: {len(targets)})\n")

    summary_rows = []
    for sub in targets:
        url = f"https://{sub}"
        try:
            header_result = check_security_headers(url)
            score_match = re.search(r'Guvenlik Skoru:\*?\*?\s*(\d+)/100', header_result)
            score = int(score_match.group(1)) if score_match else 0
            missing_match = re.search(r'Eksik Header.*?\((\d+)\)', header_result)
            missing = int(missing_match.group(1)) if missing_match else 0
            summary_rows.append((sub, score, missing, "OK"))
        except Exception as e:
            summary_rows.append((sub, 0, 0, f"hata: {e}"))

    summary_rows.sort(key=lambda r: r[1])

    out.append("| Subdomain | Skor | Eksik Header | Durum |")
    out.append("|-----------|------|--------------|-------|")
    for sub, score, missing, status in summary_rows:
        out.append(f"| `{sub}` | {score}/100 | {missing} | {status} |")

    weak = [r for r in summary_rows if r[1] < 50 and r[3] == "OK"]
    if weak:
        out.append(f"\n### Dikkat — Skoru 50 altinda {len(weak)} subdomain")
        for sub, score, _, _ in weak:
            out.append(f"  - `{sub}` ({score}/100)")

    return "\n".join(out)


@mcp.tool()
def check_threat(target: str) -> str:
    """
    AlienVault OTX API ile bir IP adresi veya domain'in tehdit gecmisini sorgular.

    Args:
        target: Sorgulanacak IP adresi veya domain (örn: "8.8.8.8" veya "example.com")
    """
    target = target.strip()
    is_ip = bool(re.match(r'^\d{1,3}(\.\d{1,3}){3}$', target))
    endpoint_type = "IPv4" if is_ip else "domain"
    api_url = f"https://otx.alienvault.com/api/v1/indicators/{endpoint_type}/{urllib.request.quote(target)}/general"

    cached = _cache_get("otx", target)
    if cached:
        try:
            data = json.loads(cached)
        except Exception:
            data = None
    else:
        data = None

    if data is not None:
        return _format_otx_report(target, data)

    ctx = _ssl_ctx()

    otx_headers = {"User-Agent": "SiberSelma/1.0"}
    otx_key = os.environ.get("ALIENVAULT_OTX_KEY", "")
    if otx_key:
        otx_headers["X-OTX-API-KEY"] = otx_key

    req = urllib.request.Request(api_url, headers=otx_headers)
    try:
        resp = urllib.request.urlopen(req, timeout=15, context=ctx)
        raw = resp.read().decode("utf-8")
        data = json.loads(raw)
        _cache_set("otx", target, raw)
    except urllib.error.HTTPError as e:
        if e.code == 401:
            return "OTX API key gerekli. ALIENVAULT_OTX_KEY ortam degiskeni olarak tanimlayin."
        if e.code == 403:
            return "OTX erisimi reddedildi. ALIENVAULT_OTX_KEY gecersiz olabilir."
        return f"OTX sorgusu basarisiz: HTTP {e.code}"
    except Exception as e:
        return f"OTX sorgusu basarisiz: {e}"

    return _format_otx_report(target, data)


def _format_otx_report(target: str, data: dict) -> str:
    out = [f"## AlienVault OTX Tehdit Raporu — {target}\n"]

    pulse_count = data.get("pulse_info", {}).get("count", 0)
    reputation = data.get("reputation", 0)
    country = data.get("country_name", "Bilinmiyor")
    asn = data.get("asn", "")

    out.append(f"**Ulke:** {country}  ")
    out.append(f"**ASN:** {asn}  ")
    out.append(f"**Itibar Skoru:** {reputation}  ")
    out.append(f"**Tehdit Pulse Sayisi:** {pulse_count}\n")

    if pulse_count > 0:
        out.append("**Uyari:** Bu hedef tehdit istihbarat veri tabanlarinda yer aliyor!")
        pulses = data.get("pulse_info", {}).get("pulses", [])[:5]
        if pulses:
            out.append("\n### Ilgili Tehdit Pulse'lari")
            for p in pulses:
                out.append(f"  - {p.get('name', '?')} ({p.get('created', '')[:10]})")
    else:
        out.append("Bilinen tehdit kaydi bulunamadi.")

    malware = data.get("malware", [])
    if malware:
        out.append(f"\n**Iliskili Malware:** {len(malware)} kayit")

    return "\n".join(out)


@mcp.tool()
def get_attack_techniques(vulnerability: str) -> str:
    """
    MITRE ATT&CK Enterprise matrisini kullanarak bir zafiyet veya kavram icin saldirgan taktik ve tekniklerini listeler.

    Args:
        vulnerability: Aranacak zafiyet veya saldiri turu (örn: "XSS", "SQL Injection", "phishing")
    """
    # MITRE ATT&CK STIX/JSON endpoint (enterprise) — 24h lokal cache
    api_url = "https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json"
    cache_dir = os.path.join(BASE_DIR, ".cache")
    cache_path = os.path.join(cache_dir, "mitre_enterprise_attack.json")
    cache_ttl_seconds = 24 * 3600

    data = None
    try:
        if os.path.exists(cache_path):
            age = (datetime.now().timestamp() - os.path.getmtime(cache_path))
            if age < cache_ttl_seconds:
                with open(cache_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
    except Exception:
        data = None

    if data is None:
        ctx = _ssl_ctx()
        req = urllib.request.Request(api_url, headers={"User-Agent": "SiberSelma/1.0"})
        try:
            resp = urllib.request.urlopen(req, timeout=20, context=ctx)
            raw = resp.read().decode("utf-8")
            data = json.loads(raw)
            try:
                os.makedirs(cache_dir, exist_ok=True)
                with open(cache_path, "w", encoding="utf-8") as f:
                    f.write(raw)
            except OSError:
                pass
        except Exception as e:
            return f"MITRE ATT&CK verisi alinamadi: {e}"

    query = vulnerability.lower()
    matches = []

    for obj in data.get("objects", []):
        if obj.get("type") != "attack-pattern":
            continue
        name = obj.get("name", "").lower()
        desc = obj.get("description", "").lower()
        if query in name or query in desc:
            ext_refs = obj.get("external_references", [])
            attack_id = next((r.get("external_id", "") for r in ext_refs if r.get("source_name") == "mitre-attack"), "")
            tactic_refs = [p.get("phase_name", "") for p in obj.get("kill_chain_phases", [])]
            matches.append({
                "id": attack_id,
                "name": obj.get("name", ""),
                "tactics": tactic_refs,
                "desc": obj.get("description", "")[:200],
            })

    if not matches:
        return f"'{vulnerability}' icin MITRE ATT&CK'te teknik bulunamadi."

    out = [f"## MITRE ATT&CK Teknikleri — '{vulnerability}' ({len(matches)} eslesme)\n"]
    for m in matches[:10]:
        tactics_str = ", ".join(m["tactics"]) if m["tactics"] else "bilinmiyor"
        out.append(f"### {m['id']} — {m['name']}")
        out.append(f"**Taktikler:** {tactics_str}")
        out.append(f"{m['desc']}...\n")

    ref = search_cyber_wiki(vulnerability)
    if "sonuc bulunamadi" not in ref:
        out.append(f"### Wiki Referansi\n{ref.split(chr(10))[0]}")

    return "\n".join(out)


@mcp.tool()
def check_breach(email: str) -> str:
    """
    Have I Been Pwned API ile bir e-posta adresinin veri ihlallerinde gorünüp gorunmedigini sorgular.
    HIBP_API_KEY ortam degiskeni gereklidir.

    Args:
        email: Sorgulanacak e-posta adresi
    """
    api_key = os.environ.get("HIBP_API_KEY", "")
    if not api_key:
        return (
            "Have I Been Pwned API key bulunamadi.\n"
            "Lutfen HIBP_API_KEY ortam degiskenini tanimlayin:\n"
            "  https://haveibeenpwned.com/API/Key adresinden ucretsiz key alin."
        )

    encoded = urllib.request.quote(email)
    api_url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{encoded}?truncateResponse=false"

    ctx = _ssl_ctx()

    req = urllib.request.Request(api_url, headers={
        "User-Agent": "SiberSelma/1.0",
        "hibp-api-key": api_key,
    })
    try:
        resp = urllib.request.urlopen(req, timeout=15, context=ctx)
        data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return f"'{email}' bilinen veri ihlallerinde bulunamadi."
        if e.code == 401:
            return "Gecersiz HIBP API key."
        if e.code == 429:
            retry_after = e.headers.get("Retry-After", "?") if hasattr(e, "headers") else "?"
            return f"HIBP rate limit asıldı. Retry-After: {retry_after} sn."
        return f"HIBP sorgusu basarisiz: HTTP {e.code}"
    except Exception as e:
        return f"HIBP sorgusu basarisiz: {e}"

    out = [f"## Have I Been Pwned — {email}\n"]
    out.append(f"**{len(data)} veri ihlalinde bulundu!**\n")

    critical_breaches = [b for b in data if b.get("IsVerified") and not b.get("IsSensitive")]
    for breach in sorted(critical_breaches, key=lambda x: x.get("BreachDate", ""), reverse=True)[:10]:
        name = breach.get("Name", "?")
        date = breach.get("BreachDate", "?")
        pwn_count = breach.get("PwnCount", 0)
        data_classes = ", ".join(breach.get("DataClasses", [])[:5])
        out.append(f"### {name} ({date})")
        out.append(f"  - Etkilenen hesap: {pwn_count:,}")
        out.append(f"  - Ele gecen veri: {data_classes}\n")

    ref = search_cyber_wiki("credential stuffing breach")
    if "sonuc bulunamadi" not in ref:
        out.append(f"### Wiki Referansi\n{ref.split(chr(10))[0]}")

    return "\n".join(out)


@mcp.tool()
def fetch_security_news(max_items: int = 10) -> str:
    """
    The Hacker News ve BleepingComputer RSS feed'lerinden guncel siber guvenlik haberlerini ceker ve docs/wiki/news/ altina kaydeder.

    Args:
        max_items: Her kaynaktan alinacak maksimum haber sayisi (varsayilan: 10)
    """
    try:
        import feedparser
    except ImportError:
        return "feedparser yuklu degil. `pip install feedparser` calistirin."

    feeds = [
        ("The Hacker News", "https://feeds.feedburner.com/TheHackersNews"),
        ("BleepingComputer", "https://www.bleepingcomputer.com/feed/"),
    ]

    news_dir = os.path.join(WIKI_DIR, "news")
    os.makedirs(news_dir, exist_ok=True)

    out = ["## Guvenlik Haberleri\n"]
    total_saved = 0

    for source_name, feed_url in feeds:
        out.append(f"### {source_name}")
        try:
            parsed_feed = feedparser.parse(feed_url, agent="SiberSelma/1.0")
        except Exception as e:
            out.append(f"Feed alinamadi: {e}\n")
            continue

        if parsed_feed.bozo and not parsed_feed.entries:
            out.append(f"Feed parse edilemedi: {parsed_feed.bozo_exception}\n")
            continue

        saved_count = 0

        for entry in parsed_feed.entries[:max_items]:
            title = (entry.get("title") or "").strip()
            link = (entry.get("link") or "").strip()
            desc_raw = entry.get("summary") or entry.get("description") or ""
            desc = re.sub(r'<[^>]+>', '', desc_raw).strip()[:500]
            pub_date = entry.get("published") or entry.get("updated") or ""

            if not title:
                continue

            out.append(f"- **{title}** ({pub_date[:16]})")

            # Dosya adi olustur
            safe_title = re.sub(r'[^\w\s-]', '', title)[:60].strip().replace(' ', '_')
            date_prefix = datetime.now().strftime("%Y-%m-%d")
            fname = f"{date_prefix}_{safe_title}.md"
            fpath = os.path.join(news_dir, fname)

            if not os.path.exists(fpath):
                md_content = f"# {title}\n\n**Kaynak:** {source_name}  \n**Tarih:** {pub_date}  \n**URL:** {link}\n\n## Ozet\n\n{desc}\n"
                try:
                    with open(fpath, "w", encoding="utf-8") as f:
                        f.write(md_content)
                    saved_count += 1
                    total_saved += 1
                except OSError:
                    pass

        out.append(f"  ({saved_count} yeni haber kaydedildi)\n")

    out.append(f"\n**Toplam {total_saved} yeni haber `docs/wiki/news/` altina kaydedildi.**")
    if total_saved > 0:
        out.append("Haberleri aranabilir yapmak icin `python ingest.py` calistirin.")

    return "\n".join(out)


def auto_cve_scan_to_wiki(verbose: bool = False) -> dict:
    """
    Server baslangicinda requirements.txt'i NVD'ye sorar, ilk kez gorulen CVE'leri
    docs/wiki/cve/CVE-XXXX-YYYYY.md olarak yazar.
    """
    req_path = os.path.join(BASE_DIR, "requirements.txt")
    if not os.path.exists(req_path):
        return {"new_cves": 0, "skipped": True}

    cve_dir = os.path.join(WIKI_DIR, "cve")
    os.makedirs(cve_dir, exist_ok=True)

    nvd_key = os.environ.get("NVD_API_KEY", "")
    sleep_between = 0.7 if nvd_key else 6.5
    ctx = _ssl_ctx()

    packages = _parse_requirements_txt(req_path)
    new_cve_count = 0
    queried = 0

    import time as _time
    for idx, (pkg_name, pkg_ver) in enumerate(packages):
        if not pkg_ver:
            continue  # Sürüm yoksa CPE eşleşmesi belirsiz, atla
        if idx > 0:
            _time.sleep(sleep_between)

        cpe = f"cpe:2.3:a:*:{pkg_name.lower()}:{pkg_ver}:*:*:*:*:*:*:*"
        api_url = f"{NVD_API_URL}?cpeName={urllib.request.quote(cpe)}&resultsPerPage=20"
        headers = {"User-Agent": "SiberSelma/1.0"}
        if nvd_key:
            headers["apiKey"] = nvd_key

        try:
            req = urllib.request.Request(api_url, headers=headers)
            resp = urllib.request.urlopen(req, timeout=15, context=ctx)
            data = json.loads(resp.read().decode("utf-8"))
            queried += 1
        except Exception:
            continue

        for vuln in data.get("vulnerabilities", []):
            cve = vuln.get("cve", {})
            cve_id = cve.get("id", "")
            if not cve_id:
                continue
            fname = os.path.join(cve_dir, f"{cve_id}.md")
            if os.path.exists(fname):
                continue

            desc = next(
                (d["value"] for d in cve.get("descriptions", []) if d.get("lang") == "en"),
                "",
            )
            metrics = cve.get("metrics", {})
            score = "N/A"
            severity = "N/A"
            for mk in ("cvssMetricV31", "cvssMetricV30", "cvssMetricV2"):
                if mk in metrics and metrics[mk]:
                    cvss = metrics[mk][0].get("cvssData", {})
                    score = cvss.get("baseScore", "N/A")
                    severity = cvss.get("baseSeverity", "N/A")
                    break

            published = cve.get("published", "")[:10]
            md = (
                f"# {cve_id}\n\n"
                f"**Paket:** `{pkg_name}=={pkg_ver}`  \n"
                f"**CVSS:** {score} ({severity})  \n"
                f"**Yayin:** {published}  \n"
                f"**NVD:** https://nvd.nist.gov/vuln/detail/{cve_id}\n\n"
                f"## Aciklama\n\n{desc}\n\n"
                f"## Etiketler\n\n#cve #{pkg_name.lower()} #{severity.lower()}\n"
            )
            try:
                with open(fname, "w", encoding="utf-8") as f:
                    f.write(md)
                new_cve_count += 1
                if verbose:
                    print(f"  [+] {cve_id} ({pkg_name} {pkg_ver}) -> {fname}", file=__import__("sys").stderr)
            except OSError:
                continue

    return {"new_cves": new_cve_count, "queried": queried, "skipped": False}


CLI_TOOLS = {
    "wiki": (search_cyber_wiki, ["query"]),
    "remediation": (get_remediation_plan, ["vulnerability_name"]),
    "sast": (analyze_project_vulnerabilities, ["directory_path"]),
    "pentest": (run_basic_pentest, ["target"]),
    "headers": (check_security_headers, ["url"]),
    "secrets": (find_exposed_secrets, ["directory"]),
    "deps": (check_dependencies, ["file_path"]),
    "report": (generate_security_report, ["url", "directory"]),
    "subdomains": (find_subdomains, ["domain"]),
    "batch": (batch_scan_attack_surface, ["domain"]),
    "nuclei": (run_nuclei_scan, ["target"]),
    "zap": (run_zap_baseline, ["target"]),
    "history": (check_history, ["url"]),
    "threat": (check_threat, ["target"]),
    "attack": (get_attack_techniques, ["vulnerability"]),
    "breach": (check_breach, ["email"]),
    "news": (fetch_security_news, ["max_items"]),
}


def _run_cli(argv):
    """Basit CLI: python server.py --tool <name> --<arg>=<value>"""
    args = {}
    tool_name = None
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--tool" and i + 1 < len(argv):
            tool_name = argv[i + 1]
            i += 2
            continue
        if a.startswith("--"):
            key, _, val = a[2:].partition("=")
            if not val and i + 1 < len(argv) and not argv[i + 1].startswith("--"):
                val = argv[i + 1]
                i += 2
            else:
                i += 1
            args[key] = val
            continue
        i += 1

    if not tool_name or tool_name not in CLI_TOOLS:
        print("Kullanim: python server.py --tool <name> --<arg>=<value>", file=__import__("sys").stderr)
        print(f"Tool'lar: {', '.join(CLI_TOOLS)}", file=__import__("sys").stderr)
        return 2

    func, params = CLI_TOOLS[tool_name]
    call_kwargs = {}
    for p in params:
        if p in args:
            v = args[p]
            # int dönüşümü gereken yerler
            if p == "max_items":
                try:
                    v = int(v)
                except ValueError:
                    pass
            call_kwargs[p] = v
        else:
            print(f"Eksik parametre: --{p}", file=__import__("sys").stderr)
            return 2

    result = func(**call_kwargs)
    print(result)
    return 0


if __name__ == "__main__":
    import sys
    import logging
    logging.basicConfig(
        level=logging.INFO,
        stream=sys.stderr,
        format="[%(asctime)s] %(levelname)s: %(message)s",
    )
    ensure_wiki_dir()

    if len(sys.argv) > 1 and "--tool" in sys.argv:
        sys.exit(_run_cli(sys.argv[1:]))

    # Otomatik CVE taraması (opt-in): SIBERSELMA_AUTO_CVE_SCAN=1
    if os.environ.get("SIBERSELMA_AUTO_CVE_SCAN", "0") == "1":
        import threading
        def _bg_cve():
            try:
                logging.info("Otomatik CVE taramasi baslatildi (arkaplan)...")
                result = auto_cve_scan_to_wiki(verbose=True)
                logging.info(f"CVE taramasi tamamlandi: {result}")
            except Exception as e:
                logging.warning(f"CVE taramasi hata verdi: {e}")
        threading.Thread(target=_bg_cve, daemon=True).start()

    logging.info("SiberSelma MCP Sunucusu baslatiliyor...")
    logging.info("Standart I/O uzerinden iletisim dinleniyor (Claude Code vb. icin hazir)")
    mcp.run()
