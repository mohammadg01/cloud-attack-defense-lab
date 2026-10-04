# Bestueckt den lokalen Azurite-Storage mit einem Fake-Secret.
# Nutzt die oeffentlich dokumentierten Standard-Zugangsdaten des Azurite-
# Emulators (devstoreaccount1) - das ist KEIN echtes Azure-Credential.
from azure.storage.blob import BlobServiceClient

CONN = (
    "DefaultEndpointsProtocol=http;"
    "AccountName=devstoreaccount1;"
    "AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;"
    "BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;"
)

# api_version festpinnen, damit das SDK zur Azurite-Version passt.
svc = BlobServiceClient.from_connection_string(CONN, api_version="2021-08-06")

try:
    svc.create_container("secrets")
    print("Container 'secrets' angelegt.")
except Exception:
    print("Container 'secrets' existiert bereits.")

blob = svc.get_blob_client("secrets", "secrets.txt")
blob.upload_blob(b"FAKE-DB-PASSWORD=SuperSecret123-NUR-FUER-LAB\n", overwrite=True)
print("Blob 'secrets/secrets.txt' hochgeladen.")
