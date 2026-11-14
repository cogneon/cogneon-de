---
title: Video vs. Audio – warum es sich manchmal lohnen kann, Videos auch als Audio-Dateien bereitzustellen
date:
  created: '2019-09-04'
  updated: '2023-10-23'
slug: video-vs-audio-warum-es-sich-manchmal-lohnen-kann-videos-auch-als-audio-dateien-bereitzustellen
authors:
- simon-dueckert
categories:
- Podcast und Multimedia
tags:
- Podcasting
- NewWork
- Podcast
- Multimedia
wp:
  id: 57001
  link: https://cogneon.de/2019/09/04/video-vs-audio-warum-es-sich-manchmal-lohnen-kann-videos-auch-als-audio-dateien-bereitzustellen/
  featured_media: null
---

# Video vs. Audio – warum es sich manchmal lohnen kann, Videos auch als Audio-Dateien bereitzustellen

Die Diskussion **Video vs. Audio** kommt im Bereich von Kommunikation und Weiterbildung immer mal wieder hoch. Meist wird Video favorisiert, aus meiner Sicht oft, weil es durch YouTube und E-Learning bekannter ist und eingeübter ist. Als großer Fan von Podcasts versuche ich dann immer, die Beteiligten über Audio als Option mal nachdenken zu lassen.

<!-- more -->

Vor einige Tagen gab es so einen Fall mit dem [New Work Chat von Gabriel](https://gabrielrath.com/newworkchat/). Er hat mittlerweile das siebte Gespräch zu Themen rund um New Work mit einer Videokonferenz-Software aufgezeichnet und dann [auf YouTube bereitgestellt](https://www.youtube.com/playlist?list=PLgaxOoFQ9OgER14UQgx89N2qDBCq1elGp) (dieses Mal mit Katha zu WOL):

[YouTube: New Work Chat #7 mit Katharina Krentz, der "Working Out Loud"-Botschafterin](https://youtu.be/AC0D21xEYlw){ .embed }

Ich wollte mir den Mitschnitt auf dem Heimweg anhören und da hat YouTube in meinen Augen drei Nachteile:

1. **Bandbreite:** es gibt keine Möglichkeit, eine Nur-Audio-Version anzuhören, was unnötig viel Bandbreite braucht (in Zeiten von Flatrates kein Problem).
2. **Akku:** das Telefon muss die ganze Zeit an sein, da die YouTube-App nur spielt, wenn sie im Vordergrund ist (insbesondere Nachts störend).
3. **Offline-Modus:** wenn man bei YouTube kein Geld einwirft, gibt es ohne Zusatzwerkzeuge wie [youtube-dl](https://github.com/yt-dlp/yt-dlp) keine Möglichkeit, das Video herunterzuladen. Man ist beim Hören/Sehen also auf Netz angewiesen (schwierig in DE).

Zusätzlich ist mir aufgefallen, dass die Abrufzahlen der Videos trotz der sehr guten Gesprächspartner sehr niedrig ist. Ich habe Garbiel dann auf Twitter gefragt, ob er seine Medien nicht auch per Podcast bereitstellen möchte:

https://twitter.com/simondueckert/status/1168782884943073286?s=21

Seine Antwort war wie folgt:

https://twitter.com/gabrealness/status/1169107977011376128?s=21

Der Aspekt der Audio-Qualität ist bei Podcasts natürlich wichtig. Die Videokonferenz-Tools sind hier meist nicht optimal, da sie eher auf geringe Latenz und Ausfallsicherheit und nicht Audioqualität optimiert sind. Außerdem sieht es im Video etwas komisch aus, wenn man mit einem guten Headset wie dem [Beyerdynamic DT297](https://amzn.to/2PHw1QE) (Affiliate-Link) vor dem Rechner sitzt. Meist haben die Gesprächspartner dann einfach die Smartphone-Kopfhörer im Ohr, deren Audioqualität nicht sonderlich gut ist.

Aber auf die Audioqualität wollte ich mit meiner Antwort eigentlich gar nicht raus. Mir ging es eher um das Nutzungsszenario von Podcasts: den New Work Chat in einer Podcast App abonnieren und neue Folgen automatisch auf das Smartphone heruntergeladen zu bekommen. Im Idealfall noch mit [Kapitelmarken](https://www.audiobeitraege.de/kapitelmarken-mit-audacity-erstellen/), damit man im Podcast thematisch springen kann. Anders als von Gabriel angezweifelt finde ich die Audioqualität seiner Aufnahmen dafür auf jeden Fall ausreichend.

Ein Podcast, der das beispielsweise so macht, ist der [Aufwachen Podcast](https://aufwachen-podcast.de) rund um Stefan Schulz. Zwei bis drei Personen schauen sich gemeinsam Ausschnitte aus Nachrichtensendungen an und kommentieren diese. Die Aufzeichnungen [landen auf YouTube](https://www.youtube.com/user/Nfes2005) und werden gleichzeitig als Audio-Podcast ausgespielt. Diese Sendung habe ich zuerst als Podcast entdeckt und mir ist erst viel später aufgefallen, dass es davon auch eine Video-Version gibt. Das hat mir klar gemacht, wie wenig einem der Video-Kanal in vielen Fällen fehlt (Tipp für ein Experiment: schaut mal die Tagesschau mit geschlossenen Augen und bewertet, ob ihr dadurch weniger Informationen erhaltet).

An Gabriels Stelle kann man den Audio-Podcast als Zweitverwertung der Aufzeichnung recht einfach ausprobieren:

1. Im Blog eine Podcast-Erweiterung wie beispielsweise [Podlove Publisher für WordPress](https://podlove.org/podlove-podcast-publisher/) installieren
2. Aus der Video-Datei z.B. Mit [ffmpeg](https://ffmpeg.org) eine Audio-Spur extrahieren (FLAC)

Die Audio-Spur durch [Auphonic](https://auphonic.com) laufen lassen, um die Audioqualität zu verbessern, Kompression hinzuzufügen und einen konstanten Pegel zu erzeugen (MP3)

Die MP3-Datei über den Blog mit Podcast-Erweiterung bereitstellen

Den Podcast-Feed bei [Apple-Podcasts](https://www.apple.com/de/itunes/podcasts/) (dort holen sich fast alle Podcast Verzeichnisse die Feeds), [fyyd](https://fyyd.de) und [bei Spotifiy](https://artists.spotify.com/faq/popular#how-do-i-get-a-podcast-on-spotify) eintragen, um langfristig die Reichweite zu erhöhen

Gabriel, ich würde mich über den New Work Chat als Podcast sehr freuen und helfe gerne, wenn es irgenwo hakt :-)
