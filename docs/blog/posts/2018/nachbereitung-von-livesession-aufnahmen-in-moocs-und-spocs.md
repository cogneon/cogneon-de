---
title: Nachbereitung von Livesession-Aufnahmen in MOOCs und SPOCs
date:
  created: '2018-12-05'
  updated: '2020-03-06'
slug: nachbereitung-von-livesession-aufnahmen-in-moocs-und-spocs
authors:
- simon-dueckert
categories:
- Podcast und Multimedia
tags:
- DIYMultimedia
- Multimedia
- MOOC
- Podcasting
bild: wp-content/uploads/2018/10/CCCOGMN-Invitation.png
wp:
  id: 54303
  link: https://cogneon.de/2018/12/05/nachbereitung-von-livesession-aufnahmen-in-moocs-und-spocs/
  featured_media: 54121
---

# Nachbereitung von Livesession-Aufnahmen in MOOCs und SPOCs

Gerade läuft der [Cross Company Course on Guide or Multiplier Networks](/2018/10/05/cross-company-course-on-guide-multiplier-networks-cccgomn/) (CCCGOMN), in dem genau wie im [Management 2.0 MOOC](https://wiki.cogneon.de/Management_2.0_MOOC) im Jahr 2013 auch wöchentliche Livesessions gemacht werden. Den Teilnehmern wird im Nachgang die Videoaufnahme (mp4) und zusätzlich eine Audioaufnahme (mp3) bereitgestellt. Dieser Beitrag beschreibt kurz, wie der Prozess der Nachbereitung erfolgt.

<!-- more -->

![](/wp-content/uploads/2018/12/cccgomn-nachbereitung.png)

Folgende Schritte verwende ich nach den Livesessions (Dauer: ca. 1h):

- Videokonferenz-Tools wie GoToMeeting oder Skype for Business erzeugen als Aufnahme meist eine mp4-Datei, die ich als Ausgangsbasis verwende
- Die mp4-Datei imporiere ich in ein Videoschnitt-Programm, in meinem Fall das kostenlose [DaVinci Resolve](https://www.blackmagicdesign.com/de/products/davinciresolve)
- Im Videoschnitt-Programm trimme ich Anfang und Ende und schneide alle Stellen, an denen Längen durch Wechsel zwischen den Rerferenten oder technische Probleme entstehen. Für schnelles Arbeiten ist es sinnvoll, sich die Tastaturkürzel des verwendeten Programms anzusehen
- Das geschnittene Ergebnis exportiere ich als mp4-Datei mit einer maximalen Datenrate von 2000 kBit/s (Achtung: viele Programme schlagen deutlich höhere Datenraten vor, was bei Livesession-Aufzeichnungen aber nicht sinnvoll ist, da es die Dateigröße deutlich vergrößert
- Danach erzeuge ich mit dem Kommandozeilen-Tool [FFmpeg](https://wiki.cogneon.de/FFmpeg) aus der mp4-Datei eine mp3-Datei (Audio)
- Beide Dateien lade ich in unsere Plattform Coshare und verlinke sie mit der entsprechenden Seite des Kurses für den Download
- Fertig :-)

Wenn Ihr auch interessante Workflows habt, die Euch Zeit sparen, könnt Ihr die gerne in den Kommentaren kurz beschreiben.
