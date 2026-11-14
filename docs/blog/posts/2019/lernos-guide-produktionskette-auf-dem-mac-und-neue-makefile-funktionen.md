---
title: lernOS Guide Produktionskette auf dem Mac und neue Makefile-Funktionen
date:
  created: '2019-07-20'
  updated: '2019-07-20'
slug: lernos-guide-produktionskette-auf-dem-mac-und-neue-makefile-funktionen
authors:
- simon-dueckert
categories:
- lernOS
tags:
- lernOS
wp:
  id: 56964
  link: https://cogneon.de/2019/07/20/lernos-guide-produktionskette-auf-dem-mac-und-neue-makefile-funktionen/
  featured_media: null
---

# lernOS Guide Produktionskette auf dem Mac und neue Makefile-Funktionen

Ich habe mich gestern mal daran gemacht, die [Produktionskette für lernOS Guides](/2018/12/13/neuer-lernos-produktions-workflow/) auch auf dem Macbook zum laufen zu bringen. Im Prinzip war das genau so einfach wie auf Windows, außer dass man für [MacTeX](https://tug.org/mactex/) Pfadanpassungen machen muss und es [Balbolka](http://www.cross-plus-a.com/de/balabolka.htm) für die Audiobook-Produktion auf dem Mac nicht gibt.

<!-- more -->

https://twitter.com/SimonDueckert/status/1152202126480859137?s=20

Bei der Gelegenheit habe ich dann auch das [Makefile](https://de.wikipedia.org/wiki/Make) für Windows (*make.bat*) in eine Shell-Skript-Version für den Mac (*make.sh*) übertragen. Die Datei findet ihr -noch unkommentiert- [im GitHub Repo des lernOS für Organisationen Guide](https://github.com/cogneon/lernos-for-organizations/tree/master/de). Im Folgenden erkläre ich mal kurz, was die einzelnen Befehle dort tun.

Zunächst werden die Pfade richtig gesetzt, damit die nachfolgenden Befehle die MacTeX-Binaries für PDF-Erstellung und [Calibre](https://calibre-ebook.com/) für E-Book-Erstellung und -Konvertierung finden:

`PATH=$PATH:/Library/TeX/texbin:/usr/texbin:/usr/local/bin<br>
PATH=$PATH:/Applications/calibre.app/Contents/console.app/Contents/MacOS`

Dann wird die Variable *f* für den Dateinahmen gesetzt, damit man in den nachfolgenden Befehlen bei verschiedenen Guides nicht immer lange Textketten austauschen muss, in dem Fall:

`f=lernOS-for-Organizations-Guide-de`

Jetzt wird die Word-Version (*docx*) des Guides erzeugt. Hier gibt es noch einige offene Punkte: So wird die Metadaten-Datei (*metadata/metadaty.yaml*) zwar übergeben, in den Dokumenteigenschaften von Word erscheinen diese aber nicht. Außerdem sieht die Word-Datei noch sehr „roh“ aus. Mit dem Schalter *–reference-doc* kann man [pandoc](https://pandoc.org/) eine Vorlage übergeben, damit Deckblatt, Fonts etc. ähnlich dem PDF aussehen.

`pandoc $f.md metadata/metadata.yaml -o $f.docx`

Danach wird die HTML-Version erzeugt. Der Schalter *–toc* erzeugt ein klickbares Inhaltsverzeichnis (Table of Contents) Für die Zukunft will ich das noch ein bisschen erweitern, damit das HTML etwas schicker und besser zu navigieren wird (habe ich mit Leonid auf dem VW Group Collaboration Barcamp schonmal getestet).

`pandoc $f.md metadata/metadata.yaml -s --toc -o $f.html`

Dann wird die PDF-Version erzeugt. Dafür wird das [pandoc LaTeX Template von Wandmalfarbe](https://github.com/Wandmalfarbe/pandoc-latex-template) verwendet (*–template lernos*). Die Metadaten wie Titel, Deckblatt-Farbe etc. stehen in der Metadaten-Datei.

`pandoc $f.md metadata/metadata.yaml --template lernos -o $f.pdf`

Für die [E-Book](https://de.wikipedia.org/wiki/E-Book)-Erstellung sind mehrere Schritte notwendig. Zunächst wird aus der PDF-Version die erste Seite (Index 0) mit 300dpi Auflösung als Deckblatt für die E-Book-Version als JPG-Datei (*images/ebook-cover.jpg*) extrahiert. Das wird mit dem Befehl magick aus dem Paket [ImageMagick](https://imagemagick.org) gemacht:

`magick -density 300 $f.pdf[0] images/ebook-cover.jpg`

Dann wird die JPG-Datei nach den [Vorgaben für Amazon KDP eBooks](http://www.ebookcoversize.com/) auf die Höhe 2500px skaliert (erster mogrify-Befehl) und im Anschluss auf die korrekte Größe von 1563x255px zurechtgeschnitten (zweiter mogrify-Befehl):

`mogrify -size 2500x2500 -resize 2500x2500 images/ebook-cover.jpg<br>
mogrify -crop 1563x2500+102+0 images/ebook-cover.jpg`

Im Anschluss wird mit pandoc die [EPUB](https://de.wikipedia.org/wiki/EPUB)-Version des eBooks erzeugt und diese dann mit dem Befehl *ebook-convert* aus dem Paket Calibre in das Kindle-Format [MOBI](https://de.wikipedia.org/wiki/Mobipocket) konvertiert:

`pandoc $f.md metadata/metadata.yaml -s --epub-cover-image=images/ebook-cover.jpg -o $f.epub<br>
ebook-convert $f.epub $f.mobi`

Fertig ist der Workflow, viel Spaß beim Nachbauen! Über Tipps und Verbesserungsvorschläge über die Kommentare bin ich jederzeit offen :-)
