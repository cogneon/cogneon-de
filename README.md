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
| `overrides/` | Vorlagen: Kopf- und Fußzeile, Startseite (`home.html`), Angebotsseiten (`angebot.html`) |
| `docs/assets/stylesheets/cogneon.css` | Gestaltung. Schriften liegen lokal in `docs/assets/fonts/` |
| `inhalte/aktuell.yml` | Highlights und Termine der Startseite |
| `scripts/build_data.py` | erzeugt daraus und aus den Blogbeiträgen `_data/aktuell.yml` |
| `scripts/wp_export.py` | wiederholbarer Export aus WordPress |
| `scripts/check_urls.py` | prüft, ob alle alten URLs erreichbar bleiben |
| `migration/` | Berichte des Exports (Inventar, URL-Liste, URL-Check) |

## Lokal arbeiten

```bash
pip install -r requirements.txt
python scripts/build_data.py   # Daten der Startseite erzeugen
zensical serve          # Vorschau unter http://localhost:8000
python -m pytest tests  # Tests des Export-Skripts
```

## Export aus WordPress

Der Export liest die öffentliche REST-API von cogneon.de. Er kann beliebig oft laufen.

```bash
python scripts/wp_export.py --inventory-only   # nur zählen
python scripts/wp_export.py --limit 10         # Pilot
python scripts/wp_export.py                    # alles
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

Ohne lokale Installation: Workflow **WordPress-Export** unter *Actions* starten. Das Ergebnis hängt als Artefakt am Lauf.

## URL-Check

Alte URLs dürfen nicht brechen. Nach dem Build:

```bash
zensical build
python scripts/check_urls.py --url-map migration/url-map.csv --url-list migration/old-urls.txt
```

URLs, die es als Seite nicht mehr gibt, brauchen einen Eintrag in `migration/redirects.map` (`alter-pfad neues-ziel`, eine Regel pro Zeile). Aus dieser Datei entsteht später die Redirect-Konfiguration des Webservers.

## Arbeitsweise

- `main` ist geschützt, Änderungen kommen per Pull Request.
- Jeder Pull Request wird gebaut und getestet (Workflow **Build**).
