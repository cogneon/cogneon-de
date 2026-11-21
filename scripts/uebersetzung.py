"""Übersetzungen unter docs/en/ verwalten.

  python3 scripts/uebersetzung.py status
      Zeigt alle englischen Seiten und ob ihre deutsche Vorlage sich seit der
      Übersetzung geändert hat.

  python3 scripts/uebersetzung.py stempel docs/en/contact.md [...]
      Trägt nach dem Übersetzen den aktuellen Prüfwert der Vorlage ein
      (quelle_hash). Ohne Dateiangabe: alle englischen Seiten.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_data import frontmatter, quell_hash  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"


def seiten(argumente: list[str]) -> list[Path]:
    if argumente:
        return [Path(a).resolve() for a in argumente]
    return sorted((DOCS / "en").rglob("*.md"))


def status() -> int:
    veraltet = 0
    for en in seiten([]):
        meta = frontmatter(en)
        quelle = meta.get("quelle")
        if not quelle:
            continue
        de = DOCS / quelle
        if not de.exists():
            zustand = "Vorlage fehlt"
        elif meta.get("frozen"):
            zustand = "eingefroren"
        elif str(meta.get("quelle_hash") or "") == quell_hash(de):
            zustand = "aktuell"
        else:
            zustand = "VERALTET"
            veraltet += 1
        print(f"{zustand:14} {en.relative_to(DOCS)}  <-  {quelle}")
    return 1 if veraltet else 0


def stempel(argumente: list[str]) -> int:
    for en in seiten(argumente):
        text = en.read_text(encoding="utf-8")
        quelle = frontmatter(en).get("quelle")
        if not quelle:
            print(f"übersprungen (kein quelle:): {en}")
            continue
        wert = quell_hash(DOCS / quelle)
        neu, n = re.subn(r'^quelle_hash:.*$', f'quelle_hash: "{wert}"', text, count=1, flags=re.M)
        if not n:
            neu = text.replace(f"quelle: {quelle}\n", f'quelle: {quelle}\nquelle_hash: "{wert}"\n', 1)
        en.write_text(neu, encoding="utf-8")
        print(f"{en.relative_to(DOCS)}: {wert}")
    return 0


if __name__ == "__main__":
    befehl, *rest = sys.argv[1:] or ["status"]
    sys.exit(status() if befehl == "status" else stempel(rest))
