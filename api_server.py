"""
SiberSelma HTTP API Server
Antigravity / Gemini'nin SiberSelma tool'larını HTTP üzerinden çağırması için wrapper.
Çalıştır: python api_server.py
Sonra Antigravity'ye: "http://localhost:8765/pentest?url=https://example.com"

Güvenlik:
  - Yerel dosya sistemi taraması yapan endpoint'ler (/sast, /secrets, /deps, /report)
    yalnızca SIBERSELMA_ALLOWED_PATHS ortam değişkeninde tanımlı kök dizinler altında çalışır.
    Tanımlı değilse default olarak proje kökü kullanılır.
  - SIBERSELMA_API_TOKEN tanımlıysa tüm istekler `Authorization: Bearer <token>` ister.
"""
import json
import os
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler

# server.py'deki tool fonksiyonlarını import et
from server import (
    BASE_DIR,
    search_cyber_wiki,
    get_remediation_plan,
    analyze_project_vulnerabilities,
    run_basic_pentest,
    check_security_headers,
    find_exposed_secrets,
    check_dependencies,
    generate_security_report,
    find_subdomains,
    check_history,
)

PORT = 8765

# İzinli kök dizinler (path traversal koruması için)
_allowed_env = os.environ.get("SIBERSELMA_ALLOWED_PATHS", "")
ALLOWED_ROOTS = [
    os.path.realpath(p.strip())
    for p in _allowed_env.split(os.pathsep)
    if p.strip()
] or [os.path.realpath(BASE_DIR)]

API_TOKEN = os.environ.get("SIBERSELMA_API_TOKEN", "")


def _safe_path(raw_path: str) -> str:
    """Verilen path'in ALLOWED_ROOTS altında olduğunu doğrular; değilse hata fırlatır."""
    if not raw_path:
        raise ValueError("path parametresi bos olamaz")
    real = os.path.realpath(raw_path)
    for root in ALLOWED_ROOTS:
        try:
            if os.path.commonpath([real, root]) == root:
                return real
        except ValueError:
            continue
    raise PermissionError(
        f"Yol izinli koklerden birinin altinda degil: {real}. "
        f"SIBERSELMA_ALLOWED_PATHS ile genisletin."
    )


ROUTES = {
    "/wiki":        lambda p: search_cyber_wiki(p.get("q", "")),
    "/remediation": lambda p: get_remediation_plan(p.get("vuln", "")),
    "/sast":        lambda p: analyze_project_vulnerabilities(_safe_path(p.get("dir", "."))),
    "/pentest":     lambda p: run_basic_pentest(p.get("url", "")),
    "/headers":     lambda p: check_security_headers(p.get("url", "")),
    "/secrets":     lambda p: find_exposed_secrets(_safe_path(p.get("dir", "."))),
    "/deps":        lambda p: check_dependencies(_safe_path(p.get("file", ""))),
    "/report":      lambda p: generate_security_report(p.get("url", ""), _safe_path(p.get("dir", "."))),
    "/subdomains":  lambda p: find_subdomains(p.get("domain", "")),
    "/history":     lambda p: check_history(p.get("url", "")),
}

class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        print(f"[SiberSelma API] {self.address_string()} - {format % args}")

    def _check_auth(self):
        if not API_TOKEN:
            return True
        auth = self.headers.get("Authorization", "")
        return auth == f"Bearer {API_TOKEN}"

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = dict(urllib.parse.parse_qsl(parsed.query))
        route = parsed.path

        if not self._check_auth():
            self._respond(401, json.dumps({"error": "Unauthorized — Authorization: Bearer <token> gerekli"}, ensure_ascii=False))
            return

        if route == "/":
            body = json.dumps({
                "name": "SiberSelma API",
                "routes": list(ROUTES.keys()),
                "examples": {
                    "/pentest": "?url=https://example.com",
                    "/headers": "?url=https://example.com",
                    "/wiki":    "?q=XSS",
                    "/sast":    "?dir=C:/path/to/project",
                    "/secrets": "?dir=C:/path/to/project",
                    "/deps":    "?file=C:/path/to/requirements.txt",
                    "/report":  "?url=https://example.com&dir=C:/path/to/project",
                    "/subdomains": "?domain=example.com",
                    "/history": "?url=https://example.com/admin",
                    "/threat":  "?target=1.2.3.4",
                }
            }, ensure_ascii=False, indent=2)
            self._respond(200, body)
            return

        if route in ROUTES:
            try:
                result = ROUTES[route](params)
                self._respond(200, json.dumps({"result": result}, ensure_ascii=False))
            except PermissionError as e:
                self._respond(403, json.dumps({"error": str(e)}, ensure_ascii=False))
            except ValueError as e:
                self._respond(400, json.dumps({"error": str(e)}, ensure_ascii=False))
            except Exception as e:
                self._respond(500, json.dumps({"error": str(e)}, ensure_ascii=False))
        else:
            self._respond(404, json.dumps({"error": "Route not found", "available": list(ROUTES.keys())}))

    def _respond(self, code, body):
        data = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(data)

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    print(f"\n[SiberSelma] HTTP API baslatiliyor: http://localhost:{PORT}")
    print(f"[SiberSelma] Tum endpoint'ler: http://localhost:{PORT}/\n")
    httpd = HTTPServer(("localhost", PORT), Handler)
    httpd.serve_forever()
