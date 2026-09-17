# Television

Schlanke lokale NiceGUI-Anwendung für das aktuelle Fernsehprogramm.

## Setup

```bash
cd /opt/PycharmProjects/television
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m app.main
```

Die Anwendung läuft lokal unter `http://127.0.0.1:9000`.

Standardmäßig lädt die App einen öffentlichen deutschen XMLTV-Feed. Für einen
anderen XMLTV-Feed kann die App mit einer URL gestartet werden:

```bash
TELEVISION_EPG_URL='https://example.invalid/guide.xml.gz' python -m app.main
```

Der `XmltvProgramProvider` unterstützt XMLTV sowie gzip-komprimierte XMLTV-Dateien
und ordnet derzeit ARD, ZDF, arte, 3sat und phoenix zu. Der `MockProgramProvider`
bleibt für Tests verfügbar.

Nach einem erfolgreichen Import werden die Programmdaten pro Sender nur einmal je
Kalendertag aktualisiert und in SQLite gespeichert. Kann der Feed nicht geladen
werden, bleiben die zuletzt erfolgreich importierten Daten erhalten.

Die zuletzt erfolgreich geladene XMLTV-Rohdatei bleibt zusätzlich unter
`data/epg/germany.xml.gz` liegen. Sie dient der lokalen Prüfung und wird nicht in
Git versioniert.
