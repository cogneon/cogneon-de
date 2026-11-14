# Seitenstruktur cogneon.de

Stand: 14.11.2026 - abgestimmter Entwurf, Grundlage für Navigation, Startseite und Design.

## Ziel

Die Website soll zwei Dinge leisten:

1. Die Angebote zu Wissensmanagement und Lernenden Organisationen sichtbar machen - verkaufsfördernd, ohne aufdringlich zu sein.
2. Die Kompetenz von Cogneon belegen.

Positionierung: "Wissen. Lernen. Wirken." - Cogneon als Partner von Organisationen für die Wissensgesellschaft des 21. Jahrhunderts. Wissensmanagement ist kein reines Technikthema, sondern die Entwicklung einer Lernenden Organisation in den Dimensionen Mensch, Organisation und Technik.

## Grundsätze

- Wenige Hauptpunkte in der Navigation.
- Einstieg nach Anlass des Käufers, nicht nach Leistungsart.
- Jede Seite endet mit demselben nächsten Schritt: Erstgespräch.
- Alte Adressen bleiben erreichbar (Cool URLs don't change).
- Barrierefreiheit nach WCAG/BITV ist feste Anforderung.
- Keine Drittanbieter-Einbindungen: Schriften, Skripte und Bilder liegen lokal (DSGVO, kein Cookie-Banner).

## Wer kommt mit welchem Anlass

| Wer | Anlass | Einstieg |
|---|---|---|
| Verantwortliche und Projektleitungen für Wissensmanagement | suchen fachliches Sparring oder einen Coach | Knowledge Excellence Coach |
| Geschäftsleitung, Eigentümer, obere Führung | wollen die "Wissensbrille" in der Organisation | Wissensbeirat |
| Fachabteilungen, Projektleitungen, HR | verlieren Wissensträger durch Ruhestand oder Abwesenheit | Wissenstransfer |
| IT-Leitung, CIO, IT-Projektleitung | konzipieren, migrieren oder erneuern Intranet, Wiki, soziale Netzwerke, KI-Systeme | Wissensinfrastruktur |
| HR und Personalentwicklung | wollen Lernen modernisieren | Learning Sessions, Communities & Barcamps |

## Hauptnavigation

**Angebote · Akademie · Blog · Termine · Über uns** - dazu rechts die **Suche** und der Knopf **Erstgespräch**.

- "Startseite" entfällt als Menüpunkt, dorthin führt das Logo.
- "Kontakt" wird zum Knopf "Erstgespräch".
- "Ressourcen" wandert in den Footer.
- "Themen" wird aufgelöst. Die Adresse `/themen/` leitet auf `/angebote/` um. Themen werden künftig im Wiki vertieft.

## Angebote

Gliederung nach den zwei Blickwinkeln der Wissenstreppe von Klaus North.

### Strategisches Wissensmanagement

| Angebot | Unterzeile |
|---|---|
| Knowledge Excellence Coach | Dauerhafte Begleitung interner Wissensmanagement-Teams |
| Wissensbeirat | Die Wissensperspektive für Geschäftsleitung und Eigentümer |
| Knowledge Pioneers | Mitgliedschaft für Organisationen |

### Operatives Wissensmanagement

| Angebot | Unterzeile |
|---|---|
| Wissenstransfer | Expert Debriefing als Dienstleistung und Ausbildung. Project Debriefing und Team Debriefing auf Anfrage, ohne festes Paket |
| Wissensinfrastruktur | Intranet, Wiki, digitaler Arbeitsplatz, KI-Systeme - Konzeption, Migration, Relaunch |
| Communities & Barcamps | Communities of Practice aufbauen, Barcamps und Lern-Events konzipieren |
| Learning Sessions | Katalog von Sessions und Impulsvorträgen mit Kategorien, darunter Microsoft 365 |
| Personal Knowledge Excellence | Persönliches Wissensmanagement fördern |

Nicht in der Navigation: Akademie online. Sie kommt erst, wenn es ein Angebot gibt.

### Übersichtsseiten und Angebotsseiten

Ein Angebot mit mehreren Formaten bekommt eine Übersichtsseite als Weiche, jedes Format eine eigene Angebotsseite mit eigener Adresse. Beispiel Wissenstransfer:

- `/wissenstransfer/` - Übersicht: drei Formate für drei Anlässe
- `/expert-debriefing/` - eigene Angebotsseite (Interviewprozess, feste Pakete)
- Project Debriefing und Team Debriefing (Workshop-Formate) - zunächst nur auf der Übersicht, eigene Seiten, sobald sie als Paket angeboten werden

Eigene Adressen machen jedes Angebot einzeln verlinkbar und in der Webanalyse einzeln auswertbar: Aufrufe, Einstiegsseiten und Klicks auf "Erstgespräch" je Angebot.

### Aufbau jeder Angebotsseite

1. Für wen und bei welchem Anlass
2. Ablauf
3. Dauer und Format (vor Ort, virtuell, hybrid)
4. Nächste Termine, wo es welche gibt
5. Preisrahmen, wo einer genannt werden soll
6. Fallbeispiele ("So haben es andere gemacht")
7. Erstgespräch

Die Punkte 2 bis 5 beantworten, wonach Interessenten bisher fragen mussten.

### Learning Sessions als Katalog

Eine Datei pro Session mit Steckbrief im Frontmatter: Titel, Kategorie, Dauer, Format, Zielgruppe, Referent. Ein Skript erzeugt daraus vor dem Build die Übersicht mit Filter. Jede Session hat eine eigene Adresse.

## Startseite

1. **Hero**: Claim, Text, Hauptknopf "Erstgespräch", Nebenknopf "Angebote".
2. **Einstieg nach Anlass**: vier bis fünf Karten in den Worten der Käufer, zum Beispiel "Ein Experte verlässt uns", "Wir bauen Wissensmanagement auf", "Wir lösen Intranet oder Wiki ab", "Wir wollen Lernen modernisieren", "Wissen wird Chefsache". Wissenstransfer steht an erster Stelle.
3. **Belege**: ruhige Logo-Leiste, eine Zahl, ein Zitat, Link zu den Fallbeispielen.
4. **Highlights**: Ankündigungen mit Ablaufdatum, in der Regel bis zu drei, technisch nicht begrenzt. Zum Start: Menerva-Programm 2036.
5. **Aktuelles**: die drei neuesten Blogbeiträge und die drei nächsten Termine, ohne Karussell.
6. **Auf dem Laufenden**: Newsletter-Anmeldung als Hauptsache, Signal und Community als Links.

Die bisherigen farbigen Blöcke werden aufgelöst: Abschnitte entstehen durch Weißraum, Typografie und Bild, Orange bleibt Akzent.

### Highlights

Eine Datei pro Highlight mit Bild, Titel, Kurztext, Link, Reihenfolge und "gültig bis". Abgelaufene Highlights verschwinden mit dem nächsten nächtlichen Build von selbst.

## Blog

- Technisch ist alles ein Blogbeitrag. "News" und "Pressemitteilungen" sind Kategorien.
- Offizielle Mitteilungen erscheinen unter dem Autor "Cogneon", Fachbeiträge unter dem Namen der Person.
- Beitrags-Adressen bleiben wie in WordPress: `/JJJJ/MM/TT/titel/`.
- Am Ende jedes Beitrags: Newsletter-Anmeldung und Link zur Diskussion in der Community.

## Termine

Eine Datei pro Termin. Daraus entstehen Terminseiten, Kalender-Feed und die Listen auf Startseite und Angebotsseiten. Kostenpflichtige Termine werden mit dem Ticketing verbunden.

## Footer

- Ressourcen: Podcasts, YouTube, Wiki, Community CONNECT, lernOS, Menerva-Programm 2036, Benchlearning, Top 10s (kuratierte Quellensammlung, wird überarbeitet)
- Newsletter-Anmeldung
- Kontakt, Impressum, Datenschutz
- Soziale Netzwerke

## Kontaktweg

- Knopf "Erstgespräch anfragen" auf jeder Angebotsseite: 30 Minuten, kostenlos.
- Die Anfrage läuft per E-Mail mit vorausgefülltem Betreff. Das bisherige Formular entfällt.
- Kein offener Terminkalender. Der Termin wird in der Antwort vereinbart.
- Später als Option daneben: ein Chatbot zur Vorklärung, der die Anfrage per E-Mail übergibt. Er ist als öffentlicher Showcase gedacht, nicht als Vertriebskanal.

## Belege

- **Kunden**: Start mit den Kunden der heutigen Logo-Leiste. Vor dem Go-live je Kunde prüfen, ob die Nennung freigegeben ist.
- **Fallbeispiele**: eigene Inhaltsart, eine Datei pro Fallbeispiel mit Kunde, Branche, Anlass, Angebot und Link zur Quelle. Erscheinen automatisch auf den passenden Angebotsseiten. Das Material ist vorhanden, aber verstreut, und wird gesammelt.
- **Zitate**: Kundenstimmen, jeweils mit Zustimmung zur Veröffentlichung von Text und Name.
- **Zahlen**: nur belegbare Angaben.

## Design

Gewählte Richtung: "Kontrast" - dunkler Einstieg mit großem Claim, eigene Schrift für Überschriften, Orange als tragende Markenfarbe. Die Abschnitte "Womit können wir helfen?" und "Im Blick" nutzen Karten auf hellem Grund.

- Das Verkehrsschild "Wissensdatenbank → Lernende Organisation" aus der Akademie bekommt einen eigenen Abschnitt auf der Startseite.
- Farbkontraste: Text erfüllt WCAG AA (4,5:1). Bewusste Ausnahme: der Abschnitt "Belege" auf der Startseite mit weißer Schrift auf dem Markenorange `#ff6600` (2,94:1). Entschieden am 14.11.2026, weil diese Kombination zur Marke gehört. Die Ausnahme gilt nur für diesen Abschnitt, nicht für Fließtext, Links oder Bedienelemente.
- Das Verkehrsschild liegt als Bild unter `docs/assets/bilder/`. Es wird durch die SVG-Fassung ersetzt, sobald sie vorliegt.
- Schriften werden lokal ausgeliefert: Geist für Überschriften, Inter für Fließtext (beide Open Font License). Entschieden am 14.11.2026.

## Bausteine

Die Seiten werden aus wiederverwendbaren Bausteinen gebaut, damit sie einheitlich aussehen:

- **Seitenvorlagen**: Angebotsseite, Übersichtsseite, Startseite. Die Redaktion füllt Felder im Frontmatter und Text, das Layout kommt aus der Vorlage.
- **Bausteine im Text**: Karten-Raster, Knopf, Hinweiskasten, Akkordeon/FAQ, Ablauf in Schritten, Zitat, Logo-Leiste, Erstgespräch-Block. Sie werden als kurze Markdown- oder HTML-Schnipsel eingesetzt.
- **Textbausteine**: wiederkehrende Abschnitte wie der Erstgespräch-Block liegen einmal im Repo und werden eingebunden.
- **Bausteinseite**: Eine Seite im Repo zeigt jeden Baustein mit Beispiel und Schreibweise. Sie ist zugleich der Design-Guide.

## Sprachregel

Eigennamen englisch, alles andere deutsch.

- Produkte tragen englische Namen: Expert Debriefing, Knowledge Pioneers, Learning Sessions, Knowledge Excellence Coach.
- Navigation, Kategorien und Beschreibungen sind deutsch.
- Jeder Produktname bekommt eine deutsche Unterzeile.
- "Wissensbeirat" bleibt deutsch.

In der englischen Version der Website bleiben die Produktnamen unverändert.

## Umgang mit den bestehenden Seiten

| Adresse | Künftig |
|---|---|
| `/` | Startseite, neu gebaut |
| `/angebote/` | Übersicht der Angebote, neu gebaut |
| `/akademie/` | Hauptnavigation: Ort für Offsites, Workshops und Projekte mit fachlicher Begleitung |
| `/blog/` | Hauptnavigation: Blog-Übersicht |
| `/events/` | Hauptnavigation: Termine |
| `/ueber-uns/` | Hauptnavigation, später mit Teamseiten |
| `/kontakt/` | bleibt, Ziel des Knopfs "Erstgespräch" |
| `/wissenstransfer/` | Angebot Wissenstransfer |
| `/expert-debriefing/` | Angebot Wissenstransfer, Unterseite |
| `/edmod/`, `/edmod-olk/` | Ausbildung Expert Debriefing, zu Wissenstransfer |
| `/ls-onenote/` | Learning Sessions, wird Eintrag im Katalog |
| `/newsletter/` | Weiterleitung auf die Anmeldung auf der Startseite (`/#newsletter`) |
| `/lernos/` | bleibt, Footer |
| `/4010km/` | Menerva-Programm 2036, bleibt, Footer und Highlight |
| `/blp26/` | Benchlearning, bleibt, Footer |
| `/top10/` | bleibt, Footer, wird überarbeitet |
| `/themen/` | wird aufgelöst, Umleitung auf `/angebote/` |
| `/podcast-2/` | entfällt, Umleitung auf podcasts.cogneon.io |
| `/impressum/`, `/datenschutz/` | bleiben unter gleicher Adresse, Inhalt wird aktualisiert |
| `/loscon23/`, `/audiobc23/`, `/c3managers/` | bleiben erreichbar, in keiner Navigation |
| `/kex/` | frühere Namensidee für Team und Project Debriefing. Inhalte fließen in das Angebot Wissenstransfer, Adresse leitet dorthin um |
| `/kme/` | agiler Ansatz zur Einführung von Wissensmanagement, Handwerkszeug des Knowledge Excellence Coach. Inhalte fließen in die Angebotsseite, Adresse leitet dorthin um. Die ausführliche Beschreibung kommt in den Leitfaden lernOS für Organisationen |
| `/nwow/` | früherer Versuch eines Session-Katalogs. Inhalte fließen in die Learning Sessions, Adresse leitet dorthin um |
| `/kme-olk/`, `/ok-msco/` | Online-Kurse hinter Passwort, werden nach SCORM überführt. Nicht Teil der Website, Verbleib mit der Online-Akademie zu klären |

## Offene Punkte

- Plattform für die Online-Akademie (Kurse, Badges, Zertifikate) und Verbleib der beiden Online-Kurse
- Benennung und Zuschnitt der Karten "Einstieg nach Anlass"
- Blog-Übersicht unter `/blog/`, während die Beiträge unter `/JJJJ/MM/TT/` liegen - technisch zu lösen
- Eigener Feed je Blog-Kategorie - technisch zu prüfen
- Preisangaben: bei welchen Angeboten ja, bei welchen nein
- Sammlung der Fallbeispiele und Freigabe der Kundennennungen
- Animation im dunklen Einstieg der Startseite: ruhig, ohne Video, abschaltbar bei "Bewegung reduzieren", mit Pause-Möglichkeit
- Moderatorenausbildung (heute `/edmod/`): Die Seite gehört zur Akademie, "Wissenstransfer" und "Expert Debriefing" verlinken darauf. Entschieden am 14.11.2026, Umsetzung offen
- Zitat auf der Startseite: bis zum Go-live durch ein Kundenzitat mit Position und Firma ersetzen oder ergänzen (Freigabe einholen)
