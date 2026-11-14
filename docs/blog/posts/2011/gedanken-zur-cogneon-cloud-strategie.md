---
title: Gedanken zur Cogneon „Cloud Strategie“
date:
  created: '2011-11-29'
  updated: '2020-03-06'
slug: gedanken-zur-cogneon-cloud-strategie
authors:
- simon-dueckert
categories:
- Akademie
tags:
- Barcamp
- Wiki
- Newsletter
- Strategie
wp:
  id: 68
  link: https://cogneon.de/2011/11/29/gedanken-zur-cogneon-cloud-strategie/
  featured_media: null
---

# Gedanken zur Cogneon „Cloud Strategie“

Das Thema Cloud Computing ist in aller Munde und natürlich auf für unsere Geschäftsentwicklung wichtig. Denkt man daran, dass Cogneon in Zukunft über noch mehr als die bisherigen Standorte verteilt sein wird, dann umso mehr. Denn im Gegensatz zu IT-Infrastruktur, die zentral angeboten und selber betrieben wird, skalieren Cloud-Angebote deutlich besser und sind zudem konkurrenzlos günstig. Einige der Dienste nutzen wir schon sehr lange, einige haben wir in unserer Strategie neu aufgenommen:

<!-- more -->

1. **E-Mail:** seit unserer Gründung in 2001 nutzen wir den Cloud-Dienst Outlook.Hosting bei 1&1, der uns einen professionellen Exchange-Server mit Outlook-Anbindung und Outlook Web Access (OWA) bietet. E-Mails mit Geheimhaltungsstufe "vertrauliche" werden mit PGP (GPG4Win) verschlüsselt.
2. **Dokumente (Geheimhaltungsstufe "öffentlich" oder "intern"):** diese Dokumente können bei Bedarf in Dropbox-Accounts abgelegt werden. Ist zusätzliche Sicherheit notwendig, werden die Dokumente mit AxCrypt bzw. ganze Ordner mit 7-Zip verschlüsselt.
3. **Dokumente (Geheimhaltungsstufe "intern" und "vertrauliche"):** bisher haben wir einen eigenen auf Windows 2000 Server basierenden Datei-Server inkl. eigenem Backup-Management und unterbrechungsfreier Stromversorgung betrieben. Das stellen wir zum Anfang des nächsten Jahres um auf den Dienst [Cloudsafe](http://www.cloudsafe.com) um, der ein ähnliches Angebot wie Dropbox bietet, aber seinen Firmensitz und seine Server in Deutschland hat und damit dem deutschen Recht unterliegt. Genau wie bei Drobpox auch kann man auf Cloudsafe über das Windows Dateisystem, ein Web-Interface oder Apps für iPhone, iPad und Android zugreifen. Wir hatten auch [Teamdrive](http://www.teamdrive.com) in der engeren Auswahl, da gibt es aber (noch?) keine Clients für mobile Endgeräte.
4. **Multimedia-Dokumente:** der Trend in der Wissensvermittlung geht klar in Richtung Multimedia (neben Text auch Bild, Bewegtbild/Video und Audio). Derartige Inhalte wollen wir in Zukunft vermehrt anbieten, die Inhalte bei uns aber nicht verwalten, da die Übertragung eine große Bandbreite erfordert. Hierfür werden wir Kanäle auf Slideshare (Präsentationen, Dokumente, mit/ohne Audiospur), Flickr (Bilder) und YouTube (Video) einrichten bzw. ausbauen.
5. **Soziales Netzwerk:** hier setzen wir seit über zwei Jahren und mit großer Zufriedenheit Yammer ein. Bisher nutzen wir "nur" die Profile und die Updates, wollen aber in Zukunft vermehrt auch mit Gruppen arbeiten, um Externe und Projektpartner in die Kommunikation einbinden zu können.
6. **Instant Messaging und Desktop Sharing:** hierfür verwenden wir intern [Skype](http://www.skype.com), das Desktop-Sharing bei zwei Benutzern zulässt. Für Desktop-Sharing mit mehr Benutzern oder mit Kunden (die dürfen i.d.R. nicht skypen) werden wir in Zukunft [GoToMeeting](http://www.gotomeeting.de) verwenden (bisher [Mikogo](http://www.mikogo.com)).
7. **Weblogs:** unsere Weblogs haben wir in 2003 gestartet und betreiben diese im Rahmen unserer Webseite cogneon.de (Basis: Drupal) selber. Im kommenden Jahr werden unsere Blogs auf Basis von WordPress in einer eigenen Subdomain blogs.cogneon.de schreiben. Zum einen, um unsere eigentliche Webseite schlanker und übersichtlicher zu machen, auf der anderen Seite, um mit WordPress mehr Praxiserfahrungen zu sammeln, da sich WordPress gerade bei Corporate Blogs (z.B. Daimler, adidas) als Standard durchgesetzt hat.
8. **Newsletter:** unseren Newsletter betreiben wir auch auf cogneon.de (Drupal, Modul: simplenews). Bisher war die Devise mit dem Vorbild des Newsletters von David eher schlicht&einfach, d.h. keine Bilder, Versand im Plain-Text-Format. Wir glauben, dass es jetzt an der Zeit ist, den Newsletter optisch ansprechender zu gestalten, für mobile Endgeräte zu optimieren und besser mit den sozialen Medien zu vernetzen (bisher ist der NL ein rechter "Black-Box-Prozess"). Deswegen werden wir den Newsletter beginnend mit der Ausgabe 02/2012 auf den Dienst [Mailchimp](http://mailchimp.com) umstellen.
9. **Webseite cogneon.de:** bisher war es für uns wichtig, unsere Webseite selber gestalten und viel experimentieren zu können, um diese Erfahrungen auch auf Social-Intranet-Projekte bei Kunden zu übertragen. Durch diese Lernkurve sind wir durch. Deswegen haben wir als ersten Schritt den Prozess der Kommentarverwaltung in die Cloud verschoben und nutzen dafür nicht mehr das Drupal-interne Kommentarsystem, sondern den Dienst [Disqus](http://disqus.com). Wenn Weblogs und Newsletter auch in der Cloud sind, ist die wichtigste Voraussetzung geschaffen, die Webseite an einen externen Drupal-Hoster zu übergeben. Hierfür haben wir aber noch keinen Zeitplan.
10. **Veranstaltungen:** auch die Veranstaltungen waren bisher Inhalte auf cogneon.de (Inhaltstyp Veranstaltung mit dem Modul CCK auf Drupal). Schwierigkeiten bzw. großen Aufwand haben uns in Vergangenheit Veranstaltungen mit Anmeldeprozess und kostenpflichtige Veranstaltungen gemacht. Hier mussten wir meist Teilnahmelisten mit Excel pflegen und Rechnungen mit der Hand versenden. Bezahlung über Kanäle wie Kreditkarte, Paypal, Bankeinzug und Micropayment waren nicht möglich. Wir hatten seit einiger Zeit die Idee hierfür [Amiando](http://www.amiando.com) einzusetzen, wussten aber nicht, ob Firmen das als Dienst akzeptieren würden. Deswegen haben wir die KnowTech 2011 abgewartet, die ihren ganze Anmeldungsprozess über Amiando abgewickelt hat, was zu keinen Problemen führte. Wir haben mit der Orange Night im Rahmen der KnowTech einen ersten Testballon auf Amiando gestartet und mit dem Dezember Jam eine kostenpflichtige Veranstaltung, beides kein Problem. Die Übernahme von Amiando durch Xing bringt uns noch näher an unsere Zielgruppe, wir werden im nächsten Jahr prüfen, ob wir die Veranstaltungen auf der Startseite von cogneon.de rechts oben durch einen iCal-Feed von Amiando ersetzen können.
11. **Wiki:** das Cogneon Wiki basiert auf [Mediawiki](http://www.mediawiki.org) und wird auf dem gleichen Server verwaltet, wie die cogneon.de (ein Hosted Rootserver bei vServer). Das Wiki ist im Kontext unserer neue gegründeten Akademie ein sehr wichtiger Baustein, da dort offen zugängliche Lernmaterialien befinden sollen. Da es unseres Wissens nach aber noch keinen geeigneten Mediawiki-Cloud-Dienst gibt (wir haben Wikia probiert, das war uns aber zu restriktiv), werden wir das Wiki auf absehbare Zeit selber betreiben. Das Kommentarsystem im Wiki haben wir bereits deaktiviert und nutzen an dieser Stelle auch Disqus.
12. **Community:** unsere Community ist bisher eher eine "Offline-Community" gewesen, mit den beiden Knowledge Jams pro Jahr als Treffpunkt. Commnunity-Mitglieder konnten sich zwar auf cogneon.de Profile anlegen und im Wiki schreiben, in diese Richtung ist aber eher wenig passiert. Deswegen haben wir uns entschieden, die Community auf mixxt umzuziehen, was wir nicht bereuen, da dort (Orange People, nur für Mitglieder) ein Vielfaches mehr an Interaktion im Vergleich zu vorher stattfindet.
13. **Webinare und Distant Education:** dafür hatten wir in der Vergangenheit gar nichts, in 2012 werden wir hierfür [Edudip](http://www.edudip.com) prototypisch verwenden.
14. **Live-Streaming:** in Vergangenheit haben wir bereits probiert, ausgewählte Veranstaltungen live zu streamen (z.B. Vortäge auf dem [GfWM KnowledgeCamp](http://www.gfwm.de/interaktiv/knowledge-camp/)). Diese Fähigkeit wollen wir in Zukunft ausbauen (wir haben dafür die technischen Voraussetzungen in unserer Akademie geschaffen) und mehr Veranstaltungen als Livestream über den Dienst [Ustream](http://www.ustream.tv) anbieten.

Im Bereich Auftragsverwaltung, Kundenbeziehungsmanagement, Zeiterfassung und Rechnungsstellung sind wir aktuell noch auf der Suche. Wir wollen eigentlich ein System, bei dem alle Funktionen unter einem Dach sind. Aktuell haben wir z.B. [Salesforce](http://www.salesforce.com), [ProjectFacts](http://www.projectfacts.de) und [Basecamp](http://37signals.com/) (inkl. Highrise) in der engeren Auswahl, der Prozess ist aber noch offen. Wer hierzu Erfahrungen und Ideen hat, ist herzlich eingeladen, diese beizusteuern.

Eine große Inspiration für die Weiterentwicklung unserer digitalen Wissensinfrastruktur ist für uns nach wie vor das Buch "Small Pieces Loosly Joined" von David Weinberger. Wir wollen nicht mehr das große, monolithische System (die eierlegende Wollmilchsau) selber gestalten, sondern fügen Komponenten, die sich auf einzelne Funktionen spezialisieren, intelligent zusamen.
