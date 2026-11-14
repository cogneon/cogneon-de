---
title: 'Podlove Podcaster Workshop #ppw15b'
date:
  created: '2015-11-14'
  updated: '2023-10-23'
slug: podlove-podcaster-workshop-ppw15b
authors:
- simon-dueckert
categories:
- Podcast und Multimedia
tags:
- Podcasting
- ChaosComputerClub
- Podcast
wp:
  id: 1568
  link: https://cogneon.de/2015/11/14/podlove-podcaster-workshop-ppw15b/
  featured_media: null
---

# Podlove Podcaster Workshop #ppw15b

Vom 13.-15.11.2015 war ich auf dem **6. Podlove Podcaster Workshop** (#ppw15w) in den Räumen von [Wikimedia Deutschland](http://wikimedia.de) in Berlin. Workshop ist dabei eigentlich der falsche Begriff, denn die beiden Tagen laufen eigentlich in einer hybriden Form Konferenz/Unkonferenz statt. Der Veranstaltungsort verfügt über einen großen Plenumsraum und außerdem vier weitere Räume (außer den Büros der Wikimedia-Mitarbeiter) für Breakouts. Die Vormittage am Samstag und am Sonntag waren jeweils mit 4-6 Vorträgen belegt, der Nachmittag wurde im Barcamp-Stil geplant und durchgeführt (s.a. Programm in frab). Durch Material und Knowhow des CCC VOC sind die Vorträge mit etwas Zeitversatz auch auf YouTube verfügbar ([Playlist mit allen Vorträgen](https://www.youtube.com/watch?v=2qwyzPIon1Q&list=PLIoqMTM7qDWolqxEiNIX4rVLa8lAqT10_)):

<!-- more -->

[YouTube: Begrüßung – #ppw15b](https://www.youtube.com/watch?v=2qwyzPIon1Q){ .embed }

Derartige Veranstaltungen sind großartige Lernevents, da große Bandbreite von Material und Expertise direkt vor Ort ist. Ich habe dieses Mal im Kern zwei Lernziele verfolgt. Zunächst wollte ich lernen, wie ich mit USB-Audio-Interface (Focusrite Scarlett 2i4) und [Reaper](http://reaper.fm)/[Ultraschall](http://ultraschall.fm) statt Audacity aufnehmen kann. Dazu musste zunächst mal Reaper und Ultraschall instellieren. Der Vortrag von Ralf Stockmann zur neuen Version Ultraschall 2.0 war dazu sehr hilfreich:

[YouTube: Ultraschall 2.0 – #ppw15b](https://www.youtube.com/watch?v=xgWthDHSswg){ .embed }

Die Installation verlief problemlos, bis auf die Stellen, an denen ich mich nicht an die Anleitung gehalten habe :-) Da alle unsere Kunden und wir selber auch auf Windows sind (7 und 10), musste das natürlich auf dieser Plattform funktionieren. Mein Ziel war, in der DAW Reaper möglichst viel digital machen zu können und möglichst wenig Audio-Hardware verwenden zu müssen. Insbesondere wollte ich für den Podcast [Knowledge on Air](http://knowledge-on-air.de) (KOA) mit Ulrich Schmidt, der ja mittlerweile in Hannover wohnt,  den gesamten Aufnahme- und Produktionsprozess in Software machen können (Stichwort: N-1-Schaltung mit Skype).

Hierfür ist es notwendig in das Audio-Routing im Windows-Betriebssystem einzugreifen. Auf dem Mac arbeitet man hier mit [Soundflower](https://rogueamoeba.com/freebies/soundflower/), in Windows verwendet man die [Virutal Audio Cables](http://software.muzychenko.net/eng/vac.htm) und den [ASIO4All Treiber](http://www.asio4all.com/). Nach einer Anleitung von Ben habe ich beides installiert und nach ersten Verständnisproblemen dann auch zum Laufen bekommen. Ich habe jetzt in Reaper eine Vorlage liegen, mit der ich mit einem Klick für eine neue KOA-Episode alle Einstellungen einrichten und die Episode aufnehmen kann.

![reaper-ultraschall](/wp-content/uploads/2015/11/reaper-ultraschall.jpg)

Durch die virtuellen Audiokabel kann man nicht nur Skybe ankabeln, sondern auch Google Hangouts, Lync & Co. Auch mit einem SIP-Client ([Phoner Lite](http://phonerlite.de)) habe ich den Verbindungsaufbau zu einem Telefon erfolgreich getestet. Was noch nicht ging ist der Aufbau einer HD Voice Verbindung (G.722 mit über 7kHz statt 3,5 kHz Bandbreite) ist mir noch nicht gelungen, aber da forsche ich noch etwas. Mit diesem Setup werden wir jetzt die zwei Medienarbeitsplätze in der Akademie ausstatten, so dass auch Gäste Podcasts unter Einbindung von Remote-Teilnehmern machen können. Dazu werden wir in naher Zukunft auch die Seiten rund um [Corporate Podcasts](http://wiki.cogneon.de/Corporate_Podcast) im Wiki ausbauen.
