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
| `scripts/build_social.py` | Vorschaubilder und Beschreibungen fürs Teilen (`docs/assets/social/`) |
| `scripts/mastodon.py` | kündigt neue Beiträge und Termine auf Mastodon an (im Deploy) |
| `scripts/check_umzug.py` | spielt die Weiterleitungen der `.htaccess` gegen `site/` durch: alte WordPress-Adressen und interne Links, Bericht `migration/umzug-check.md` |
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

- `main` ist der veröffentlichte Stand. Änderungen kommen über einen eigenen
  Branch und einen Pull Request (PR) dorthin.
- Jeder PR wird gebaut und getestet (Workflow **Build**), nach dem Mergen
  veröffentlicht der Workflow **Veröffentlichen** die Seite.

## Ablauf für Redakteur:innen (Git Schritt für Schritt)

Begriffe in einem Satz: Ein **Branch** ist eine Arbeitskopie, an der Du in Ruhe
änderst. Ein **Commit** speichert einen Arbeitsschritt mit Beschreibung.
**Push** lädt Deine Commits zu GitHub hoch (die Website ändert sich dadurch
nicht). Ein **Pull Request** schlägt vor, den Branch in `main` zu übernehmen;
erst das **Mergen** bringt die Änderungen auf die Website.

### 1. Vor dem Start: aktuellen Stand holen

```bash
cd ~/Documents/GitHub/cogneon-de
git switch main
git pull
```

### 2. Branch anlegen

Ein Branch pro Vorhaben, Name kurz und sprechend:

```bash
git switch -c inhalt/termine-2027
```

### 3. Ändern, prüfen, committen (beliebig oft)

Dateien bearbeiten, Vorschau mit `python3 scripts/build_data.py && zensical serve`
(oder in VS Code: "Tasks: Run Task" > "Vorschau starten"). Dann:

```bash
git status                     # was ist geändert?
git add docs/                  # Inhalte vormerken (ggf. auch migration/)
git commit -m "Termine 2027 angelegt (#35)"
```

`(#35)` verknüpft den Commit mit Issue 35. Nur vormerken, was Du bewusst
geändert hast: Dateien wie `frontmatter.json` ändern Werkzeuge manchmal von
selbst.

### 4. Hochladen

```bash
git push -u origin HEAD        # beim ersten Mal (legt den Branch auf GitHub an)
git push                       # danach
```

### 5. Pull Request öffnen

1. https://github.com/cogneon/cogneon-de öffnen. Kurz nach einem Push steht
   oben ein gelber Hinweis mit **Compare & pull request**: anklicken.
   Sonst: Reiter **Pull requests** > **New pull request**, links `base: main`,
   rechts Deinen Branch wählen.
2. Titel eintragen, in die Beschreibung z.B. `Closes #35` (schließt das Issue
   beim Mergen automatisch).
3. **Create pull request** klicken. Wer noch weiterarbeitet: Pfeil daneben >
   **Create draft pull request**; später **Ready for review**.
4. Unten laufen die Prüfungen (Build). Grüner Haken = alles gut. Bei rotem
   Kreuz auf **Details** klicken oder Bescheid geben.
5. Reiter **Files changed** zeigt alle Änderungen zum Gegenlesen.

### 6. Mergen

**Merge pull request** > **Confirm merge**, danach **Delete branch**. Nach ein
paar Minuten ist die Änderung auf der Website (Reiter **Actions** >
"Veröffentlichen").

Danach lokal aufräumen:

```bash
git switch main
git pull
git branch -d inhalt/termine-2027
```

### Zwischendurch: neuen Stand von main in den eigenen Branch holen

Wurden andere PRs gemergt, während Du arbeitest:

```bash
git pull --no-edit origin main
```

Einmalig vorher (falls Git nach "divergent branches" fragt):
`git config --global pull.rebase false`

### Häufige Meldungen und was zu tun ist

| Meldung | Bedeutung | Lösung |
|---|---|---|
| `no changes added to commit` | Nichts vorgemerkt | erst `git add docs/`, dann `git commit` |
| `Your local changes … would be overwritten by merge` | Ungespeicherte Änderung an einer Datei, die auch auf main geändert wurde | Eigene Änderung: `git add` + `git commit`, dann erneut pullen. Ungewollte Änderung (z.B. `frontmatter.json`): `git stash push <datei>`, pullen, `git stash show -p` ansehen, `git stash drop` |
| `Need to specify how to reconcile divergent branches` | Git fragt, wie es zusammenführen soll | `git config --global pull.rebase false`, erneut pullen |
| `Waiting for your editor to close the file` | Git will eine Merge-Nachricht | im Terminal-Editor `Esc`, `:wq`, Enter; künftig `git pull --no-edit …` |
| `zsh: suspended` | Mit Ctrl+Z angehalten | `fg`, dann wie oben |
| `CONFLICT (content)` | Dieselbe Stelle wurde zweimal geändert | Datei öffnen, zwischen `<<<<<<<` und `>>>>>>>` die richtige Fassung behalten, Markierungen löschen, `git add`, `git commit`; im Zweifel Bescheid geben |
| PR: "This branch has conflicts" | wie oben, auf GitHub | im eigenen Branch `git pull --no-edit origin main`, Konflikt lösen, `git push` |

