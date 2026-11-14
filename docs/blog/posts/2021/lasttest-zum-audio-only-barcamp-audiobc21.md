---
title: 'Lasttest zum Audio-only Barcamp #audiobc21'
date:
  created: '2021-01-26'
  updated: '2023-10-23'
slug: lasttest-zum-audio-only-barcamp-audiobc21
authors:
- simon-dueckert
categories:
- Events und Vorträge
tags:
- AudioOnlyBarcamp
- Podcasting
wp:
  id: 58368
  link: https://cogneon.de/2021/01/26/lasttest-zum-audio-only-barcamp-audiobc21/
  featured_media: 58371
---

# Lasttest zum Audio-only Barcamp #audiobc21

Um zu testen, ob wir die [Idee eines Audio-only Barcamps](/2021/01/20/call-for-ideas-das-1-audio-only-barcamp/) in unserer Infrastruktur umsetzen können, machen wir am **Donnerstag 28.01.2021 von 11:00-12:00 Uhr** einen **Lasttest**. Wir wollen mit mindestens einer dreistelligen Anzahl von Nutzer\*innen auf unserem Audio-Chat-Server Comble testen. Wer Lust und Zeit hat ist herzlich eingeladen. Ihr könnt gerne auch noch Kolleg\*innen dazu einladen. In diesem Blog findet ihr die Beschreibung, wie ihr am Lasttest teilnehmen könnt. Fragen gerne unten in die Kommentare schreiben.

<!-- more -->

## Update: Ergebnis des Lasttests

Alles in allem hat der Lasttest sehr gut funktioniert, wir konnten die Agenda wie geplant durchführen und es gab keine größeren Probleme. Es waren etwas über 40 Personen beim Lasttest dabei. Die Serverkonsole hat zeitweise eine Auslastung von 150% angezeigt, es gab aber keine Aussetzer oder Abstürze. Für das audiobc21 werden wir den Server temporär noch 1-2 Stufen aufstocken.

**Ergo: das audiobc21 Audio-only BarCamp wird stattfinden.**

**Aufzeichnung** des Lasttests (links die Server-Konsole mit den KPIs, rechts COMBLE, Video ist im Zeitraffer, 10 Minuten = 2 Stunden):

