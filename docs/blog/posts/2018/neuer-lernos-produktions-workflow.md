---
title: Neuer lernOS Produktions-Workflow
date:
  created: '2018-12-13'
  updated: '2020-08-12'
slug: neuer-lernos-produktions-workflow
authors:
- simon-dueckert
categories:
- lernOS
tags:
- lernOS
wp:
  id: 54419
  link: https://cogneon.de/2018/12/13/neuer-lernos-produktions-workflow/
  featured_media: 54660
---

# Neuer lernOS Produktions-Workflow

Für die Erstellung von [lernOS](http://lernos.org) Leitfäden haben wir uns einen Produktions-Workflow gebaut, der aus einer Single-Source automatisch verschiedene Zielformate erzeugen kann. Die Quellen der Leitfäden sind durchgängig in [Markdown](https://de.m.wikipedia.org/wiki/Markdown) geschrieben. Für den ersten lernOS Guide in der Version 1.0 haben wir daraus die Formate PDF, DOCX (MS Word), HTML und EPUB (eBook) erzeugt. Für die Version 1.1 haben wir diesen Workflow etwas erweitert. In diesem Blog beschreibe ich alle notwendigen „Zutaten“.

<!-- more -->

![](/wp-content/uploads/2018/12/img_1286-2.jpg)

Der alte Workflow hat im Kern zwei Werkzeuge verwendet:

1. [Pandoc](http://pandoc.org): eine Anwendung zur Konvertierung von Dokumentformaten. Pandoc unterstützt eine Vielzahl von Dateiformaten, darunter z.B. Markdown, textile, HTML, LaTeX, Mediawiki, Creole, MS Word, ODT (Libre Office), DocBook uvm.
2. [MikTeX](https://miktex.org): damit pandoc auch PDF erzeugen kann, ist MikTeX notwendig. MikTeX ist eine [LaTeX](https://de.m.wikipedia.org/wiki/LaTeX)-Version für Windows.

Im alten Workflow wurde eine PDF-Version, eine Word-Version, eine HTML-Version (u.a. zur Erzeugung der OneNote-Vorlage) und eine [EPUB](https://de.m.wikipedia.org/wiki/EPUB)-Version erstellt. Die PDF-Version hatte das lernOS-typische orange Cover, die anderen Versionen waren ohne Cover, da die Cover-Erzeugung eine Funktion der LaTex-Vorlage ist. Außerdem konnte die EPUB-Version nicht direkt an den verbreiteten Amazon Kindle (Device oder App) übertragen werden, da dieser [MOBI](https://de.m.wikipedia.org/wiki/Mobipocket) und nicht EPUB als Format verwendet. Daher wurde der Workflow für die Version 1.1 des lernOS Guide wie folgt erweitert:

1. [ImageMagick](https://www.imagemagick.org/script/index.php): freie Anwendung zur Erstellung und Bearbeitung von Raster- und Vektor-Grafiken. Damit ist die Konvertierung des Covers (erste Seite des PDF) in eine PNG-Datei möglich.
2. [Calibre](https://calibre-ebook.com): freie Anwendung zur Verwaltung und Konvertierung von eBooks. Damit kann die EPUB-Version um Metadaten und das Cover erweitert und im Anschluss auch in das MOBI-Format konvertiert werden.

Auf diese Weise entsteht im neuen Workflow eine Datei mit Endung .mobi, die an die E-Mail-Adresse des eigenen Kindle geschickt werden kann. Dort kann der Leitfaden dann kommentiert, durchsucht und mit Lesezeichen versehen werden. Alle Markierungen synchronisieren sich automatisch über alle Kindle-Geräte.
