---
title: Bausteine
description: Übersicht der Bausteine, die Redakteur:innen in Markdown-Seiten verwenden können.
---

# Bausteine

Diese Seite zeigt, welche Bausteine in normalen Markdown-Seiten zur Verfügung
stehen und wie man sie schreibt. Sie dient als Nachschlagewerk für die
Redaktion und wird vor dem Go-live aus der Navigation genommen.

## Knopf

Ein Link wird zum Knopf, wenn man ihm die Klasse `cg-button` gibt. Pro Seite
möglichst nur ein Knopf.

```markdown
[Erstgespräch anfragen](mailto:info@cogneon.de){ .cg-button }
```

[Erstgespräch anfragen](mailto:info@cogneon.de){ .cg-button }

## Karten

Eine Liste in einem Block mit der Klasse `cg-cards` wird zu Karten.

```markdown
<div class="cg-cards" markdown>

- **Wissenstransfer**

    Erfahrungswissen sichern und weitergeben.

    [Zum Angebot](wissenstransfer.md)

- **Expert Debriefing**

    Interviewprozess für das Wissen einer Person.

    [Zum Angebot](expert-debriefing.md)

</div>
```

<div class="cg-cards" markdown>

- **Wissenstransfer**

    Erfahrungswissen sichern und weitergeben.

    [Zum Angebot](wissenstransfer.md)

- **Expert Debriefing**

    Interviewprozess für das Wissen einer Person.

    [Zum Angebot](expert-debriefing.md)

</div>

## Schritte

Eine nummerierte Liste in einem Block mit der Klasse `cg-schritte` wird zum Ablauf.

```markdown
<div class="cg-schritte" markdown>

1. **Vorgespräch**<br>Kontext und Ziel klären.
2. **Durchführung**<br>Maßnahmen umsetzen.
3. **Reflexion**<br>Ergebnis prüfen.

</div>
```

<div class="cg-schritte" markdown>

1. **Vorgespräch**<br>Kontext und Ziel klären.
2. **Durchführung**<br>Maßnahmen umsetzen.
3. **Reflexion**<br>Ergebnis prüfen.

</div>

## Zitat

```markdown
<figure class="cg-zitat" markdown>
> [Zitat - nur mit Freigabe]

<figcaption>[Name, Funktion, Organisation]</figcaption>
</figure>
```

<figure class="cg-zitat" markdown>
> [Zitat - nur mit Freigabe]

<figcaption>[Name, Funktion, Organisation]</figcaption>
</figure>

## Hinweis

```markdown
!!! note "Hinweis"
    Text des Hinweises.
```

!!! note "Hinweis"
    Text des Hinweises.

## Bausteine mit eigener Vorlage

Startseite und Angebotsseiten haben eigene Vorlagen. Dort stehen die Inhalte
als Felder im Kopf der Markdown-Datei, die Vorlage baut daraus die Abschnitte.

| Vorlage | Felder | Beispiel |
| --- | --- | --- |
| `home.html` | hero, schild, anlaesse, belege | `docs/index.md` |
| `angebot.html` | pfad, untertitel, einleitung, anlaesse, gruppen, formate, ablauf, pakete, verwandt, cta | `docs/expert-debriefing.md` |

Highlights und Termine der Startseite stehen in `inhalte/aktuell.yml`. Ein
Eintrag mit `gueltig_bis` verschwindet nach diesem Datum von selbst.