[YouTube: audiobc21 Lasttest](https://youtu.be/UuiBvT8sOxM){ .embed }

**Erfahrungen** aus dem Lasttest:

- Bei Nutzung von **Push-to-Talk** müssen erst die Pegel eingestellt werden, damit das Mikrofon sinnvoll aktiviert wird.
- Nach **Installation** von Mumble **auf dem Mac** erscheint eine Sicherheitsmeldung nach dem Start. Über Einstellungen->Sicherheit muss der Start von Mumble erst bestätigt werden.
- Im **Chat** werden sehr viele Nachrichten angezeigt (Raum betreten/verlassen, Muten/Unmuten etc.). Diese Kann man in den Einstellungen manuell deaktivieren, schön wäre an Tln. eine Standardeinstellung zu verteilen.
- Ein **Screencast mit der Ersteinrichtung** von Mumble auf einem Rechner und einem Smartphone wäre hilfreich.
- Beim **Saalmikrofon** wäre es gut, wenn die Personen in der Reihenfolge des „Anstellens“ angezeigt werden würden, aktuell geht es nach dem Alphabet (Simon prüft)

~~Als **nächster Schritt** wird eine Terminabstimmung an alle Tln. und auf Twitter bereitgestellt, mit dem wir den genauen Termin des Camps festlegen (Ende März/Anfang April).~~

**Termin für das audiobc21 ist der 29.04.2021 (10-17 Uhr)**, außerdem wird es ein „Get Together“ am Vorabend geben. Es haben sich einige Leute gefunden, die aktiv im Orga-Team mitwirken wollen. Wer noch dabei sein mag, einfach bei mir melden oder im Kanal [#audiobc21](/tag/audiobc21/) [in unserem Slack](https://join.slack.com/t/cogneon/shared_invite/zt-kgk2trls-s9hrjyLEDV8mZfH_fDe~wA) aufschlagen.

## VORAUSSETZUNGEN

Ihr braucht einen **Mumble-Client** für die Teilnahme, am besten schon einige Zeit **VOR dem Lasttest** installieren. Diesen gibt es für alle Plattformen (etwas ausführlichere Dokumentation und Links [in COPEDIA](https://wiki.cogneon.de/comble):

- [Download](https://www.mumble.info/downloads/) für Windows, Mac und Linux
- iOS App: [Mumble](https://apps.apple.com/de/app/mumble/id443472808), [Mumblefy](https://apps.apple.com/de/app/mumblefy/id858752232) (kostenpflichtig € 5,49, sonst habt ihr Werbung im Audio)
- Android App: Plumble, [Mumla](https://play.google.com/store/apps/details?id=se.lublin.mumla&hl=de&gl=US)
- **TIPP:** wer auf Windows keine Software installieren möchte/darf, kann sich auch die [Mumble Portable Version](https://portableapps.com/apps/internet/mumble-portable) herunterladen
- **TIPP:** in Mumble sollte man die Push-to-Talk-Funktion aktivieren, damit man nur beim Drücken einer Taste zu hören ist (vermindert Störgeräusche)
- **TIPP:** die nervigen Audio-Ansagen kann man im Menü abschalten (Text-to-Speech)

## EINWAHL

In **Mumble** müsst ihr einen Server mit **folgenden Zugangsdaten** hinzufügen und euch dann mit dem Server verbinden (geht zum Testen ab jetzt schon):

- **Adresse:** meet.cogneon.de
- **Port:** 64738
- **Benutzername:** kann frei gewählt werden (am besten vornamenachname, Sonderzeichen sind nicht erlaubt)
- **Passwort:** audiorocks

![](/wp-content/uploads/2021/01/comble-login.png)

## ABLAUF

- **10:30 Uhr:** ab jetzt ist jemand in der Lounge, ihr könnt euch schonmal einwählen und Fragen stellen/testen.
- **11:00 Uhr:** Begrüßung und Einführung in COMBLE und die Idee des Audio-only Barcamps.
  - **Bitte kommt pünktlich um 11:00 Uhr in den Raum „Publikum“ im Plenum.**
  - Die Idee des Audio-only Barcamps kurz erkärt
  - Der Ablauf heute (wichtigstes Ziel: Lasttest, Diskussion geeigneter Audio-Session-Formate, Anlegen temporärer Räume)
  - Die wichtigsten Funktionen von Mumble:
    - **Hinweis:** nicht alle Funktionen der Desktop-Anwendung sind in der mobilen App verfügbar
    - **Tipps:** Text-zu-Sprache deaktivieren, Anzahl der Benutzer je Kanal anzeigen (Einstellungen->Benutzerinterface)
    - **Raumwechsel** mit Doppelklick auf dem Raumnamen
    - **Mute/Unmute** manuell oder per Push-to-Talk (PTT)
    - **Taub-schalten:** wenn man sich kurz ausklinken will, kann man sich selber „taub“ (deaf) stellen
    - **Personen stumm stellen:** per Rechtsklick auf einer Person, kann man diese für sich stumm stellen (nicht für andere) oder deren Lautstärke anpassen
    - **Textchat** im Raum und privat mit einzelnen Personen
    - **Profil:** über Avatar und Kommentar könnt ihr euch ein Miniprofil erstellen (wird per Mouse-over angezeigt)
- **11:30 Uhr:** Diskussion in 7 Kleingruppen
  - Welche Arten von Sessions eignen sich für ein Audio-only Barcamp?
  - Dokumentieren eure Ideen bitte [in diesem Pad](https://meet.cogneon.de/pad/p/audiobc21-lasttest).
- **11:45 Uhr:** Gemeinsamer Abschluss
  - Was gefällt euch gut?
  - Gab es Probleme, was können wir besser machen?
- **11:55 Uhr:** Test des Anlegens eigener Räume
  - Klickt mit der rechten Maustaste auf die Lounge und legt einen temporären Raum an (Achtung: geht nur in Desktop-Anwendung, nicht in der mobilen App)
  - Gebt dem Raum einen sprechenden Namen (z.B. Thema, über dass ihr gerne sprechen wollt, oder einfach Walk&Talk), keine Sonderzeichen erlaubt
  - Wenn die letzte Person den Raum verlässt, schließt er sich automatisch (deswegen: temporär)
- **12:00 Uhr:** Ende des Lasttests (Zugang funktionier noch bis 28.01. EOB).

## FAQ

Einige schon gestellte Fragen beantworte ich an dieser Stelle gleich:

- **Welche technische Ausstattung brauche ich?<br>**Ein Desktop-Computer, Smartphone oder Tablet mit einem [Mumble-Client](https://www.mumble.info/downloads/) darauf. Für gute Audio-Qualität ein Headset oder zumindest einen Kopfhörer.
- **Geht es auch mit dem iPad?**<br>
  Ja, einfach die iOS App aus dem App Store installieren.
- **Ist die Nutzung direkt im Browser möglich?**<br>
  Nein, für die Nutzung von Mumble braucht ihr eine Desktop- oder Mobile-App.
- **Kann ich auch mobil teilnehmen?**<br>
  Ja, klar! Wir finden sogar, dass es eine gute Idee ist, am Audio-only Barcamp unterwegs, im Wald, beim Spazieren gehen, beim Wandern etc. teilzunehmen. In Videokonferenzen waren wir jetzt alle oft genug😉
