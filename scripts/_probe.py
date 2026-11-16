"""Einmalige Erkundung der Schnittstellen für Termine und Weiterleitungen."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import wp_export
wp = wp_export.WordPress("https://cogneon.de")
def show(route, params):
    r = wp.get(route, params)
    print("==", route, params, r.status_code, {k: v for k, v in r.headers.items() if k.lower().startswith("x-")})
    try:
        d = r.json()
    except Exception:
        print(r.text[:300]); return
    def cut(o):
        if isinstance(o, dict): return {k: cut(v) for k, v in list(o.items())[:60]}
        if isinstance(o, list): return [cut(v) for v in o[:2]] + ([f"... {len(o)} gesamt"] if len(o) > 2 else [])
        if isinstance(o, str): return o[:160]
        return o
    print(json.dumps(cut(d), ensure_ascii=False, indent=1)[:7000])
show("tribe/events/v1/events", {"per_page": 2, "start_date": "2001-01-01", "status": "publish"})
show("tribe/events/v1/categories", {"per_page": 50})
show("redirection/v1/redirect", {"per_page": 3, "page": 0})
show("redirection/v1/group", {"per_page": 50})
