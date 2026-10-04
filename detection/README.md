# Detection

Erkennung der SSRF-auf-IMDS-Angriffskette mit Wazuh.

## Idee
Die Web-App protokolliert jeden Abruf als JSON-Zeile nach `/var/log/webapp/fetch.log`
(Feld `event: webapp_fetch`, `url: <abgerufene URL>`). Wazuh liest dieses Log
(JSON-Decoder, kein eigener Decoder noetig) und alarmiert, sobald eine URL die
Metadaten-Adresse `169.254.169.254` enthaelt.

## Dateien
- `local_rules.xml` - die Erkennungsregel (ID 100100, Level 12).
- `ossec-localfile.xml` - Konfig-Block, damit Wazuh das Log einliest.

## Installation
1. Inhalt von `local_rules.xml` nach `/var/ossec/etc/rules/local_rules.xml`.
2. Inhalt von `ossec-localfile.xml` ans Ende von `/var/ossec/etc/ossec.conf` anhaengen.
3. `sudo systemctl restart wazuh-manager`
4. Pruefen: `echo '<json-zeile>' | sudo /var/ossec/bin/wazuh-logtest`

## MITRE ATT&CK
| Technik | ID |
|---|---|
| Exploit Public-Facing Application | T1190 |
| Unsecured Credentials: Cloud Instance Metadata API | T1552.005 |

## Hinweis
Reines Lab mit emulierter Umgebung. Azurite validiert keine Azure-AD-Token;
der Storage-Zugriff im Angriffsskript ist daher emuliert, der erkannte
SSRF-auf-IMDS-Indikator entspricht aber dem realen Angriff.
