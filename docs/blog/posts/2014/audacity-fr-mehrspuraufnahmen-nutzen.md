---
title: Audacity für Mehrspuraufnahmen nutzen
date:
  created: '2014-11-23'
  updated: '2021-05-16'
slug: audacity-fr-mehrspuraufnahmen-nutzen
authors:
- simon-dueckert
categories:
- Podcast und Multimedia
tags:
- Podcasting
- Podcast
wp:
  id: 1001
  link: https://cogneon.de/2014/11/23/audacity-fr-mehrspuraufnahmen-nutzen/
  featured_media: null
---

# Audacity für Mehrspuraufnahmen nutzen

Eines meiner Ziele beim [4. Podlove Podcaster Workshop](http://metaebene.me/blog/2014/08/17/4-podlove-podcaster-workshop-in-berlin-am-22-23-november-2014/) (#ppw14b) in Berlin war, [Audacity](http://wiki.cogneon.de/Audacity) zusammen mit dem [Podcast-Studio unseres Media Labs](http://wiki.cogneon.de/Podcast_Studio_%28Cogneon_Media_Lab%29) für Mehrspur-Audio-Aufnahmen verwenden zu können. Natürlich wurde ich hier mehrfach gefragt “WARUM AUDACITY???”, denn in der Podcast-Szene sind hauptsächlich Apple-Anhänger unterwegs und die nutzen natürlich eher Garageband oder Reaper/Ultraschall.

<!-- more -->

Unser Einsatzszenario ist allerdings etwas anders. Wir wollen Wissensarbeiter in Unternehmen in die Lage versetzen, selber Audio und Video im Kontext der Wissensteilung zu verwenden. Dabei haben wir mit zwei Grundproblemen zu kämpfen:

1. Unternehmen sind i.d.R. reine **Windows-Umgebungen** (in unserem Kundenkreis z.B. fast ausschließlich Windows 7).
2. Die Mitarbeiter haben **keine Administrations-/Konfigurationsrechte** und nutzen durch die IT vorkonfigurierte Rechner. Dort sind meist keine Audio- und/oder Videoeditoren vorhanden.

D.h. wir benötigen eine Windows-Audio-Software, die sich ohne lokale Installation auf dem Rechner nutzen lässt (Portable Software). Hierfür fiel die Wahl auf das einfach zu bedienende Audacity, das allerdings standardmäßig nur Mono- und Stereo-Aufnahmen unterstützt (s.a. Multichannel Recording mit Audactity). Für Mehrspuraufnahmen kann z.B. das Audio Stream Input/Output Protokoll (ASIO) verwendet werden, das aber aus Lizenzgründen nicht mit Audacity ausgeliefert werden kann.

Der einzige Weg Audacity Mehrkanal-fähig zu machen ist, sich die einzelnen Quellen herunterzuladen und von Grund auf neu zu kompilieren. Wahrscheinlich keine allzu schwere Aufgabe für einen Programmierer, aber von ein bisschen Raspberry-Pi-Programmierung mit Python abgesehen, waren meine letzten Software-Entwicklungen in der Uni Mitte der 90er Jahre.

Daher hat es mich gestern einen halben Tag gekostet, die Entwicklungsumgebung mit allen Quellen so einzurichten, dass man Audacity darauf für Windows kompilieren, mit den ASIO-Treibern versehen und portable auf einen USB-Stick kopieren kann. Das ganze habe ich mit einer 6-Kanal-Aufnahme mit dem Podcast-Studio heute morgen getestet und es hat ganz hervorragend geklappt :-) In unserem habe ich unter [Tipps&Tricks zu Audacity](http://wiki.cogneon.de/Audacity) die Hauptquellen mit den Anleitungen verlinkt. Wer Hilfe bei diesem Vorhaben braucht, kann sich gerne bei mir melden. Unten ein Screenshot des Ergebnisses.
