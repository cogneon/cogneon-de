# cogneon-de

Repo für die Cogneon-Website unter [cogneon.de](https://cogneon.de): Inhalte als Markdown, gebaut mit [Zensical](https://zensical.org).

Stand: Aufbau und Test. Die Live-Website läuft weiter auf WordPress, bis der Umzug entschieden ist.

## Aufbau

| Pfad | Inhalt |
|---|---|
| `docs/` | Inhalte der Website als Markdown |
| `docs/blog/posts/` | Blogbeiträge, ein Ordner pro Jahr. Veröffentlicht unter `/JJJJ/MM/TT/titel/` wie in WordPress |
| `docs/.authors.yml` | Autorenprofile |
| `docs/wp-content/uploads/` | Medien unter ihren alten WordPress-Pfaden |
| `zensical.toml` | Konfiguration der Website |
| `overrides/` | Vorlagen: Kopf- und Fußzeile, Startseite (`home.html`), Angebotsseiten (`angebot.html`), Blogbeitrag (`blog-post.html`), Blog-Übersicht (`blog-liste.html`) |
| `docs/assets/stylesheets/cogneon.css` | Gestaltung. Schriften liegen lokal in `docs/assets/fonts/` |
| `inhalte/aktuell.yml` | Highlights und Termine der Startseite |
| `scripts/build_data.py` | erzeugt daraus und aus den Blogbeiträgen die Daten für Startseite und Blog-Übersicht. Muss vor `zensical build` oder `zensical serve` einmal laufen |
| `scripts/check_links.py` | prüft die Links der gebauten Website, mit `--extern` auch fremde Adressen. Wöchentlich im Issue "Linkprüfung" |
| `scripts/optimize_media.py` | verkleinert übernommene Bilder unter `docs/wp-content/` (läuft im Export) |
| `scripts/build_htaccess.py` | erzeugt `site/.htaccess`: Weiterleitungen aus `migration/redirects*.map` und Server-Regeln |
| `scripts/wp_export.py` | wiederholbarer Export aus WordPress |
| `scripts/check_urls.py` | prüft, ob alle alten URLs erreichbar bleiben |
| `migration/` | Berichte des Exports (Inventar, URL-Liste, URL-Check) |

## Lokal arbeiten

```bash
pip3 install -r requirements.txt
python3 scripts/build_data.py   # Daten der Startseite erzeugen
zensical serve          # Vorschau unter http://localhost:8000
python3 -m pytest tests  # Tests des Export-Skripts
```

## Export aus WordPress

Der Export liest die öffentliche REST-API von cogneon.de. Er kann beliebig oft laufen.

```bash
python3 scripts/wp_export.py --inventory-only   # nur zählen
python3 scripts/wp_export.py --limit 10         # Pilot
python3 scripts/wp_export.py                    # alles
```

cogneon.de gibt die REST-API nur für angemeldete Benutzer frei. Der Export braucht deshalb ein WordPress-Anwendungspasswort (WordPress: Benutzer > Profil > Anwendungspasswörter), am besten für einen eigenen Benutzer mit der Rolle Redakteur:

```bash
export WP_USER="benutzername"
export WP_APP_PASSWORD="xxxx xxxx xxxx xxxx xxxx xxxx"
```

Für den Workflow dieselben beiden Werte als Repository-Secrets `WP_USER` und `WP_APP_PASSWORD` anlegen. Die Zugangsdaten gehören nie ins Repo.

Regeln:

- Seiten mit `frozen: true` im Frontmatter überschreibt der Export nie. Das gilt für alles, was von Hand überarbeitet wurde.
- Medien werden nur geladen, wenn sie lokal fehlen.
- Der Bericht liegt danach in `migration/report.md`.

Ohne lokale Installation: Workflow **WordPress-Export** unter *Actions* starten. Das Ergebnis hängt drei Tage lang als Artefakt am Lauf.

## URL-Check

Alte URLs dürfen nicht brechen. Nach dem Build:

```bash
zensical build
python3 scripts/check_urls.py --url-map migration/url-map.csv --url-list migration/old-urls.txt
```

URLs, die es als Seite nicht mehr gibt, brauchen einen Eintrag in `migration/redirects.map` (`alter-pfad neues-ziel`, eine Regel pro Zeile). Aus dieser Datei entsteht später die Redirect-Konfiguration des Webservers.

## Arbeitsweise

- `main` ist geschützt, Änderungen kommen per Pull Request.
- Jeder Pull Request wird gebaut und getestet (Workflow **Build**).

## Adventskalender

Der Kalender unter `/advent/` kommt aus `inhalte/advent.yml`: ein Eintrag je
Türchen mit `typ`, `titel`, `link`, `von` (optional), `warum` und `impuls`
(optional), dazu die Themen der Adventswochen.

- Ein Türchen öffnet sich am Vorabend seines Tages: Ab 18 Uhr (Berliner Zeit)
  gilt beim Bauen der Folgetag. Das abendliche Veröffentlichen (22:17 MEZ)
  bringt es auf die Seite, niemand muss etwas tun. GitHub verzögert geplante
  Läufe oft um Stunden; der Puffer bis zum Morgen fängt das ab. Wer abends
  vorbeischaut, sieht das Türchen also schon vor Mitternacht.
- Inhalte künftiger Türchen stehen nicht im HTML der Seite, wohl aber in
  `inhalte/advent.yml` im öffentlichen Repository.
- Fehlt an einem Tag `titel`, `link` oder `warum`, bleibt das Türchen zu und
  `build_data.py` warnt.
- Vorschau für einen Stichtag: `python3 scripts/build_data.py --heute 2026-12-05`,
  danach `zensical serve`. Vor dem Einchecken wieder ohne `--heute` laufen lassen
  (die erzeugten Dateien sind ohnehin nicht im Repo).
- Ein Klick auf ein Türchen klappt es auf und zeigt den Inhalt in einem Dialog.
  Direktlink für Newsletter und Social Media: `https://cogneon.de/advent/#tag-5`.
- Videos nur verlinken, nicht einbetten. Keine Buchcover übernehmen.
- Das Netz im Hintergrund lässt sich oben in `docs/assets/javascripts/advent.js`
  einstellen (Dichte, Tempo, Helligkeit).

## Termine

Jeder Termin ist eine Datei unter `docs/event/`. Der Dateiname wird zur Adresse:
`docs/event/edmod27a.md` erscheint unter `/event/edmod27a/`.

```markdown
---
title: Expert Debriefing Praxis-Ausbildung Frühjahr 2027
template: termin.html
beginn: 2027-03-11 09:00
ende: 2027-03-12 17:00
ort:
  name: Cogneon Akademie
  adresse: Bucherstr. 79a, 90419 Nürnberg
kosten: 1.900 €
anmeldung: https://pretix.eu/...       # Link zur Anmeldung
kategorien: [Expert Debriefing Praxis-Ausbildung]
kategorie_slugs: [edmod]
---

# Expert Debriefing Praxis-Ausbildung Frühjahr 2027

Beschreibung des Termins.
```

Für ganztägige Termine `ganztags: true`, für Online-Termine `online: true` statt `ort`.

**Save the Date:** Steht ein Termin fest, aber Beschreibung und Anmeldung fehlen noch,
reicht eine Datei mit Titel, `beginn`, `ende` und `save_the_date: true`. Der Termin
erscheint mit der Marke "Save the Date". Sobald Text und `anmeldung` da sind, die
Zeile `save_the_date: true` wieder löschen.
Übersicht (`/events/`), Kategorie-Seiten, die Terminliste der Startseite und die
Kalenderdatei `/events/cogneon.ics` entstehen daraus bei jedem Build. Vergangene
Termine wandern von selbst ins Archiv.

## Kopfbild auf Unterseiten

Seiten mit `template: angebot.html` können rechts neben Titel, Untertitel,
Text und Button ein Bild zeigen. Beide Felder sind optional; ohne `kopfbild`
sieht die Seite aus wie bisher.

```yaml
kopfbild: wp-content/uploads/2026/03/workshop.jpg
kopfbild_alt: Teilnehmende beim Expert Debriefing an der Wissenslandkarte
```

- Format 16:9, wie Blog- und Terminbilder (dasselbe Bild wie für Präsentationen).
- Am Desktop steht es neben dem Text (halbe Breite), mobil darunter.
- Andere Formate werden auf 16:9 zugeschnitten (Mitte bleibt sichtbar).
- `kopfbild_alt` beschreibt, was zu sehen ist. Rein dekorative Bilder: Feld weglassen.
- Echte Fotos aus Projekten oder der Akademie wirken besser als Stock-Bilder.
- Vor dem Einchecken `python3 scripts/optimize_media.py` laufen lassen.

## Englische Seiten

Englische Fassungen liegen unter `docs/en/` und erscheinen unter `/en/…`. Jede
nennt im Front Matter ihre deutsche Vorlage:

```yaml
quelle: kontakt.md
quelle_hash: "3f2a…"   # Prüfwert der Vorlage beim Übersetzen
```

- Sprachumschalter (EN/DE) in der Kopfzeile führt zum Gegenstück, sonst zur
  Startseite der anderen Sprache. `hreflang`-Angaben entstehen automatisch.
- Feste Texte der Vorlagen (Knöpfe, Menü, Fußzeile) stehen zweisprachig in
  `overrides/partials/texte.html`; das englische Menü in `zensical.toml`
  unter `[[project.extra.menu_en]]`.
- Interne Links in Vorlagen nutzen `tx.ziel('kontakt/')`: auf englischen Seiten
  führt das zur englischen Fassung, falls es eine gibt.
- Blog, Termine, Akademie, Impressum und Datenschutz bleiben deutsch. Auf
  Blogbeiträgen sehen Lesende mit nicht-deutschem Browser einen Hinweis, dass
  ihr Browser übersetzen kann. Englische Blogbeiträge bekommen `sprache: en`.
- Veraltete Übersetzungen: `python3 scripts/uebersetzung.py status`. Nach dem
  Übersetzen den Prüfwert setzen: `python3 scripts/uebersetzung.py stempel
  docs/en/contact.md`. Der Build warnt ebenfalls.
- Englische Seiten, die von Hand gepflegt werden, bekommen `frozen: true`;
  dann gibt es keine Warnung mehr.

## Hinweisleiste

Meldungen über der Kopfzeile pflegst Du in `inhalte/hinweise.yml`:

```yaml
hinweise:
  - text: Der Adventskalender ist offen - jeden Tag ein neues Türchen.
    text_en: Our advent calendar is open - a new door every day.
    link: advent/
    art: aktion      # hinweis (gelb), warnung (rot), aktion (orange)
    ab: 2026-11-30
    bis: 2026-12-24
```

- Es erscheint höchstens eine Meldung: zuerst Warnungen, sonst die erste gültige.
- Der tägliche Build schaltet sie nach `ab`/`bis` an und aus.
- Ohne `text_en` gibt es auf englischen Seiten keine Leiste.
- Weggeklickt bleibt sie weg, bis sich ihr Text ändert (Speicherung nur im Browser).

## Bearbeiten mit VS Code

Das Repository bringt eine Einrichtung für Visual Studio Code mit:

- **Empfohlene Erweiterungen** (`.vscode/extensions.json`): VS Code bietet sie beim
  Öffnen des Ordners zur Installation an. Front Matter CMS, Markdown All in One,
  Rechtschreibprüfung Deutsch/Englisch.
- **Schreib-Einstellungen** für Markdown (`.vscode/settings.json`): Zeilenumbruch,
  keine Zeilennummern und Minimap, Rechtschreibprüfung. Bilder, die Du in einen
  Text einfügst oder ziehst, landen unter `docs/wp-content/uploads/JJJJ/MM/`.
- **Vorschau**: Befehlspalette (Cmd+Shift+P) > "Tasks: Run Task" > "Vorschau
  starten", dann http://localhost:8000 öffnen. Gespeicherte Änderungen
  erscheinen nach wenigen Sekunden.
- **Front Matter CMS** (`frontmatter.json`): Übersicht über Blog, Termine und
  Seiten, Formularfelder statt YAML, "Create content" für neue Beiträge und
  Termine. Neue Inhalte bekommen ein Feld `type` (blogbeitrag, termin, seite),
  an dem Front Matter die passenden Felder erkennt.
- **Vorlagen** unter `.frontmatter/templates/` (Blogbeitrag, Termin, Seite):
  im Front-Matter-Dashboard "Create content" > "Create by template", oder die
  Datei von Hand kopieren und umbenennen. Blogbeiträge gehören nach
  `docs/blog/posts/JJJJ/`, Termine nach `docs/event/`, Seiten nach `docs/`.

## Kurzlinks über Hashtags

Termine, Seiten und Blogbeiträge können im Front Matter einen Hashtag tragen:

```yaml
hashtag: loscon27          # oder mehrere: [loscon27, lernoscon27]
```

Daraus entsteht beim Veröffentlichen automatisch die Weiterleitung
`cogneon.de/loscon27` auf die Seite. Erlaubt sind a-z, 0-9 und `-`. Doppelte
Hashtags, Hashtags, die schon eine Seite sind, oder Abweichungen zu
`migration/redirects.map` meldet `build_data.py` als Warnung und erzeugt sie
nicht. Kurzlinks ohne eigene Seite (z.B. auf externe Adressen) bleiben in
`migration/redirects.map`.

## Veröffentlichen

Der Workflow "Veröffentlichen" baut die Website und lädt sie per SFTP auf den
Webspace: bei jedem Merge nach `main`, jeden Morgen und auf Knopfdruck
(Actions, "Veröffentlichen", "Run workflow"). Die Zugangsdaten stehen als
Secrets im Repository (`SFTP_HOST`, `SFTP_USER`, `SFTP_PASSWORD`, `SFTP_PATH`).

Weiterleitungen stehen in `migration/redirects.map`, eine je Zeile:
alte Adresse, Leerzeichen, neue Adresse. Beim Veröffentlichen entsteht
daraus die Datei `.htaccess` für den Webserver.

## Karte

Auf einer Seite erscheint eine Karte mit `<div class="cg-karte"></div>` im Markdown.
Die Orte stehen in `inhalte/karte.yml` (Name, Koordinaten, Art, optional Text und Link).
Die Karte lädt erst nach einem Klick, vorher wird nichts von OpenStreetMap abgerufen.

## Lizenz

- Texte: [CC BY 4.0](LICENSE-INHALTE.md), Namensnennung "Cogneon GmbH, cogneon.de"
- Code (Skripte, Vorlagen, CSS, JavaScript): [MIT](LICENSE)
- Ausgenommen sind Marken und Logos, Kundenlogos, Fotos von Personen sowie
  Werke Dritter, Schriften und Bibliotheken (Einzelheiten in `LICENSE-INHALTE.md`)
