---
title: Neue Website - cogneon.de ist jetzt statisch, schneller und zweisprachig
date:
  created: '2026-11-30'
slug: neue-website-cogneon-de
authors:
- simon-dueckert
categories:
- Cogneon News
bild: assets/bilder/neue-website-startseite.jpg
tags:
- Website
---

# Neue Website - cogneon.de ist jetzt statisch, schneller und zweisprachig

Die Website von Cogneon hat schon einige Systeme erlebt: Angefangen hat sie als statisches HTML, gebaut mit Microsoft FrontPage. Danach kam Drupal, dann WordPress, beide auf PHP. Ab heute ist cogneon.de wieder statisches HTML - back to the roots. Die Inhalte sind dieselben, alle alten Links funktionieren weiter. Hier ein kompakter Überblick, warum wir umgestellt haben, wie die Seite gebaut ist und was neu ist.

<!-- more -->

## Warum wir umgestellt haben

WordPress hat uns lange gut gedient. Zuletzt überwogen aber die Nachteile. Die jüngsten Sicherheitslücken in PHP und die Angriffsflächen, die wir mit Plugins, Login und Datenbank hatten, kosteten Zeit und Nerven. Dazu kam deutlich mehr Spam in den Kommentaren, inzwischen oft von KI-Agenten erzeugt. Eine statische Website besteht aus fertigen HTML-Seiten. Es gibt keine Datenbank, kein Login und nichts, was ständig gepatcht werden muss. Die Seite lädt schneller, ist sicherer und günstiger im Betrieb.

Wichtiger ist uns aber etwas anderes: Alle Inhalte liegen jetzt als einfache Textdateien (Markdown) in einem Git-Repository. Damit gehören sie wirklich uns, sind versioniert und unabhängig von einem bestimmten System lesbar. Für eine Knowledge Company ist das auch ein Stück gelebtes Wissensmanagement.

## Agentische Pflege

Weil alles Text ist, können wir die Website gemeinsam mit einem KI-Agenten pflegen. Neue Funktionen, Übersetzungen, Prüfungen und Korrekturen entstehen im Dialog mit Claude. Der Agent schlägt jede Änderung als Pull Request vor, wir prüfen sie und geben sie frei. So bleibt die Verantwortung beim Menschen, die Fleißarbeit erledigt die Maschine. Die Umstellung selbst ist auf diese Weise entstanden.

## Technische Umsetzung

- **Zensical** baut aus den Markdown-Dateien die Website. Es kommt vom Team hinter Material for MkDocs.
- **GitHub** hält Inhalte und Code. Das Repository [cogneon/cogneon-de](https://github.com/cogneon/cogneon-de) ist öffentlich, der Code steht unter MIT-Lizenz, die Inhalte unter CC BY 4.0 (mit Ausnahmen).
- **GitHub Actions** baut die Seite bei jeder Änderung und jede Nacht neu und lädt sie zu unserem Hoster hoch.
- **Weiterleitungen** sorgen dafür, dass rund 1.600 Adressen der alten Website weiter funktionieren, ebenso Kurzlinks wie [/wtc27](/wtc27).
- **VS Code mit Front Matter CMS** ist unser Redaktionswerkzeug für Beiträge und Termine.

## Was neu ist

- **Schnelle Suche:** Die Suche läuft direkt im Browser und zeigt Ergebnisse schon beim Tippen.
- **Englische Version:** Die wichtigsten Seiten gibt es jetzt auch auf Englisch, mit Sprachumschalter im Kopf der Seite.
- **Dark Mode:** Die Seite folgt der Einstellung eures Geräts und lässt sich hell oder dunkel schalten.
- **llms.txt:** Unter [/llms.txt](/llms.txt) finden KI-Assistenten eine kompakte Übersicht unserer Seiten.
- **Termine mit Kalenderdatei:** Jeder Termin lässt sich mit einem Klick in den eigenen Kalender übernehmen. Hybride Veranstaltungen sind gekennzeichnet.
- **Podcast auf der Startseite:** Die neuesten Folgen von "Keep Calm & Learn On" erscheinen automatisch, mit Links zum Abonnieren.
- **Kommentare aus dem Fediverse:** Neue Beiträge kündigen wir auf Mastodon an. Antworten dort erscheinen als Kommentare unter dem Beitrag, geladen erst nach einem Klick.
- **Vorschaubilder beim Teilen:** Jede Seite bringt ein eigenes Vorschaubild für LinkedIn, Mastodon & Co. mit.
- **Karte mit Luftbild:** Die Anfahrt zur Cogneon Akademie zeigt eine OpenStreetMap-Karte, wahlweise mit Luftbild. Sie lädt erst nach einem Klick.
- **Adventskalender:** Zum Start gibt es den [Wissensmanagement-Adventskalender](/advent/) mit 24 Türchen, die sich jeweils am Vorabend öffnen.

Wenn euch etwas auffällt, das nicht funktioniert, oder ihr eine Idee habt, schreibt uns an [info@cogneon.de](mailto:info@cogneon.de?subject=Neue%20Website).

**KEEP CALM & LEARN ON**<br>
Euer Simon
