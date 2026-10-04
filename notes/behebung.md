# Behebung (Defense in Depth)

Die SSRF-auf-IMDS-Kette wird nicht durch eine einzelne Massnahme entschaerft,
sondern durch mehrere Ebenen. Faellt eine aus, greift die naechste.

## 1. Anwendungsebene - SSRF schliessen (umgesetzt)
Die Web-App prueft jede Ziel-URL VOR dem Abruf:
- Nur `http`/`https` erlaubt.
- Host wird aufgeloest; zeigt eine IP auf einen internen/reservierten Bereich
  (link-local 169.254.0.0/16, loopback, private Netze, reserviert) -> blockiert.
Das blosse Blocken des Strings "169.254.169.254" reicht NICHT (DNS-Rebinding,
alternative IP-Schreibweisen). Richtig ist die Pruefung der aufgeloesten IP.

## 2. Identitaetsebene - Least Privilege
Die Managed Identity sollte nur die minimal noetigen Rechte haben. Selbst wenn
ein Token abfliesst, ist der Schaden begrenzt, wenn die Identitaet z.B. nur
Lesezugriff auf genau einen Container statt auf das ganze Konto hat.

## 3. Metadaten-Dienst haerten (IMDS)
- IMDSv2-Prinzip: Token-/Header-Pflicht (`Metadata: true`) erschwert naive SSRF.
- Wo moeglich den Zugriff auf den Metadaten-Endpunkt fuer die Anwendung
  einschraenken (lokale Firewall-Regel, die 169.254.169.254 nur fuer noetige
  Prozesse erlaubt).

## 4. Netzwerkebene - Egress-Filter
Ausgehende Verbindungen der Web-App auf interne Adressbereiche unterbinden.
Die App muss den Metadaten-Dienst fachlich nie erreichen.

## 5. Erkennung - Defense in Depth
Auch eine geblockte Anfrage wird protokolliert und von Wazuh (Regel 100100)
alarmiert. Blockieren UND Erkennen: ein Umgehungsversuch bleibt sichtbar.
