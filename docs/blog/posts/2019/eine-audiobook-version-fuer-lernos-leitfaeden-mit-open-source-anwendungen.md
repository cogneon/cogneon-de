---
title: Eine Audiobook-Version für lernOS Leitfäden mit Open Source Anwendungen
date:
  created: '2019-07-07'
  updated: '2020-03-06'
slug: eine-audiobook-version-fuer-lernos-leitfaeden-mit-open-source-anwendungen
authors:
- simon-dueckert
categories:
- lernOS
tags:
- lernOS
- Podcasting
wp:
  id: 56913
  link: https://cogneon.de/2019/07/07/eine-audiobook-version-fuer-lernos-leitfaeden-mit-open-source-anwendungen/
  featured_media: null
---

# Eine Audiobook-Version für lernOS Leitfäden mit Open Source Anwendungen

Audiobooks sind mit Plattformen wie Amazon Unlimited oder Audible ein großer Trend geworden. Dort kann man sich gelesene Versionen von Büchern herunterladen und unterwegs anhören. Ende März hat Asja auf Twitter die Frage aufgebracht, ob man so ein Audiobook nicht auch für lernOS Leitfäden anbieten könnte:

<!-- more -->

https://twitter.com/asja_heinrich/status/1111462432478822400?s=21

Da die Inhalte gemäß einer agilen Entwicklungsmethode alle drei Monate in einer neuen Version erscheinen, ist das Einlesen der Texte von menschlichen Sprechern nicht realistisch – außer wir finden einen Sponsor, der uns regelmäßig Rufus Beck finanziert :-)

Also habe ich mich mal auf die Suche nach freien [Sprachsynthese](https://de.wikipedia.org/wiki/Sprachsynthese)-Anwendungen begeben. Gedanklich waren die Anforderungen an die Anwendung ungefähr so (es gab kein Lastenheft):

- **Freie Software**, damit alle damit experimentieren können
- Verfügbarkeit gut klingender **Stimmen**
- **Kommandozeilen-Tool**, damit wir es in unseren automatisierten Produktionsprozess einbinden können
- **Export-Funktion** als MP3, idealerweise weiterer Audio-Formate
- **Kapitelmarken**-Funktion, damit die Kapitel im Leitfaden auch im Audiobook einzeln ansteuerbar sind

Getestet haben wir z.B. auch, Siri auf dem iPhone den Leitfaden vorlesen zu lassen und dass dann über ein Audio-Interface aufzunehmen. Schließlich haben wir uns dann für die Freeware-Anwendung [Balabolka](http://www.cross-plus-a.com/de/balabolka.htm) entschieden.

Balabolka setzt auf dem Windows [Speech Application Programming Interface](https://de.wikipedia.org/wiki/Speech_Application_Programming_Interface) (SAPI) auf. Dadurch kann auf eine Vielzahl kostenloser und kostenpflichtiger Stimmen zurückgegriffen werden. Für SAPI 5 sind noch nicht so viele Stimmen verfügbar, wie für SAPI 4, das wird sich aber in Zukunft noch ändern.

Balabolka kann Text aus einer großen Auswahl von Quellen einlesen, darunter die Zwischenablage und Dateiformate wie DOC, EPUB, HTML, MOBI, HTML und PDF. Da wir die lernOS Leitfäden auch in den eBook-Formate EPUB und MOBI erstellen, kam uns diese Flexibilität sehr entgegen. Die synthetisierten Texte können dann in den Audio-Formaten WAV, MP3, OGG und WMA abgespeichert werden. Perfekt.

Ich habe jetzt mal die deutsche und englische Version des [lernOS for You Leitfaden](/lernos) als MP3 erstellt (Laufzeit ca. 1h, Größe ca. 50 MByte). Um für die experimentellen Audiobooks eine kompakte Seite mit Player und Feedback-Option zu erhalten, habe ich [beide Dateien auf archive.org](https://archive.org/details/lernos-for-you-v1.3-audiobook) hochgeladen:

[![](/wp-content/uploads/2019/07/img_0003.jpg)](https://archive.org/details/lernos-for-you-v1.3-audiobook)

Es ist natürlich klar, dass die Sprachsynthese nicht an die Lösung mit Rufus Beck heranreicht. Aber hört bitte trotzdem mal rein und schreibt auf der Seite unten eine sog. Rezension mit eurem Feedback. Meine Frage ist, ob wir dieses Art Audiobooks bei den Leitfäden mal mit anbieten sollen, oder ob das noch zu weit von brauchbar entfernt ist.
