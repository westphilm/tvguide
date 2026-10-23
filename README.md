# tvguide

Schlanke lokale NiceGUI-Anwendung für das aktuelle Fernsehprogramm

<img src="doku/img/main-light.jpg" alt="TVGuide hell" width="500">&nbsp;
<img src="doku/img/main-dark.jpg" alt="TVGuide dunkel" width="500">

## Setup

Das Startpaket enthält den vollständigen Senderkatalog einschließlich der
hinterlegten Mediathek-Links. Beim ersten Start legt die Anwendung daraus
automatisch alle Sender und die beiden Standardtabellen an.

```bash
git clone https://github.com/westphilm/tvguide.git
cd tvguide
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m app.main
```

Die Anwendung läuft lokal unter `http://127.0.0.1:9000`.

### Zugriff im lokalen Netzwerk

Zum Bereitstellen im lokalen Netzwerk die Anwendung an alle Netzwerkschnittstellen
binden:

```bash
TVGUIDE_HOST=0.0.0.0 python -m app.main
```

Im Browser wird dabei die IP-Adresse des Pi verwendet, zum Beispiel
`http://192.168.50.1:9000`. `0.0.0.0` ist nur die Bindeadresse und keine Adresse
für den Browser. Bei einer Firewall muss TCP-Port 9000 im lokalen Netzwerk
freigegeben sein.

Um das Startpaket später erneut einzuspielen, die Anwendung beenden,
`data/tvguide.db` löschen und sie wieder starten. Eigene Senderreihenfolgen und
Tabellen werden dabei zurückgesetzt; die Stream-Links stammen aus
`app/config/channel_catalog.py`.

Standardmäßig lädt die App einen öffentlichen deutschen XMLTV-Feed. Für einen
anderen XMLTV-Feed kann die App mit einer URL gestartet werden:

```bash
TVGUIDE_EPG_URL='https://example.invalid/guide.xml.gz' python -m app.main
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

### Aufruf

```bash
  nohup "$HOME/bin/tvguide.sh" </dev/null >"$HOME/tvguide.log" 2>&1 &
  tail -f "$HOME/tvguide.log"
```  
  
  
> &#127760; **http://192.168.1.2:9000/**

### Version
> NiceGUI TV Guide &middot; 23.10.2026  
> Author: Jann Westphal 2026  
> Version: beta-release 0.9.3-beta  
> [github.com/westphilm/tvguide](https://github.com/westphilm/tvguide) &middot; Supported by ChatGPT &middot; [MIT License](https://opensource.org/license/mit/)


__
