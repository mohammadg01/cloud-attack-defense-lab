from flask import Flask, request, Response
import requests, json, os, socket, ipaddress
from urllib.parse import urlparse
from datetime import datetime, timezone

app = Flask(__name__)
LOG_PATH = "/var/log/webapp/fetch.log"

def log_fetch(url, client_ip, blocked=False):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": "webapp_fetch",
        "client": client_ip,
        "url": url,
        "blocked": blocked,
    }
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")

def is_safe_url(url):
    # SSRF-Schutz: nur http/https, und Ziel darf keine interne/reservierte IP sein.
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return False, "nur http/https erlaubt"
    host = parsed.hostname
    if not host:
        return False, "kein gueltiger Host"
    try:
        infos = socket.getaddrinfo(host, None)
    except Exception:
        return False, "Host nicht aufloesbar"
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
            return False, f"interne/reservierte Adresse blockiert ({ip})"
    return True, "ok"

@app.route("/")
def index():
    return """
    <h2>Link-Vorschau-Service</h2>
    <p>Gib eine URL ein, wir holen sie fuer dich ab:</p>
    <form action="/fetch">
        <input name="url" size="60" placeholder="https://example.com">
        <button type="submit">Abrufen</button>
    </form>
    """

@app.route("/fetch")
def fetch():
    url = request.args.get("url", "")
    if not url:
        return "Parameter 'url' fehlt", 400

    # Ziel pruefen BEVOR wir es abrufen (SSRF-Schutz).
    safe, reason = is_safe_url(url)
    if not safe:
        log_fetch(url, request.remote_addr, blocked=True)  # Versuch trotzdem loggen
        return f"Blockiert: {reason}", 403

    log_fetch(url, request.remote_addr, blocked=False)
    try:
        headers = {}
        if request.args.get("metadata") == "true":
            headers["Metadata"] = "true"
        r = requests.get(url, headers=headers, timeout=5)
        return Response(r.content, status=r.status_code,
                        content_type=r.headers.get("content-type", "text/plain"))
    except Exception as e:
        return f"Fehler beim Abruf: {e}", 502

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
