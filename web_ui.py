"""
SiberSelma Minimal Web UI
Standart kutuphaneyle calisan basit bir HTML formu — tool'lari tarayici uzerinden cagirir.
Calistir: python web_ui.py
Sonra: http://localhost:8766
"""
import json
import html
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler

from server import (
    BASE_DIR,
    search_cyber_wiki,
    run_basic_pentest,
    check_security_headers,
    find_subdomains,
    check_threat,
    get_attack_techniques,
    batch_scan_attack_surface,
    generate_security_report,
)

PORT = 8766

TOOLS = {
    "wiki":       (search_cyber_wiki,           [("query", "Sorgu")]),
    "pentest":    (run_basic_pentest,           [("target", "URL")]),
    "headers":    (check_security_headers,      [("url", "URL")]),
    "subdomains": (find_subdomains,             [("domain", "Domain")]),
    "threat":     (check_threat,                [("target", "IP / Domain")]),
    "attack":     (get_attack_techniques,       [("vulnerability", "Zafiyet")]),
    "batch":      (batch_scan_attack_surface,   [("domain", "Domain")]),
    "report":     (generate_security_report,    [("url", "URL"), ("directory", "Dizin")]),
}

PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="utf-8">
<title>SiberSelma</title>
<style>
  body {{ font-family: -apple-system, Segoe UI, sans-serif; max-width: 900px; margin: 2em auto; padding: 0 1em; background: #0f1419; color: #e2e8f0; }}
  h1 {{ color: #f59e0b; }}
  nav a {{ display: inline-block; padding: 0.4em 0.8em; margin: 0.2em; background: #1e293b; color: #93c5fd; text-decoration: none; border-radius: 4px; }}
  nav a:hover {{ background: #334155; }}
  nav a.active {{ background: #f59e0b; color: #0f1419; }}
  form {{ background: #1e293b; padding: 1em; border-radius: 6px; margin: 1em 0; }}
  label {{ display: block; margin: 0.5em 0 0.2em; }}
  input {{ width: 100%; padding: 0.6em; background: #0f1419; color: #e2e8f0; border: 1px solid #334155; border-radius: 4px; box-sizing: border-box; }}
  button {{ margin-top: 1em; padding: 0.7em 1.5em; background: #f59e0b; color: #0f1419; border: 0; border-radius: 4px; cursor: pointer; font-weight: 600; }}
  button:hover {{ background: #fbbf24; }}
  pre {{ background: #1e293b; padding: 1em; border-radius: 6px; overflow-x: auto; white-space: pre-wrap; }}
</style>
</head>
<body>
<h1>🕵️‍♀️ SiberSelma</h1>
<nav>{nav}</nav>
{form}
{result}
<p style="margin-top:3em;color:#64748b;font-size:0.85em">SiberSelma Web UI — MCP server'in HTTP yansimasi</p>
</body>
</html>
"""


def render_page(active_tool=None, result_text=None):
    nav = "".join(
        f'<a href="/?tool={t}" class="{"active" if t == active_tool else ""}">{t}</a>'
        for t in TOOLS
    )
    nav += '<a href="/">home</a>'

    form_html = ""
    if active_tool and active_tool in TOOLS:
        _, params = TOOLS[active_tool]
        fields = "".join(
            f'<label>{html.escape(label)}</label><input name="{name}" required>'
            for name, label in params
        )
        form_html = (
            f'<form method="post" action="/run">'
            f'<input type="hidden" name="tool" value="{active_tool}">'
            f"{fields}"
            f'<button type="submit">Calistir</button>'
            f"</form>"
        )

    result_html = ""
    if result_text:
        result_html = f"<h2>Sonuc</h2><pre>{html.escape(result_text)}</pre>"

    return PAGE_TEMPLATE.format(nav=nav, form=form_html, result=result_html)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print(f"[WebUI] {self.address_string()} - {fmt % args}")

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = dict(urllib.parse.parse_qsl(parsed.query))
        active = params.get("tool")
        page = render_page(active_tool=active)
        self._respond(200, page, "text/html; charset=utf-8")

    def do_POST(self):
        if self.path != "/run":
            self._respond(404, "not found")
            return
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode("utf-8")
        params = dict(urllib.parse.parse_qsl(body))
        tool_name = params.pop("tool", "")
        if tool_name not in TOOLS:
            self._respond(400, "unknown tool")
            return
        func, expected = TOOLS[tool_name]
        kwargs = {k: params.get(k, "") for k, _ in expected}
        try:
            result = func(**kwargs)
        except Exception as e:
            result = f"Hata: {e}"
        page = render_page(active_tool=tool_name, result_text=str(result))
        self._respond(200, page, "text/html; charset=utf-8")

    def _respond(self, code, body, content_type="text/plain; charset=utf-8"):
        data = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    print(f"\n[SiberSelma] Web UI baslatiliyor: http://localhost:{PORT}\n")
    HTTPServer(("localhost", PORT), Handler).serve_forever()
