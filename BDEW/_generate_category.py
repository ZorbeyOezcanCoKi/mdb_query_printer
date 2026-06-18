#!/usr/bin/env python3
"""
BDEW -> Brandwatch-Category-Query: (EXACT-MATCH Textfetzen) AND author:(...).

Pro Unternehmen (= Zeile in BDEW_SocialMedia_GESAMT.xlsx) genau EIN Handle,
ausgewaehlt nach Prioritaet:  1. Facebook  2. X  3. Instagram  4. Bluesky.

"Handle" = author-faehiger Username:
  - Facebook : Vanity-Username (facebook.com/<name>); numerische/Page-/People-
               /p-Formen haben KEINEN author-Handle -> faellt auf naechste Prio.
  - X        : x.com/twitter.com-Username
  - Instagram: Username-Slug
  - Bluesky  : voller Handle (<name>.bsky.social)

So ist jedes Unternehmen genau EINMAL vertreten. Der Content-Block oben ist
ein Platzhalter (Phrasen noch zu definieren).

Hinweis: author: ist fuer FB/IG laut Brandwatch-Doku unzuverlaessig; robust
waere fuer FB/IG channelId:. Diese Variante nutzt bewusst author: (wie bestellt).

Output:
  BDEW/category_query.txt        - fertige Category-Query (Content-Platzhalter)
  BDEW/category_handle_pick.csv  - Nachweis: Unternehmen -> Plattform/Handle
"""
import csv
import re
from pathlib import Path

import openpyxl

from _generate_query import x_handle, ig_handle, fb_handle, bsky_handle

ROOT = Path(__file__).resolve().parent.parent
XLSX = ROOT / "BDEW_SocialMedia_GESAMT.xlsx"
OUT_Q = ROOT / "BDEW" / "category_query.txt"
OUT_CSV = ROOT / "BDEW" / "category_handle_pick.csv"

# (Spaltenindex, Plattform-Label, Extractor) in Prioritaetsreihenfolge
PRIO = [
    (4, "Facebook", fb_handle),
    (2, "X", x_handle),
    (3, "Instagram", ig_handle),
    (5, "Bluesky", bsky_handle),
]

TEMPLATE = """\
<<< ================================================================= >>>
<<< CATEGORY: BDEW-Unternehmen — Content + Author                     >>>
<<< Schema:  ( EXACT-MATCH Textfetzen )  AND  author:( 1 Handle / Unt.) >>>
<<< Ein Post wird nur getaggt, wenn er BEIDES erfuellt:               >>>
<<<   - genau eine der Phrasen unten enthaelt UND                     >>>
<<<   - von einem der gelisteten Accounts stammt.                     >>>
<<< ================================================================= >>>

<<< 1) TEXTFETZEN — HIER EINTRAGEN. Exact match = Phrase in "..." .    >>>
<<<    Fuer Sonderzeichen (+, &, /) statt "..." -> raw: verwenden.     >>>
(
  "PLATZHALTER PHRASE 1" OR
  "PLATZHALTER PHRASE 2"
)

AND

<<< 2) AUTHORS — genau 1 Handle pro Unternehmen, Prio FB>X>IG>Bluesky.  >>>
<<<    {n_handles} Unternehmen abgedeckt. FB/IG via author: ist laut    >>>
<<<    Brandwatch unzuverlaessig -> fuer FB/IG ggf. channelId: nutzen.  >>>
author:(
{authors}
)
"""


def main():
    wb = openpyxl.load_workbook(XLSX, read_only=True, data_only=True)
    ws = wb["Alle Ergebnisse"]
    rows = list(ws.iter_rows(min_row=2, values_only=True))

    picks = []          # (name, platform, handle)
    uncovered = []      # Unternehmen ohne author-faehigen Handle
    for r in rows:
        name = r[0] or ""
        chosen = None
        for idx, plat, fn in PRIO:
            if not r[idx]:
                continue
            h = fn(r[idx])
            if h and not re.fullmatch(r"[0-9.]+", h):  # rein-numerisch = ID, kein author
                chosen = (name, plat, h)
                break
        if chosen:
            picks.append(chosen)
        elif any(r[idx] for idx, _, _ in PRIO):
            uncovered.append(name)  # hat Links, aber keinen author-Handle (nur FB-IDs)

    # author-Liste: kanaluebergreifend dedupt (Reihenfolge erhalten)
    seen, handles = set(), []
    for _, _, h in picks:
        if h.lower() not in seen:
            seen.add(h.lower())
            handles.append(h)

    authors = " OR\n".join("  " + h for h in handles)
    OUT_Q.write_text(TEMPLATE.format(n_handles=len(handles), authors=authors),
                     encoding="utf-8")

    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Unternehmen", "Plattform", "Handle"])
        w.writerows(picks)

    from collections import Counter
    by_plat = Counter(p for _, p, _ in picks)
    print("=== BDEW Category-Query ===")
    print(f"Unternehmen gesamt:       {len(rows)}")
    print(f"-> mit author-Handle:     {len(picks)}")
    for plat in ("Facebook", "X", "Instagram", "Bluesky"):
        print(f"     {plat:10s}: {by_plat.get(plat, 0)}")
    print(f"-> unique Handles:        {len(handles)}")
    print(f"-> ohne author-Handle:    {len(uncovered)} (nur FB-ID/ohne Social -> channelId noetig)")
    print(f"-> ganz ohne Social:      {len(rows) - len(picks) - len(uncovered)}")
    print(f"geschrieben: {OUT_Q.name}, {OUT_CSV.name}")


if __name__ == "__main__":
    main()