### Dasselbe in VS Code per Klick

- **Branch:** unten links auf den Branch-Namen klicken > "Create new branch".
- **Committen:** Seitenleiste "Quellcodeverwaltung" (Cmd+Shift+G): bei
  jeder Datei "+" (vormerken), Nachricht eintippen, **Commit**.
- **Push/Pull:** Schaltfläche **Sync Changes** bzw. "…" > Pull/Push.
- **Pull Request:** mit der Erweiterung "GitHub Pull Requests" direkt aus
  VS Code, sonst wie oben im Browser.

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
- Vorschau für einen Stichtag: in VS Code die Aufgabe "Vorschau für Stichtag"
  (Datum eingeben, z.B. 2026-12-01), oder im Terminal
  `python3 scripts/build_data.py --heute 2026-12-05`, danach `zensical serve`. Vor dem Einchecken wieder ohne `--heute` laufen lassen
  (die erzeugten Dateien sind ohnehin nicht im Repo).
- Ein Klick auf ein Türchen klappt es auf und zeigt den Inhalt in einem Dialog.
  Direktlink für Newsletter und Social Media: `https://cogneon.de/advent/#tag-5`.
- Videos nur verlinken, nicht einbetten. Keine Buchcover übernehmen.
- Das Netz im Hintergrund lässt sich oben in `docs/assets/javascripts/advent.js`
  einstellen (Dichte, Tempo, Helligkeit).

## Inhalte anlegen und pflegen

Jeder Inhalt ist eine Markdown-Datei. Oben zwischen `---` stehen die
Metadaten (Front Matter), darunter der Text. Am bequemsten geht das mit
VS Code und Front Matter CMS (siehe "Bearbeiten mit VS Code"): Dashboard
"FM" > "Create content" > Blog, Termine oder Seiten; die Felder erscheinen
als Formular. Vorlagen liegen unter `.frontmatter/templates/`.

Nach dem Anlegen, Umbenennen oder Löschen von Beiträgen und Terminen die
Vorschau neu starten (`python3 scripts/build_data.py && zensical serve`),
denn Übersichten, Startseite und Kalender erzeugt `build_data.py`.

### Wo liegt was, wie heißt die Datei?

| Inhalt | Ordner | Adresse |
|---|---|---|
| Blogbeitrag | `docs/blog/posts/JJJJ/` | aus Datum und Slug: `/2026/12/01/mein-beitrag/` |
| Termin | `docs/event/` | Dateiname: `docs/event/lernos-convention-2027.md` → `/event/lernos-convention-2027/` |
| Seite | `docs/` | Dateiname: `docs/akademie.md` → `/akademie/` |

Dateinamen klein, ohne Umlaute und Leerzeichen, Wörter mit `-` getrennt,
lieber sprechend und lang. Kurze Adressen wie `/loscon27` entstehen über
das Feld `hashtag` (siehe "Kurzlinks über Hashtags"), nicht über den Dateinamen.

### Blogbeitrag

```yaml
---
title: Titel des Beitrags
date:
  created: '2026-12-01'        # Erscheinungsdatum, bestimmt die Adresse
  updated: '2026-12-03'        # optional
slug: titel-des-beitrags       # optional, sonst aus dem Titel
authors: [simon-dueckert]      # Schlüssel aus docs/.authors.yml
categories: [Wissensmanagement]
tags: [Wissensmanagement, GenerativeKI]   # CamelCase, siehe migration/schlagworte.csv
bild: assets/bilder/kclo-banner.png       # 16:9, erscheint in Übersicht und Kopf
bild_alt: Was auf dem Bild zu sehen ist
hashtag: kclo2612              # optional: Kurzlink /kclo2612
sprache: en                    # nur für englische Beiträge
---

# Titel des Beitrags

Anreißer: ein bis drei Sätze für Übersicht und Feed.

<!-- more -->

Weiterer Text.
```

### Termin

