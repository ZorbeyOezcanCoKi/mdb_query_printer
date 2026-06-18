#!/usr/bin/env python3
"""
BDEW Category in 4000-Zeichen-Sub-Categories splitten.

Pro Unternehmen genau EIN Handle (Prio FB>X>IG>Bluesky, wie _generate_category),
dann die Author-Liste so in Bloecke aufteilen, dass jede Sub-Category passt:

  ( Texte, ~1000 Zeichen reserviert )  AND  author:( ... )   <= 4000 Zeichen

Budget:
  - 1000 Zeichen fuer die Textfetzen (Platzhalter, vom Nutzer zu fuellen)
  - Author-Klausel `author:(...)`  <= 2990 Zeichen
  -> Gesamt mit vollem Text + " AND " bleibt < 4000.

Output:
  BDEW/categories/category_01.txt ...  - je 1 fertige Query-Zeile (nur einfuegen)
  BDEW/categories/_uebersicht.txt      - Stats je Sub-Category
"""
import re
import shutil
from pathlib import Path

import openpyxl

from _generate_query import x_handle, ig_handle, fb_handle, bsky_handle

ROOT = Path(__file__).resolve().parent.parent
XLSX = ROOT / "BDEW_SocialMedia_GESAMT.xlsx"
OUTDIR = ROOT / "BDEW" / "categories"

TOTAL_LIMIT = 4000
TEXT_RESERVE = 1000
AUTHOR_MAX = TOTAL_LIMIT - TEXT_RESERVE - len(" AND ")  # = 2995 -> Klausel `author:(...)`
AUTHOR_MAX = 2990                                        # kleine Sicherheitsmarge

# Platzhalter-Textblock (vom Nutzer ersetzen, <= ~1000 Zeichen, in ALLEN gleich)
TEXT_PLACEHOLDER = '("PLATZHALTER PHRASE 1" OR "PLATZHALTER PHRASE 2")'

PRIO = [(4, fb_handle), (2, x_handle), (3, ig_handle), (5, bsky_handle)]


def collect_handles():
    wb = openpyxl.load_workbook(XLSX, read_only=True, data_only=True)
    ws = wb["Alle Ergebnisse"]
    seen, handles = set(), []
    for r in ws.iter_rows(min_row=2, values_only=True):
        for idx, fn in PRIO:
            if not r[idx]:
                continue
            h = fn(r[idx])
            if h and not re.fullmatch(r"[0-9.]+", h):
                if h.lower() not in seen:
                    seen.add(h.lower())
                    handles.append(h)
                break
    return handles


def chunk_by_chars(handles, budget):
    """Greedy: fuelle author:(...) bis < budget Zeichen, dann naechster Block."""
    chunks, cur = [], []
    base = len("author:()")
    sep = len(" OR ")
    cur_len = base
    for h in handles:
        add = len(h) + (sep if cur else 0)
        if cur and cur_len + add > budget:
            chunks.append(cur)
            cur, cur_len = [], base
            add = len(h)
        cur.append(h)
        cur_len += add
    if cur:
        chunks.append(cur)
    return chunks


def main():
    handles = collect_handles()
    chunks = chunk_by_chars(handles, AUTHOR_MAX)

    if OUTDIR.exists():
        shutil.rmtree(OUTDIR)
    OUTDIR.mkdir(parents=True)

    lines = [f"BDEW Category-Split  —  {len(handles)} Accounts in {len(chunks)} Sub-Categories",
             f"Limit {TOTAL_LIMIT} Z. | Text-Reserve {TEXT_RESERVE} Z. | author:(...) <= {AUTHOR_MAX} Z.",
             ""]
    n = len(chunks)
    for i, ch in enumerate(chunks, 1):
        clause = "author:(" + " OR ".join(ch) + ")"
        query = f"{TEXT_PLACEHOLDER} AND {clause}"
        # Gesamt bei VOLLEM 1000-Zeichen-Text:
        worst = TEXT_RESERVE + len(" AND ") + len(clause)
        fname = f"category_{i:02d}.txt"
        (OUTDIR / fname).write_text(query + "\n", encoding="utf-8")
        lines.append(
            f"{fname}: {len(ch):3d} Accounts | author:() {len(clause):4d} Z. | "
            f"jetzt gesamt {len(query):4d} Z. | mit 1000 Z. Text max {worst} Z.")

    (OUTDIR / "_uebersicht.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    over = [i for i, ch in enumerate(chunks, 1)
            if TEXT_RESERVE + 5 + len("author:(" + " OR ".join(ch) + ")") > TOTAL_LIMIT]
    print(f"\nSub-Categories ueber {TOTAL_LIMIT} (worst case): {over or 'keine'}")
    print(f"Summe Accounts: {sum(len(c) for c in chunks)} (== {len(handles)})")


if __name__ == "__main__":
    main()
