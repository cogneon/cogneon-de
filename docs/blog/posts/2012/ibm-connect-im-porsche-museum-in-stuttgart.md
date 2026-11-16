---
title: IBM Connect im Porsche Museum in Stuttgart
date:
  created: '2012-09-19'
  updated: '2012-09-19'
slug: ibm-connect-im-porsche-museum-in-stuttgart
authors:
- simon-dueckert
categories:
- Events und Vorträge
tags:
- Enterprise20
- Intranet
wp:
  id: 337
  link: https://cogneon.de/2012/09/19/ibm-connect-im-porsche-museum-in-stuttgart/
  featured_media: null
---

# IBM Connect im Porsche Museum in Stuttgart

IBM lud heute (19.09.2012) zur IBM Connect 2012 in das Porsche Museum in Stuttgart. In Ihreer Begrüßung verglich Maria Gomez von IBM Enterprise-2.0-Werkzeuge (ich mag die Begriffe "Social Business" und "Social Tools" nicht) mit dem Auto und dem Telefon in ihrer Funktion als Mensch mobil zu sein und sich mit anderen auszutauschen. Das war der Grund, das Porsche Museum als Veranstaltungsort auszuwählen. Im folgenden einige Notizen zu den Vorträgen (Bilder folgen in den nächsten Tagen noch).

<!-- more -->

## Social Business

