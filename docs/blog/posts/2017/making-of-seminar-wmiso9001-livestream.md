---
title: Making of Seminar WM&ISO9001 Livestream
date:
  created: '2017-05-12'
  updated: '2020-03-28'
slug: making-of-seminar-wmiso9001-livestream
authors:
- simon-dueckert
categories:
- Podcast und Multimedia
tags:
- DIYMultimedia
- Podcasting
- GfWM
- Standards
- Multimedia
- Qualitätsmanagement
- Sennheiser
wp:
  id: 10278
  link: https://cogneon.de/2017/05/12/making-of-seminar-wmiso9001-livestream/
  featured_media: null
---

# Making of Seminar WM&ISO9001 Livestream

Heute habe ich im Rahmen der GfWM Mitgliederversammlung ein [Seminar zum Thema Wissensmanagement und ISO 9001:2015 in der Praxis](http://www.gfwm.de/mitschnitt-zum-seminar-wissensmanagement-und-iso-90012015-in-der-praxis/) gehalten. Das Seminar habe ich live ins Internet übertragen, um die Teilnahme für einen größeren Personenkreis zu ermöglichen. Vor Ort haben 8 Personen teilgenommen, im Livestream 24. Wenige Stunden nach Seminarende hatte das Video bereits über 100 Abrufe. In diesem Blog will ich kurz das technische Setup des Livestreams beschreiben.

<!-- more -->

[YouTube: GfWM Seminar Mitglieder für Mitglieder: Wissensmanagement und ISO 9001:2015 in der Praxis](https://www.youtube.com/watch?v=XyqLtEoqXBU){ .embed }

Als Streaming-Plattform habe ich **YouTube-Live** (Konto der GfWM) verwendet. Für die Übertragung eines Videostreams zu YouTube wird das [Real Time Messaging Protokoll](https://de.m.wikipedia.org/wiki/Real_Time_Messaging_Protocol) (RTMP) verwendet. Gestreamt habe ich in 720p-Auflösung (1280×720, kleines HD).

Die Folien mit dem Vortrag habe ich in der Akademie von meinem **Notebook** (Lenovo Carbon X1, Windows 10) präsentiert. An diesem Notebook war ein **USB-Headset** ([Sennheiser PC 36](https://amzn.to/342t2G5)) und eine **USB-Webcam** ([Logitech ConferenceCam Connect](https://amzn.to/2UGrbCv)) angeschlossen.

Um aus dem Bildschirm und dem Webcam-Video einen Livestream zu machen benötigt man eine sog. **Encoder-Software**. Hierfür habe ich die Open-Source-Software [OBS Studio](https://obsproject.com) verwendet. In OBS kann man verschiedene Audio-/Videoquellen kombinieren. Im Fall des Seminars war das der Notebook-Bildschirm und die Webcam im [Side-by-Side-Modus](https://support.google.com/youtube/answer/183851?hl=de) (im Gegensatz zu Picture-in-Picture nebeneinander, damit die Folien nicht überdeckt werden). In OBS trägt man einfach den **Streaming-Key** aus seinem YouTube-Kanal ein, klickt „Streaming starten“ und der Stream ist live.

YouTube stellt nach Beendigung des Livestreams das aufgezeichnete Video direkt im Kanal zur Verfügung. Mit dem [YouTube-Video-Editor](https://support.google.com/youtube/answer/183851?hl=de) habe ich Anfang und Ende des Videos getrimmt und das Video dann gespeichert.

Falls Ihr Fragen zum Workflow, der Software oder der Hardware habt, gerne unten in die Kommentare.
