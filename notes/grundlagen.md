# Grundlagen

Kurznotizen zu den Konzepten hinter diesem Lab.

## SSRF (Server-Side Request Forgery)
Schwachstelle, bei der ein Angreifer den Server dazu bringt, HTTP-Anfragen an ein frei wählbares Ziel zu schicken. Gefährlich, weil der Server oft interne Adressen erreicht, die von außen gar nicht erreichbar sind (interne APIs, Metadaten-Dienste). Typischer Einstieg: eine Funktion, die eine vom Nutzer angegebene URL abruft (Vorschau, Import, Webhook), ohne das Ziel zu prüfen.

## IMDS (Instance Metadata Service)
Nur intern erreichbarer Dienst in Cloud-VMs unter der festen Adresse `169.254.169.254`. Liefert Metadaten über die Instanz und - bei zugewiesener Managed Identity - Zugriffstoken für Cloud-Dienste. Diese Token sind das Ziel: Wer per SSRF den IMDS erreicht, lässt sich ein gültiges Token ausstellen. Azure verlangt dafür den Header `Metadata: true` (ein Teil-Schutz).

## Managed Identity
Azure-Mechanismus, mit dem sich eine Ressource gegenüber anderen Azure-Diensten ausweist, ohne gespeicherte Passwörter. Das Token holt die VM zur Laufzeit beim IMDS. Vorteil: keine Secrets im Code. Risiko: Wer das Token abgreift, erbt die Rechte der Identität - darum ist Least Privilege (nur minimale Rechte vergeben) so wichtig.

## Azurite
Offizieller lokaler Emulator für Azure Storage (Blob/Queue/Table). Läuft als Container und verhält sich wie echter Azure-Storage, ohne Cloud-Kosten. Im Lab liegt darin eine (Fake-)`secrets.txt`, die am Ende der Angriffskette ausgelesen wird.
