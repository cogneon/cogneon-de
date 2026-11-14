---
title: Livestreaming von Vorträgen – Ein Beispiel
date:
  created: '2016-04-29'
  updated: '2020-03-06'
slug: livestreaming-von-vortraegen-ein-beispiel
authors:
- simon-dueckert
categories:
- Events und Vorträge
tags:
- DIYMultimedia
- Multimedia
wp:
  id: 1831
  link: https://cogneon.de/2016/04/29/livestreaming-von-vortraegen-ein-beispiel/
  featured_media: null
---

# Livestreaming von Vorträgen – Ein Beispiel

Heute war ich bei einer Akademie für genossenschaftliche Organisationen, um dort im Rahmen einer zweitägigen Veranstaltung einen der Vorträge live zu streamen. Im Folgenden ein Überblick und ein kurzer Erfahrungsbericht zum Projekt.

<!-- more -->

Die wichtigste zu klärende Frage im Vorfeld ist immer die der Konnektivität vor Ort. Für einen HD-Livestream benötigt man ca. 2,5 MBit Bandbreite im Upstream. Die Netzanbindung sollte über Kabel und nicht über WLAN erfolgen. Idealerweise ist man mit dem Videostream nicht im Gastnetz der Teilnehmer, sondern in einem separaten Netz mit garantierter Bandbreite. Mit Diensten wie dem [DSL Speedtest](http://dsl-speedtest.computerbild.de) kann man sich einen Überblick über die vorhandene Bandbreite verschaffen. In Fall in Montabaur sah die Messung schonmal sehr positiv aus:

![montabaur-bandbreite](/wp-content/uploads/2016/04/montabaur-bandbreite.jpg)

Da ich mit dem Zug am Vortag für Aufbau und Test angereist bin, habe ich mich [aus unserem Media Lab](http://wiki.cogneon.de/Cogneon_Media_Lab) für ein sehr leichtgewichtiges Setup entschieden:

- **Kamera:** [Canon XA25](http://wiki.cogneon.de/Canon_XA25) mit Speisemöglichkeit für externe Audioquellen über XLR. Zusätzlich habe ich die Zoom-Fernbedienung mitgenommen, um den Zoom am Stativgriff bequem einstellen zu können.
- **Stativ:** Manfrotto 290 xtra mit Carbon-Füßen (Gewicht) und einem Manfrotto Fluid-Videokopf 509 HD für flüssige Schwenks.
- **Streaming:** [Matrox Monarch HD](http://wiki.cogneon.de/Matrox_Monarch_HD), das über ein HDMI-Kabel (Mini-HDMI auf HDMI) das Audio- und Video-Signal bekommt und über einen LAN-Anschluss an den Videostreaming-Dienst (in unserem Fall YouTube Live) überträgt.
- **Audio-Backup:** für den Fall, dass man den Ton nicht aus der Mikrofonanlage der Akademie vor Ort bekommt, hatte ich eine [Sennheiser EW100 G3 Funkstrecke](http://wiki.cogneon.de/Sennheiser_ew100-ENG_G3) dabei (musste sie aber glücklicherweise nicht einsetzen).
- **Kabel:** 20 Meter Netzwerkkabel Cat6, 10m Verlängerungskabel Strom, Mehrfachsteckdose 4 x Strom und 2 x USB, 30 Meter Audiokabel XLR-XLR.
- **Erste-Hilfe-Koffer:** ein Zipper Bag mit Adaptern, Werkzeug, Klebeband, Batterien etc.

So sah der Aufbau nach ca. 30 Minuten Aufbauzeit dann aus:

![streaming-aufbau](/wp-content/uploads/2016/04/streaming-aufbau.jpg)

Als kleine Checkliste für die Veranstalter (und alle, die so etwas auch mal machen wollen) hier die wichtigsten Schritte des Aufbaus:

1. **Geigneten Ort für den Kameraaufbau finden.** Darauf achten, dass Redner in der Standard-Position nicht vor den Folien stehen (Kamera diagonal zum Redner). Kameraposition sollte so hoch sein, dass Publikum i.d.R. nicht im Bild ist (Stichwort: Recht am eigenen Bild). Außerdem sollte die Kamera außerhalb der Laufwege platziert sein, damit das Publikum nicht aus versehen dagegen stößt.
2. **Beamer- oder Fernsehfrequenz testen.** Videokameras (in Europa) nehmen meist mit 25 Hz Frequenz (=25 Bilder pro Sekunde) auf. Manche Beamer oder Fernseher projezieren mit anderen Bildwiederholraten, z.B. 60 Hz bei Beamer. Das führt dazu, dass das aufgenommene Beamerbild flackert. Einfachste Abhilfe in dem Fall ist, den Beamer auf 50 Hz umzustellen.
3. **Beleuchtung testen und einstellen.** In vielen Veranstaltungslokation gibt es keine separate Bühnenbeleuchtung, sondern nur Deckenlicht. Das führt dazu, dass projezierte Folien und Redner von der Helligkeit sehr unterschiedlich sind. Ist in der Kamera die automatische Belichtung aktiviert, führt das meist dazu, dass das helle Beamer-Bild dominiert und sich die Kamera danach ausrichtet. In der Folge erscheint der Sprecher dann zu dunkel („absaufen“). Optimiert mann die Helligkeit auf den Redner, ist das Beamer-Bild so hell, dass kein Kontrast mehr vorhanden und die Folien nicht lesbar sind („ausbrennen“). In meinem Fall habe ich versucht, die Belichtung über eine Spanne von 2,5 Stufen manuell nachzuführen.
4. **Tonsignal in die Kamera einspeisen.** In meinem Fall hat die Kamera einen Audioeingang über XLR-Kabel. Die Techniker vor Ort konnten mir aus der Mikrofonanlage ein langes Cinch-Kabel mit dem gemischten Tonsignal (Redner-Mikro, Moderatoren-Mikro, Publikums-Mikro) bereitstellen. Mit einem Cinch-XLR-Adapter ging das dann in die Kamera. Wichtig: alle Mikrofone sollten gleich laut sein. Am besten auch die Redner und in der Moderation darauf hinweisen, dass der Abstand Mikrofon-Mund idealerweise immer gleich sein sollte.
5. **Streaming-Device anschließen und testen.** Der Matrox Monarch HD verfügt nur über einen LAN Zugang. Die Techniker vor Ort konnten mir am Kamera-Ort ein LAN-Kabel zur Verfügung stellen. Für die Verbindung musste die MAC-Adresse des Matrox in der Netzwerkumgebung freigeschaltet weden (der Matrox kann nicht über Netze, die Login/Passwort benötigen, verbunden werden!). Das hat problemlos geklappt, ein Knopfdruck und der Livestream war im YouTube-Kanal der Organisation zu sehen.

Soweit mein Bericht. Falls jemand dieses kleine Rezept verwendet oder andere Ansätze hat, bin ich auf weitere Tipps und Erfahrungen per Kommentar gespannt.
