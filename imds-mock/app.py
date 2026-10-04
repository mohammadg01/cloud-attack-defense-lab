from flask import Flask, request, jsonify

app = Flask(__name__)

# Fake-Token, das der echte Azure-IMDS bei einer Managed Identity zurückgeben würde.
# Rein lokal und erfunden - kein echtes Azure-Credential.
FAKE_TOKEN = {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.FAKE-LAB-TOKEN.DO-NOT-USE",
    "client_id": "11111111-1111-1111-1111-111111111111",
    "expires_in": "3599",
    "resource": "https://storage.azure.com/",
    "token_type": "Bearer"
}

# Der echte Azure-IMDS-Pfad fuer Managed-Identity-Token.
@app.route("/metadata/identity/oauth2/token")
def token():
    # Azure verlangt den Header 'Metadata: true'. Wir pruefen ihn auch,
    # damit sich der Mock realistisch verhaelt.
    if request.headers.get("Metadata") != "true":
        return jsonify({"error": "Metadata header 'true' required"}), 400
    return jsonify(FAKE_TOKEN)

# Kleiner Status-Endpunkt zum Testen, ob der Dienst laeuft.
@app.route("/")
def health():
    return "IMDS-Mock laeuft\n"

if __name__ == "__main__":
    # Lauscht auf allen Interfaces, Port 80 (wie der echte IMDS).
    app.run(host="0.0.0.0", port=80)
