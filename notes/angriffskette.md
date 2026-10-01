# Angriffskette (SSRF -> IMDS -> Storage)

## Ablauf
1. Einstieg per SSRF: Angreifer ruft den verwundbaren `/fetch`-Endpunkt der Web-App auf und gibt als Ziel-URL den IMDS an: `http://169.254.169.254/metadata/identity/oauth2/token`.
2. Server-seitiger Abruf: Die Web-App holt diese URL selbst ab - aus ihrer Sicht ein interner Request - und erreicht so den Metadaten-Dienst.
3. Token-Diebstahl: Der IMDS-Mock antwortet mit einem Fake-Zugriffstoken der Managed Identity; es landet in der Antwort an den Angreifer.
4. Zugriff auf Storage: Mit dem Token liest der Angreifer die geschützte `secrets.txt` aus dem Azurite-Storage.

## MITRE ATT&CK
| Schritt | Technik | ID |
|---|---|---|
| SSRF in die App | Exploit Public-Facing Application | T1190 |
| Token aus IMDS stehlen | Unsecured Credentials: Cloud Instance Metadata API | T1552.005 |
| Gestohlene Identität nutzen | Valid Accounts: Cloud Accounts | T1078.004 |

## Erkennung (Woche 2)
Leitindikatoren in den Logs: ausgehender Request der Web-App auf `169.254.169.254` (SSRF-Verdacht), unmittelbar gefolgt von einem Storage-Zugriff - diese Verkettung macht den Angriff sichtbar.

## Behebung (Woche 3)
SSRF-Fix per Allowlist (nur erlaubte Ziele, `169.254.169.254` blocken), Least Privilege an der Identität, IMDS-Zugriff einschränken.
