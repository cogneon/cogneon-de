---
title: Barrierefrei für Mensch und Maschine – Kleine Helferlein zur Konvertierung von Office-Dokumenten in maschinenlesbare Formate
date:
  created: '2026-02-08'
  updated: '2026-02-08'
slug: barrierefrei-fuer-mensch-und-maschine-kleine-helferlein-zur-konvertierung-von-office-dokumenten-in-maschinenlesbare-formate
authors:
- simon-dueckert
categories:
- Fachwissen
- Künstliche Intelligenz
tags:
- KünstlicheIntelligenz
- GenerativeKI
wp:
  id: 66598
  link: https://cogneon.de/2026/02/08/barrierefrei-fuer-mensch-und-maschine-kleine-helferlein-zur-konvertierung-von-office-dokumenten-in-maschinenlesbare-formate/
  featured_media: 66599
---

# Barrierefrei für Mensch und Maschine – Kleine Helferlein zur Konvertierung von Office-Dokumenten in maschinenlesbare Formate

Die **„Währung“** in der **dokumentiertes Wissen** in Organisationen transferiert wird sind **Office-Dateiformate** wie pptx, docx, xlsx und PDF. Leider sind das Formate, die **für Maschinenlesbarkeit denkbar ungünstig** sind. Oft sind sie zusätzlich so groß (z.B. durch in Powerpoint-Präsentationen eingefügte Grafiken), dass sie schnell die Limits von KI-Chatbots wie Copilot, ChatGPT und Claude sprengen.

<!-- more -->

Mit [Barrierefreiheit](https://de.wikipedia.org/wiki/Barrierefreiheit) für Menschen haben sich sicher viele von Euch in der Vergangenheit schon beschäftigt. Im **KI-Zeitalter** solltet Ihr Euch zusätzlich um die **Barrierefreit für Maschinen** kümmern. Das hat in der Regel damit zu tun, verschiedene Dateiformate in **strukturierten Text** (meist [Markdown](https://de.wikipedia.org/wiki/Markdown)) zu überführen. Ein weiterer Vorteil dabei ist, dass die Dateien meist deutlich kleiner werden, was Backup und Archiv freuen (z.B. 100MB Powerpoint wird zu 100kB Text-Datei).

Hier sind einige **Werkzeuge und Helferlein**, die ich in der Praxis sehr häufig verwende:

- **PDF:** das P in PDF steht für „printable“ und damit ist auch der Haupt-Anwendungsfall von PDFs benannt, das **Gegenteil von Maschinenlesbarkeit**. Mit Werkzeugen wie [Llamaindex](https://www.llamaindex.ai/) und [Docling](https://www.docling.ai/) entstehen daraus strukturierte Text-Dateien. Wer diese Tools nicht im Zugriff hat, kann folgenden Trick verwenden: einfach das PDF in **Microsoft Word** öffnen, dabei wird es automatisch in ein Text-Dokument konvertiert.
- **DOCX & ODT:** Word-Dateien und deren offenes Pendant [Open Document Format](https://de.wikipedia.org/wiki/OpenDocument) lassen sich in der neuen Version 26.2 von [LibreOffice](https://de.libreoffice.org/) öffnen und direkt in Markdown abspeichern. Libreoffice Writer ist mittlerweile auch ein [WYSIWYG](https://de.wikipedia.org/wiki/WYSIWYG)-Markdown-Editor.
- **Audio & Video:** der Prozess, aus Audio- und Video-Dateien (z.B. wav, mp3, mp4) Text zu erstellen, nennt sich [Transkription](https://de.wikipedia.org/wiki/Transkription_(Sozialwissenschaften)). Bei Aufzeichnungen von Videokonferenzen z.B. mit Microsoft Teams werden neben den Mediendateien direkt auch Transkripte im Word- und [VTT](https://en.wikipedia.org/wiki/WebVTT)-Format erzeugt. Alternativ können Werkzeuge wie [MacWhisper](https://goodsnooze.gumroad.com/l/macwhisper) Mediendateien sehr schnell transkribieren und in einer Vielzahl von Formaten speichern.
- **Pandoc:** [Pandoc](https://pandoc.org/) ist mein **„Schweizer Taschenmesser“ für die Text-Konvertierung**. Wenn ich Transkripte mit KI zusammengefasst habe (z.B. Vorträge von Lern-Events oder Townhalls), liegen diese i.d.R. im Markdown-Format vor. Sollen die Inhalte dann in **Sharepoint-Pages oder Wiki-Seiten in Confluence** bereitgestellt werden, sind die notwendigen Formate in Bruchteilen von Sekunden erzeugt. Tipp für alle, die Pandoc auf Ihrem Firmenrechner nicht installieren dürfen: mit der neuen Version 3.9 geht das [als Webanwendung auch direkt im Browser](https://pandoc.org/app/), ohne dass die Inhalte den eigenen Rechner verlassen.

Wir haben im letzten Jahr eine **Vielzahl von Projekten** gemacht, bei der Sammlungen von **Präsentationen oder Archive von Aufzeichnungen** z.B. von internen **Konferenzen, Barcamps oder Webinaren** mit Hilfe dieser Tools **KI-ready** gemacht wurden. Falls Ihr an einem derartigen Projekt Interesse habt, meldet Euch gerne.

Was sind Eure Tools, Helferlein und Tricks, um Eure Inhalte für Maschinen und KI-Chatbots barrierefrei zu machen?
