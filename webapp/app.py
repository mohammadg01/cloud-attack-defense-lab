from flask import Flask, request, Response
import requests

app = Flask(__name__)

# Startseite mit kleinem Formular - simuliert eine "URL-Vorschau"-Funktion,
# wie man sie in echten Apps oft findet (Link-Preview, Import, Webhook-Test).
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

# ---- SSRF-Schwachstelle ----
# Der Endpunkt nimmt eine beliebige URL und ruft sie SERVER-seitig ab,
# OHNE das Ziel zu pruefen. Dadurch kann ein Angreifer interne Adressen
# erreichen, die von aussen nicht erreichbar sind - z.B. den Metadaten-Dienst
# unter 169.254.169.254. Genau das ist die Luecke, die wir spaeter ausnutzen.
@app.route("/fetch")
def fetch():
    url = request.args.get("url", "")
    if not url:
        return "Parameter 'url' fehlt", 400
    try:
        # KEINE Pruefung des Ziels -> SSRF. Header werden mit weitergegeben,
        # damit auch der vom IMDS erwartete 'Metadata: true' durchkommen kann.
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