```yaml
---
title: Expert Debriefing Praxis-Ausbildung Frühjahr 2027
untertitel: Zwei Tage Praxis am eigenen Fall   # optional, im Kopf
template: termin.html
hashtag: edmod27a              # Kurzlink /edmod27a
beginn: 2027-03-11 09:00
ende: 2027-03-12 17:00         # mehrtägig: erscheint als 11.-12.03.2027
ganztags: false
ort:
  name: Cogneon Akademie
  adresse: Bucherstr. 79a, 90419 Nürnberg
online: true                   # mit ort = "Hybride Veranstaltung"
kosten: 1.900 €
anmeldung: https://pretix.eu/cogneon/edmod27a/   # leer = kein Anmeldeknopf
kategorien: [Expert Debriefing Praxis-Ausbildung]
bild: assets/bilder/expert-debriefing-16-9.png
bild_alt: Zwei Menschen im Gespräch an einem Tisch
save_the_date: false
---

# Expert Debriefing Praxis-Ausbildung Frühjahr 2027

Beschreibung des Termins. Keinen eigenen Anmeldeknopf in den Text setzen,
den erzeugt die Seite aus `anmeldung`.
```

- **Ort und online:** nur `ort` = vor Ort, nur `online: true` = Online,
  beides = hybrid (Marke "Hybride Veranstaltung").
- **Anmeldung:** Der Knopf "Jetzt anmelden" erscheint im Kopf und unten, wenn
  `anmeldung` einen Link enthält und der Termin noch nicht vorbei ist.
- **Save the Date:** Steht nur das Datum fest, `save_the_date: true` setzen und
  `anmeldung` leer lassen. Der Termin bekommt die Marke "Save the Date", im
  Kalender gilt er als vorläufig. Sobald Text und Anmeldung stehen, Link
  eintragen und `save_the_date` entfernen.
- **Kategorien:** Name genügt. Die Adresse der Kategorieseite kommt aus
  `inhalte/termin-kategorien.yml` oder aus bestehenden Terminen; neue Namen
  bekommen automatisch eine Seite. `kategorie_slugs` brauchen nur
  übernommene WordPress-Termine.
- **Bild im Text:** Steht das Bild schon im Text, `bild_im_text: true` setzen,
  dann erscheint es nicht zusätzlich im Kopf.
- Übersicht (`/events/`), Kategorieseiten, Startseite und Kalenderdatei
  (`/events/cogneon.ics`) entstehen bei jedem Build; vergangene Termine wandern
  ins Archiv.

### Seite

```yaml
---
title: Titel der Seite
description: Ein Satz für Suchmaschinen und Vorschaukarten.
hashtag: akademie-tour         # optional
frozen: true                   # vom WordPress-Export nicht überschreiben
---
```

**Kommende Termine auf einer Seite:** Mit `termine_kategorie: <adresse>` im
Front Matter zeigt eine Seite die kommenden Termine dieser Kategorie, genau wie
unter /events/, jeweils mit Link auf den Termin. Die Adresse ist der letzte Teil
von `/events/kategorie/<adresse>/`, z.B. `edmod`. Die Liste erscheint dort, wo
im Text die Zeile `<!-- termine -->` steht, ohne diese Zeile am Seitenende.
Gibt es keinen kommenden Termin, steht dort ein Hinweis auf /events/. Beispiel:
`docs/edmod.md`. Neue Termine erscheinen nach dem nächsten Bau automatisch,
vergangene verschwinden von selbst.

Angebotsseiten mit Kopf, Karten und Ablauf nutzen `template: angebot.html`;
Aufbau siehe `docs/angebote.md` und "Kopfbild auf Unterseiten".

### Bilder

- **Format:** 16:9 für Beitrags-, Termin- und Kopfbilder, dasselbe Bild wie für
  Präsentationen und Videostreams. Breite höchstens 1920 Pixel, PNG oder JPG.
- **Wiederkehrende Bilder** (z.B. eines für alle Expert-Debriefing-Ausbildungen,
  das KCLO-Banner) einmal unter `docs/assets/bilder/` ablegen, sprechend
  benennen und überall darauf verweisen:
  `bild: assets/bilder/expert-debriefing-16-9.png`. Ein neues Motiv ersetzt
  dann alle Verwendungen auf einmal, wenn es denselben Dateinamen bekommt.
- **Einmalige Bilder** (Keyvisual einer bestimmten Veranstaltung, Fotos in einem
  Beitrag) in VS Code in den Text einfügen oder hineinziehen. Sie landen unter
  `docs/wp-content/uploads/JJJJ/MM/`; den Pfad bei Bedarf in `bild:` übernehmen.
- **Bestehende Bilder** aus WordPress liegen unter `docs/wp-content/uploads/`
  und können weiterverwendet werden.
- **Bildbeschreibung:** `bild_alt` bzw. `![Beschreibung](pfad)` sagt, was zu sehen
  ist. Rein dekorative Bilder ohne Beschreibung.
- **Große Fotos** vor dem Einchecken verkleinern (längste Kante 1920 Pixel):
  `python3 scripts/optimize_media.py` für `docs/wp-content/`,
  `python3 scripts/optimize_media.py --dir docs/assets/bilder` für wiederkehrende Bilder.
