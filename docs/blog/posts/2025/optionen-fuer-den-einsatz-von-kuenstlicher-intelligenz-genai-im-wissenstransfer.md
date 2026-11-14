---
title: Optionen für den Einsatz von Künstlicher Intelligenz (GenAI) im Wissenstransfer
date:
  created: '2025-07-19'
  updated: '2025-07-19'
slug: optionen-fuer-den-einsatz-von-kuenstlicher-intelligenz-genai-im-wissenstransfer
authors:
- simon-dueckert
categories:
- Wissenstransfer
tags:
- GenerativeKI
wp:
  id: 65559
  link: https://cogneon.de/2025/07/19/optionen-fuer-den-einsatz-von-kuenstlicher-intelligenz-genai-im-wissenstransfer/
  featured_media: 65573
---

# Optionen für den Einsatz von Künstlicher Intelligenz (GenAI) im Wissenstransfer

In nahezu allen unseren **Aktivitäten zum Wissenstransfer** wie beispielsweise dem [Expert Debriefing](/ed), oder den [Keep-Experience-Workshops](/kex/) (KEX Workshops) für den Wissenstransfer, aber auch in **Lernveranstaltungen** wie dem [SAP Learning & Adoption Forum 2025](https://cogneon.github.io/sapf25doku/de/) oder die [lernOS Convention 2025](https://cogneon.github.io/loscon25doku/de/) kommt seit einiger Zeit **Künstliche Intelligenz** (KI), speziell **Generative KI** (GenAI) zum Einsatz. Damit wird ein entscheidender Paradigmenwechsel möglich. Seit der Erfindung der Schrift und all ihren Folgeerscheinungen (Buchdruck, Internet, Textverarbeitung etc.) ist das Dokument (z.B. eine Powerpoint-Präsentation, ein Artikel als PDF) die zentrale Währung der Wissensvermittlung in vielen Organisationen.

<!-- more -->

Das **Problem beim Wissenstransfer** ist, dass das relevante Wissen in den Informationen, beispielsweise in den Spiegelstrichen, gar nicht enthalten ist. Es steckt in dem gesprochenen Wort, das ich während der Präsentation äußere sowie in den **Erfahrungen und Geschichten**, von denen ich berichte. Das **Wissen steckt „zwischen den Spiegelstrichen“** der Präsentation. Das Gleiche gilt beispielsweise für die Protokollierung von Besprechungen. Es hängt sehr von der verfügbaren Zeit des Protokollanten (sofern es überhaupt einen gibt) und dessen subjektiver Sichtweise und Bewertung (Stichwort: [Cognitive Bias](https://de.wikipedia.org/wiki/Kognitive_Verzerrung)) ab, welche Informationen im Protokoll landen – und welche nicht.

Mithilfe von GenAI ist hier nun **eine neue Herangehensweise** möglich. Statt wie bisher nach Vorträgen, Besprechungen und Schulungen Folien zu verteilen, kann nun -die Einwilligung aller Beteiligten vorausgesetzt- **das gesprochene Wort aufgezeichnet und automatisch transkribiert** werden. Aus diesen Transkripten können dann gewünschte Inhalte wie beispielsweise Zusammenfassungen, FAQs, Lessons Learned, Aufgabenliste usw. generiert werden. Außerdem steht das vollständige Transkript von einer oder mehrerer Veranstaltungen zur Verfügung und kann in einem KI-Tool wie beisielsweise einem Chatbot „befragt“ werden.

Dabei stellt sich oft die Frage nach **Datenschutz und Datensicherheit**. Die sogenannten „Frontline Modelle“ wie Claude, GPT-4.1 und Gemini bieten natürlich meistens die beste Qualität bei der Generierung von Inhalten. Dies wird dadurch ermöglicht, dass die Berechnung der Ergebnisse (Inferenz) in sehr leistungsstarken Rechenzentren in der Cloud, also auf Computern anderer Leute, stattfindet. Bei Veranstaltungen wie dem [SAP Learning & Adoption Forum](https://cogneon.github.io/sapf25doku/de/) oder der [lernOS Convention](https://cogneon.github.io/loscon25doku/de/), bei denen die Inhalte im Nachgang ohnehin veröffentlicht werden, ist das kein Problem. In [Expert Debriefings](/ed) und [KEX Workshops](/kex/) haben wir es jedoch häufig mit vertraulichen oder gar geheimen Inhalten zu tun, die auf keinen Fall in der Cloud und manchmal nicht einmal auf unserer Infrastruktur gespeichert werden dürfen.

Auf diese verschiedenen Anforderungen haben wir uns eingestellt und bieten für Veranstaltungen, Expert Debriefings und KEX-Workshops **unterschiedliche Optionen des KI-Einsatzes**. Das folgende Schaubild erklärt die Optionen und deren Implikationen:

![](/wp-content/uploads/2025/07/ed-kex-event-infrastruktur-1030x826.png)

1. Ausgangspunkt in der Praxis ist immer die **Tonspur einer Audio- oder Videoaufzeichnung**. Das kann z.B. die integrierte Aufnahmefunktion in Microsoft Teams, Zoom oder WebEx sein. Wenn das nicht möglich ist, können wir aber auch mit Podcast-Mischpulten oder separaten Mikrofonen aufzeichnen. Die Aufnahmen liegen dann in der genutzten Software (z.B. Videokonferenz-Tool) oder Hardware (z.B. Audiorekorder).
2. Die **Tonspur aus der Aufzeichnung transkribieren wir** mit [Whisper](https://en.wikipedia.org/wiki/Whisper_(speech_recognition_system)), einem Sprachmodell von OpenAI, das aber anders als ChatGPT nicht in der Cloud, sondern auf eigener Infrastruktur ausgeführt wird. Bei Mitarbeitenden mit Macs geschieht das direkt auf dem Laptop, bei Windows-11-PCs wird ein lokaler Server in unserer eigenen IT-Infrastruktur verwendet.
3. Für die **Auswertung der Transkripte** haben wir einen Knowledge-Transfer-Prompt-Katalog entwickelt, der z.B. Prompts für Zusammenfassungen, Lessons Learned, Checklisten, Aufgabenbeschreibungen, Projektübersichten, Wiki-Seiten, Kunden- und Wettbewerber-Dossiers uvm. enthält. Das war in den Projekten früher sehr viel Handarbeit! Die Prompts können unabhängig von der verwendeten KI-Technologie (i.d.R. Microsoft Copilot, ChatGPT Enterprise oder lokale KI/Chatbots) verwendet werden.
4. Für die **Inferenz der Sprachmodelle** (LLMs) bieten wir in der Praxis folgende Optionen an:
   - **Cloud-basiertes Frontline Modell (z.B. GPT-4x, Claude 4)** – wir verwenden in allen Fällen bezahlte Zugänge, die zusichern, dass die bereitgestellten Daten nicht für Trainingszwecke verwendet werden. Dieser Weg liefert aus unserer Erfahrung die besten Ergebnisse.
   - **Microsoft Copilot oder Azure OpenAI API in unserem Microsoft 365 Tenant** – die Daten bleiben innerhalb unseres Tenants (Bereicht) in der Microsoft 365 Cloud, für den wir einen [Vertrag für Auftragsdatenverarbeitung](https://www.e-recht24.de/artikel/datenschutz/10580-auftragsdatenverarbeitung-adv-datenschutz.html) haben. Dieser. Weg liefert auch sehr gute Ergebnisse, bei erhöhter Datensicherheit.
   - **Lokale Sprachmodelle (Open Weights Modelle) wie z.B. Llama, Qwen oder Phi** – diese Modell kann man wie Whisper herunterladen und auf eigenen Rechnern ausführen. Die verwendeten Daten verlassen also genau wie die Transkripte nicht unsere eigene IT-Infrastruktur. Die Datensicherheit ist sehr hoch, die Qualität aber bisher auch deutlich niedriger.
   - **KI-Tools in der Infrastruktur der Kunden** – viele Organisationen haben mittlerweile eigene KI-Tools in der Infrastruktur, die sich meist an die Funktionalität von ChatGPT anlehnen (z.B. [BoschGPT](https://industriemagazin.at/news/boschgpt-ki-sprachmodell-von-bosch-wird-zum-vorbild-fuer-heimische-industrie/), [DATEV GPT](https://www.datev.de/web/de/ueber-datev/datev-ki/datev-ki-werkstatt/), [SparkasseGPT](https://www.sparkasse.de/ueber-uns/kuenstliche-intelligenz/sparkassegpt.html)). In diesen Fällen liefern wir Transkripte und entsprechende Prompts und die Auswertung der Inhalte geschieht komplett in der Infrastruktur und mit den Sicherheitsvorgaben der Kunden.

Habt ihr auch Anwendungsfälle für die Unterstützung des Wissenstransfers mit KI? Sprecht uns gerne an, wir sind für alle Projektideen offen und natürlich für professionelle Lösungen EU-AI-Act-qualifiziert.
