from flask import Flask, request, Response
import requests, json, os
from datetime import datetime, timezone

app = Flask(__name__)
LOG_PATH = "/var/log/webapp/fetch.log"

def log_fetch(url, client_ip):
    # Jeden Abruf als JSON-Zeile protokollieren - Wazuh liest JSON nativ.
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": "webapp_fetch",
        "client": client_ip,
        "url": url,
    }
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")

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

# ---- SSRF-Schwachstelle (siehe Kommentar in Woche 1) ----
@app.route("/fetch")
def fetch():
    url = request.args.get("url", "")
    if not url:
        return "Parameter 'url' fehlt", 400
    log_fetch(url, request.remote_addr)   # <-- fuer die Erkennung
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