- Bilder von Personen nur mit deren Einverständnis, Logos und Werke Dritter
  nur mit Erlaubnis (siehe `LICENSE-INHALTE.md`).

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

## Podcast auf der Startseite

Unter Blog und Terminen zeigt die Startseite die neuesten Folgen von "Keep Calm
& Learn On". Die Folgen kommen beim Bauen aus dem Feed auf podcasts.cogneon.io,
also jede Nacht und bei jedem Merge neu. Von Hand gepflegt wird nur
`inhalte/podcast.yml`:

- `angepinnt`: Folgen, die oben stehen sollen. Adresse der Folge oder nur ihr
  letzter Teil, z.B. `personal-knowledge-mastery-mit-harold-jarche`.
- `bild`, `bild_alt`: Foto links.
- `plattformen`: Abo-Links. Die Adressen für Apple Podcasts und Spotify stehen
  im Feed. Mit `logo: assets/bilder/podcast/apple.svg` erscheint statt des
  Namens das Abzeichen der Plattform (offizielle Abzeichen von den
  Marketing-Seiten der Plattformen herunterladen).
- `anzahl`: wie viele Folgen (Standard 5).

Ist der Feed beim Bauen nicht erreichbar, bleibt der letzte Stand bzw. der
Abschnitt entfällt; der Build läuft weiter. Lokal testen ohne Netz:
`python3 scripts/build_data.py --podcast-feed tests/daten/podcast-feed.xml`.

## Teilen in sozialen Netzwerken

**Vorschaubilder:** Jede Seite, jeder Beitrag und jeder Termin bekommt beim
Veröffentlichen ein Vorschaubild 1200x630 (Logo, Art, Titel, Datum/Ort), das
LinkedIn, Mastodon, Signal & Co. beim Teilen eines Links zeigen. Dazu
Beschreibung (Anriss des Textes) und Titel als `og:`-Angaben.
`scripts/build_social.py` zeichnet nur geänderte Bilder neu. Lokal ist das
nicht nötig; wer die Bilder sehen will: `python3 scripts/build_social.py`,
Ergebnis in `docs/assets/social/`.

**Mastodon:** Nach einem Merge postet GitHub für jeden neuen Blogbeitrag und
jeden neuen Termin einen Toot ("Neuer Blog-Beitrag auf cogneon.de: Titel" +
Link). Voraussetzung: Secrets `MASTODON_INSTANZ` (z.B.
`https://mastodon.social`) und `MASTODON_TOKEN` (Mastodon: Einstellungen >
Entwicklung > Neue Anwendung, Recht `write:statuses` und
`read:accounts`/`read:statuses`). Ohne Secrets passiert nichts. Nicht gepostet
werden Entwürfe, Beiträge älter als 14 Tage oder mit Datum in der Zukunft,
vergangene Termine und alles, wenn mehr als 3 neue Einträge auf einmal kommen
(Import). Was passiert ist, steht in der Zusammenfassung des Laufs unter Actions.

**Kommentare aus dem Fediverse:** Unter jedem Blogbeitrag, zu dem es einen
Toot gibt, steht ein Abschnitt "Kommentare". Kommentare sind die öffentlichen
Antworten auf den Toot; sie werden erst nach Klick auf "Kommentare laden"
direkt von der Mastodon-Instanz geholt und bereinigt angezeigt (ohne
Profilbilder). Idee nach Carl Schwan.

- Welcher Toot zu welchem Beitrag gehört, speichert der Bot nach dem Posten
  im Branch `daten/mastodon` (Datei `mastodon.json`) und startet einen zweiten
  Lauf, damit der Abschnitt sofort erscheint. Den Branch nicht löschen.
- Ältere Beiträge: im Front Matter `mastodon: <Link zum Toot>` eintragen.
- Einzelne Antworten ausblenden: Link der Antwort in `inhalte/kommentare.yml`
  unter `ausblenden`.

**Bluesky:** Genauso wie Mastodon, über `scripts/bluesky.py` mit einer
Link-Karte samt Vorschaubild. Secrets: `BLUESKY_HANDLE`
(`cogneon.eurosky.social`) und `BLUESKY_APP_PASSWORD` (App-Passwort, nicht das
Konto-Passwort). Antworten auf Bluesky erscheinen im selben Kommentarbereich
wie die von Mastodon, nach Zeit sortiert und mit Herkunft gekennzeichnet. Für
ältere Beiträge im Front Matter: `bluesky: https://bsky.app/profile/…/post/…`.
In `inhalte/kommentare.yml` unter `ausblenden` funktionieren Links aus beiden
Netzwerken.

**LinkedIn:** Den Blog-Feed `https://cogneon.de/feed.xml` in der
Einstellungen der Unternehmensseite unter "Manage Content Sharing" eintragen
(deutsche Oberfläche: sinngemäß "Inhalte teilen").

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
