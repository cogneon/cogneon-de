---
title: Kommunikation & Kollaboration bei Automattic – was können wir davon lernen?
date:
  created: '2019-08-29'
  updated: '2021-08-28'
slug: kommunikation-kollaboration-bei-automattic-was-koennen-wir-davon-lernen
authors:
- simon-dueckert
categories:
- Fallbeispiel
tags:
- Blogging
- Zusammenarbeit
- Kommunikation
- HybridWork
wp:
  id: 56993
  link: https://cogneon.de/2019/08/29/kommunikation-kollaboration-bei-automattic-was-koennen-wir-davon-lernen/
  featured_media: null
---

# Kommunikation & Kollaboration bei Automattic – was können wir davon lernen?

[Automattic](https://en.m.wikipedia.org/wiki/Automattic) ist das Unternehmen, das hinter der Entwicklung von [WordPress](https://en.m.wikipedia.org/wiki/WordPress) steht. WordPress ist ein Blog- und Content-Management-System, mit dem ca. ein Drittel der Seiten des Internets betrieben werden.

<!-- more -->

Im Urlaub habe ich das Buch [The Year Without Pants](http://www.amazon.de/dp/1118660633/?tag=cogneonde-21) (Affiliate-Link) von Scott Berkun über das Arbeiten bei Automattic gelesen. Interessant ist, dass die knapp 1.000 Mitarbeiter\*innen alle remote und über die Welt verteilt arbeiten. Automattic hatte eine sehr moderne (newworkige) Location am Pier 38, [hat diese aber bereits 2007 geschlossen](https://www.businessinsider.com/automattic-closes-san-francisco-office-to-let-everyone-work-remotely-2017-6), weil dort nur selten jemand gearbeitet hat.

[YouTube: Automattic office at Pier 38 | pestaola.gr](https://youtu.be/73l_ejTIT7k){ .embed }

Im Gegensatz zu Präsenzkulturen muss man sich bei komplett verteilter Arbeit sehr viel mehr Gedanken über Routinen und Tools für die Kommunikation und die Kollaboration in der Organisation und den Teams machen.

Natürlich gibt es bei Automattic auch E-Mail, aber wie der Gründer von Automattic Matt Mullenweg [in seinem Blog](https://ma.tt/2009/05/how-p2-changed-automattic/) schreibt, kam E-Mail nach IRC und Skype schon immer an letzter Stelle der Kommunikationswege. Mit der Einführung von [P2](https://p2theme.com) (Project Log), einem auf Status-Updates basierendem Gruppen-Blog, hat sich das Gleichgewicht der Kommunikation noch weiter verschoben (Seite 48 im Buch):

1. Blogs (P2): 75 Prozent
2. IRC: 14 Prozent
3. Skype: 5 Prozent
4. E-Mail: 1 Prozent

Wichtig ist, dass alle P2s intern für alle offen einsehbar und kommentierbar sind, so dass komplette Transparenz entsteht. Für den Support von Nutzeranfragen gibt es nochvein Ticket-System, über das Tickets erstellt und nachverfolgt werden. Andere Werkzeuge wie Team-Videokonferenzen, Whiteboards etc. wurden zwar ausprobiert, haben sich aber bei verteilten Teams als nicht robust genug erwiesen.

Was können wir aus der Automattic Story lernen? Ich habe für mich folgende Punkte identifiziert:

1. **Open by Default als Leitprinzip:** jeder sollte Informationen zu Zwecken der Kommunikation und Kollaboration offen einsehen können, um Silo-Bildung zu vermeiden.
2. **Blog als E-Mail-Ersatz:** der gemeinsame Team-Blog kann die Team-internen E-Mails weitestgehend ersetzen. Die Öffnung des Blogs für alle ermöglicht Wissenstransfer aus dem Team heraus und Unterstützung des Teams von aussen.
3. **Chat und Audio-Konferenz als Gesprächsersatz:** als Ersatz für das schnelle Gespräch im Büro braucht es Online Chats und Audio-Konferenz-Tools, die möglichst schnell und einfach funktionieren. Chat (asynchron) ist der synchronen Audiokonferenz oft überlegen.
4. **Digitaler Raum für das Team:** wo das P2 eines Teams als dessen Whiteboard zur Dokumentation verstanden werden kann, bildet IRC das digitale Büro. Jedes Team hat dort einen Kanal als Raum, jeder kann jedem Raum Beitreten (digitale Open Door Policy). Ich kenne bis heute kein Werkzeug, dass das besser abbilden kann, als das Anfang der 1990er Jahre entstandene IRC.
5. **Tickets zur Nachverfolgung:** für alle Themen (issues), die nicht verloren gehen dürfen und nachverfolgt werden müssen, braucht es ein Ticketsystem wie Trac, OTRS, Zendesk oder [Zammad](https://zammad.com/de). Nur so können transparen Verantwortlichkeiten für wichtige Themen vergeben werden.

Habt ihr das Buch auch gelesen? Was sind eure Schlussfolgerungen für zeitgemäße Kommunikation und Zusammenarbeit in verteilten Teams?

Wer sich noch tiefer für die Arbeit bei Automattic interessiert, dem empfehle ich den [Podcast Distributed](https://distributed.blog/podcast/) mit Matt Mullenweg.