- Referent: Alistair Rennie (General Manager Social Business, IBM)
- Social Networks + Mobility + Social Content & Analytics.
- Fallbeispiel cemex, die "networks of expertise" genutzt haben, um ein globales Produkt in einem Drittel der üblichen Zeit entwickelt haben.
- Fallbeispiel TD Bank, die Mitarbeiter in offenen und kollaborativen Foren interagieren lässt, um Kundendienst und Entwicklung zu verbessern.
- Fallbeispiel Reliance, haben ihre Betriebskosten um 30% gesenkt und sind dabei gleichzeitig gewachsen.
- Weitere Fallbeispiele: Bayer, Bosch, GAD, Amadori, Primerica (Versicherung)
- Human capital is the leading cited sourc of economic value (human capital 71%%, product/service innovation 66%, customer relationships 52%) but CEOs face significant workforce challenges (15% employee turnover per year in US, total costs of replacement can reach 200% of the annual salary).
- Sources: VCC Case study, Bersin Report: The Science to Fit, 2012 IBM CEO Study, Cemex case study.
- Hauptanwendungsfelder für Enterprise 2.0 sind Produktentwickung, Kundendienst und Vertrieb.
- ROI sollte bei den Kernprozessen ansetzen und eine Idee entwickeln, wie durch Enterprise 2.0 die KPIs dieser Prozesse verbessert werden können (z.B. kürzere Durchlaufzeiten, mehr Output, geringer Kosten)
- Änderungen in der aktuellen IBM Connections Version: connections mail ("increasingly we see people not want to leave it", integrated activity Stream (business systems like SAP etc.), embedded experiences, community pages.
- Social analytics can replace/extend employee surveys.
- Notes Social Edition: Integration von sozialen Funktionen wie Aktivitätenstrom in den E-Mail-Client (auf der Zugfahrt werde ich darüber nachdenken, was meine Wunschvorstellung eines modernen "Personal Dashboard" ist).
- "Mobility is hard to overestimate".
- Lessions Learned
    - Kernziele von Enterprise 2.0 sind "create smarter workforce" und "create exceptional customer experience".
    - Being purposful by defining business outcome and sponsorship is critical
    - Need leadership around strategy, culture by being authentic&iterative
    - Early engagement is the key to learn lessons for a successful long journey

## Implementierung von IBM Connections bei der Robert Bosch GmbH

- Referent: Dr. Erik Wüstner (Robert Bosch GmbH)
- Projekt-Mission: "Das zentrale Projekt wird die unternehemsweiten Voraussetzungen schaffen, um die Social Business Adoption in allen operativen Einheiten zu unterstützen und voranzutreiben (intern und extern)".
- Zu Enterprise 2.0 (intern) gehören Technologie (EINE Standardplattform, Anwendungsfallspezifische Ergänzungen), Führung (Förderung von Transparenz/Feedback/Diskussionen und organisationsübergreifender Zusammenarbeit), Richtlinien (Bereitstellung von Empfehlungen/Guidelines, Klärung von rechtlichen Aspekten),  und Organisation (Umsetzung der E2.0-Organisation, Sicherstellung von E2.0-Training und -Coaching).
- Für alle Geschäftsbereiche wurden Enterprise-2.0-Koordinatoren definiert.
- Prozess der Enterprise-2.0-Toolauswahl
    - Vier Marktführende E2.0-Plattformen plus Open-Source-Lösung als Kandidaten
    - Evaluation mittels Testinstallation (on-premise)
    - Produkt-Kriterien (Kosten, Funktionsumfang, IT-Anforderungen, Usability, Marktstärke/Strategie)
    - Anbieter-Kriterien (Support-/Servicekonzept, Unternehmensstärke)
    - Non-funktionale Anforderungen (Skalierbarkeit und Performanz, mobile Nutzung, Mehrsprachigkeit, weltweiter Support, einfache Integration in Bosch-Infrastruktur)
    - Auswertung externer Analysen sowie Zugriff auf die Erfahrungen anderer Nutzer
    - Konkreter Praxistest (sechs Wochen mit konkreten Praxisanforderungen)
- Entscheidung wurde für IBM Connections gefällt (Version 3) mit folgenden Vor- (+) und Nachteilen (-)
    - + Nahezu alle funktionalen Anforderungen erfüllt
    - + Schnittstellen zu relevanten IT-Werkzeugen bei Bosch
    - + IBM nutzt Connections selbst für 400.000 Mitarbeiter
    - + Klare, einfache Benutzerschnittstelle
    - + Gute Strategie und Vision
    - + Support weltweit verfügbar
    - – Verknüpfung von Personen, Informationen und Aktivitäten noch nicht perfekt
    - – Überschneidung im IBM-Produkt-Portfolio
    - – Nicht die höchste Innovationsrate
- Aufbau der Umgebung
    - Mehrtägiger Workshop mit Bosch-Experten (Storage, Netzwerk, Datenbank, Security) sowie IBM-Architekten
    - Auslegung für bis zu 60.000 Nutzer weltweit, weiterer Ausbau in 2013
    - Grundlegende Architekturentscheidung (dreistufige Landschaft (Entwicklungs-, Test-, Produktionssystem), zentrale Installation ohne regionale Komponenten (Caching), komplette Umgebung in isolierter Netzwerkzone (um System mobil/von zu Hause aus dem Internet zu ermöglichen), Nutzung virtualisierter Windows 2008 Server und Datenbank auf Linux-Cluster)
    - Rascher Aufbau einer Sandbox für Pilotanwender zum Kennenlernen des Systems (Vorteil: Menge an Power-Usern wurde gewonnen)
    - Nutzung der Hardware-Lieferzeit (Hardware mit über einem Terrabyte RAM) für detaillierte Planung und Vorbereitung
    - Installation Connections-Datenbank
    - Installation von mehr als 30 virtuellen Servern für alle drei Umgebungen
    - Paralleler Aufbau einer Lasttest-Umgebung
- Landschaft besteht aus WebSEAL Instanzen, Caching Server (bei E2.0 kann nicht lange gecacht werden, da Inhalte sehr dynamisch), Loadbalancer, Tivoli Directory Integrator (Single Sign On), Web Server, WebSphere Application Server, File Storage und Datenbank
- Tuning-Phase
    - Erfolgreicher Test des Profilimports von 200.000 Nutzern
    - Anpassung Corporate Design (eher dezente Anpassung, nur im Rahmen von IBM-Support)
    - Durchführung Lasttest
- Insgesamt 14 Wochen Durchlaufzeit vom Architektur-Workshop bis zur Abnahme des Produktivsystems durch den internen Kunden
- Probleme
    - Identifikation optimale Server/Server-Kommunikation zeitraubend und komplex
    - WebSphere-Konfiguration sehr komplex und damit fehleranfällig
- Erfolgsfaktoren
    - Enge und frühzeitige Einbindung aller Bereiche, permanente Abstimmung
    - Tiefgehendes internes WebSphere Know-how (da viele Einstellungen über Websphere gemacht werden, "Connections sollte eigentlich ‚Social Websphere‘ heißen")
    - Berücksichtigung der internen Komponenten (z.B. Oracle) bei Architekturentscheidungen
    - Sehr gute Unterstützung durch IBM vor Ort und Support/Labor
- Herausforderungen
    - Automatisierung der WebSphere-Konfigurationsänderungen notwendig
    - Connections hat kein Transportsystem, daher war Aufbau eines Deployment-Prozesses notwendig
    - Große Umgebung fürht zu aufwändiger Fehlersuche (unzählige Logdateien!)
- Ausblick
    - Erprobung ausgewählter Anwendungsfllo und anschließender unternehmensweiter Rollout
    - Upgrade auf Connections 4 im November/Dezember
    - Bereitstellung des mobilen Zugriffs
    - Einbindung in Intranet-Portal und Enterprise-Suche
    - Anbindung an Instant-Messaging/Telefonie-Lösung
    - Anbindung an Dokumentenmanagement-System
- Reverse-Mentoring-Programm für Führungskräfte wurde gestartet (Hinweis kam, dass man es eigentlich in "Mentoring" umbenennen sollte, da Hierarchie nicht mehr so relevant)
- Erster Anwendungsfall ist Community aller IT-Manager

## Adios Capitano – Kommunikation und Führung im digitalen Umbruch

- Referent: Prof. Ewald Wessling
- Revolution 2.0: Nachkriegsgeneration hat im Schnitt 1,9 Medien gleichzeitig genutz, heutige Generationen 5,4
- "Technologie wird immer nach der Geburt erfunden" (für einen 6-jährigen ist ein iPhone keine Technologie, sondern die Welt)
- Viedeo: wir leben in einer exponentiellen Zeit
- Beispiel zur Weisheit der Vielen: der Publikumsjoker ist weltweit in allen WWM-Sendungen der erfolgreichsten Joker
- Handyenzug statt Stubenarrest (schickt man einen 15-jährigen für drei Stunden auf sein Zimmer, fragt er sich "womit habe ich das verdient?")
- Führung 2.0: Unternehmen müssen Wissen organisieren unter den Rahmenbedingungen Komplexität und Geschwindigkeit. Hierfür ist "Führung durch Vernetzung" nicht "Führung durch Bestimmen" notwendig
- Adios Capitano verdeutlicht anhand von Bildern von Ballak/Lahm, Schröder/Merkel/Piratenpartei
- Beispiel FARC (Terrorgruppe) in Kolumbien, selbstorganisierte Facebook-Gruppe "No Mas FARC" zu deren Bekämpfung (nach kurzer Zeit über 200.000 Fans)

## IBM Collaboration Solutions: ein bunter live Streifzug durch das aktuelle Software Portfolio

- Live-Demonstration von **IBM Lotus Notes Social Edition**
- Live-Demonstration von **IBM Connections 4**
    - Aktivitätenstrom im Inhaltsberich (mit Filtermechanismus), einzelne Aktivitäten haben rechts kleine Pfeile, um ein Vorschaufenster einzublenden
    - Microblog-Eingabefeld obendrüber (Microblogs können geliket und ge-repostet werden)
    - Externe Systeme können in den Aktivitätenstrom eingebunden werden (z.B. SAP)
    - Communities haben jetzt nicht mehr einzelne Widgets zu Forum etc., sondern einen integrierten Aktivitätenstrom
    - Communities haben jetzt Gruppen, Drag&Drop von Dokumenten
    - In Kalender gibt es die Funktion "Add to Personal Calender" mit RSS-Icon
    - Anmeldung bei Kalender-Einträgen ist möglich
    - Neu: auf Profilen  werden öffentliche Aktivitäten angezeigt
    - In Communities gibt es Metrics (dahinter steckt Cognos) mit number of unique authenticated visitors, number of new members, mumber of members who left the communiy, number of unique contributirs, number or new updates, number of unique people following the community, most active content
    - In der Toolbar oben gibt es ein Mail-Symbol an das Domino oder Exchange angebunden werden können
- Live-Demonstration **IBM Social Portal**

- Fiktive Firma Greenwell
- Social media Aktivitäten in Connections, Facebook und Twitter sind im WCMS integriert
