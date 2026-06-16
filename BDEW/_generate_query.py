#!/usr/bin/env python3
"""
BDEW Social-Media-Handles -> kompakte author:()-Query fuer Brandwatch.

Sammelt die Handles ALLER vier Kanaele (X, Instagram, Facebook, Bluesky)
aus BDEW_SocialMedia_GESAMT.xlsx und baut eine einzige, maximal kompakte
Klausel:

    OR author:(h1 OR h2 OR ... OR hn)

zum Anhaengen ans Ende einer bestehenden Query.

Handle je Kanal (= author-Token, kleingeschrieben, kanaluebergreifend dedupt):
  - X / Twitter : Username  (x.com/<user>, twitter.com/<user>)
  - Instagram   : Username-Slug
  - Facebook    : Vanity-Username  (numerische Page-IDs gehen NICHT mit author:)
  - Bluesky     : voller Handle (<name>.bsky.social)

Hinweis (Brandwatch-Doku Kap. 13.4): author: ist fuer FB/IG nicht zuverlaessig,
fuer FB/IG ist channelId: robuster. Hier dennoch author:, weil so gewuenscht.
"""
import re
from pathlib import Path
from urllib.parse import urlparse, parse_qs, unquote

import openpyxl

ROOT = Path(__file__).resolve().parent.parent
XLSX = ROOT / "BDEW_SocialMedia_GESAMT.xlsx"
OUT = ROOT / "BDEW" / "author_query.txt"

IG_NON_PROFILE = {"p", "reel", "reels", "explore", "stories", "tv", "s", "accounts",
                  "legal", "about", "privacy", "terms", "directory", "developer", "web"}
X_RESERVED = {
    "i", "intent", "share", "search", "hashtag", "home", "explore", "settings",
    "privacy", "tos", "login", "signup", "messages", "notifications", "compose",
    "status", "about", "help", "press", "jobs", "de", "en", "discover",
}
FB_SYSTEM = {
    "policy.php", "privacy", "photo", "photo.php", "help", "legal", "terms",
    "login", "login.php", "share", "sharer", "sharer.php", "story.php",
    "permalink.php", "watch", "groups", "events", "marketplace", "gaming",
    "media", "public", "bookmarks", "settings", "careers", "business", "ads",
    "l.php", "home.php", "recover", "checkpoint", "notes", "events.php",
}


def unwrap(u: str) -> str:
    if "urldefense.com" not in u:
        return u
    m = re.search(r"__(https?:/.*?)__;", u)
    if not m:
        return u
    return re.sub(r"^(https?):/(?!/)", r"\1://", m.group(1))


def base_host(netloc: str) -> str:
    return re.sub(r"^(www|m|mobile|de-de|l)\.", "", netloc.lower())


def x_handle(raw):
    u = unwrap(unquote(str(raw).strip()))
    p = urlparse(u if "://" in u else "https://" + u)
    if base_host(p.netloc) not in ("x.com", "twitter.com"):
        return None
    segs = [s for s in p.path.split("/") if s]
    if not segs:
        return None
    h = segs[0].lstrip("@").split("?")[0]
    if h.lower() in X_RESERVED or not re.fullmatch(r"[A-Za-z0-9_]{1,15}", h):
        return None
    return h.lower()


def ig_handle(raw):
    u = unwrap(unquote(str(raw).strip()))
    p = urlparse(u if "://" in u else "https://" + u)
    if base_host(p.netloc) != "instagram.com":
        return None
    segs = [s for s in p.path.split("/") if s]
    if not segs:
        return None
    first = segs[0].lower()
    if first == "accounts":
        cand = [s for s in parse_qs(p.query).get("next", [""])[0].split("/") if s]
        if cand and re.fullmatch(r"[A-Za-z0-9._]+", cand[0]) and cand[0].lower() not in IG_NON_PROFILE:
            return cand[0].lower()
        return None
    if first in IG_NON_PROFILE or not re.fullmatch(r"[A-Za-z0-9._]+", segs[0]):
        return None
    return segs[0].lower()


def fb_handle(raw):
    """Nur Vanity-Username (author: kann keine numerischen IDs)."""
    u = unwrap(unquote(str(raw).strip()))
    p = urlparse(u if "://" in u else "https://" + u)
    if "facebook.com" not in p.netloc.lower():
        return None
    if "id" in parse_qs(p.query):  # profile.php?id= -> nur numerisch, kein Handle
        return None
    segs = [s for s in p.path.split("/") if s]
    if not segs:
        return None
    first = segs[0]
    # ID-basierte Formen (kein Vanity-Handle -> via channelId:, nicht author:)
    if first.lower() in {"pages", "people", "profile.php", "pg", "category", "p"}:
        return None
    # FB-System-/Utility-Seiten, keine Marken-Pages
    if first.lower() in FB_SYSTEM:
        return None
    if not re.fullmatch(r"[A-Za-z0-9.]+", first):  # echte FB-Vanity: a-z0-9.
        return None
    return first.lower()


def bsky_handle(raw):
    u = unwrap(unquote(str(raw).strip()))
    p = urlparse(u if "://" in u else "https://" + u)
    if "bsky.app" not in p.netloc.lower():
        return None
    segs = [s for s in p.path.split("/") if s]
    if len(segs) >= 2 and segs[0].lower() == "profile":
        return segs[1].lower()
    return None


def main():
    wb = openpyxl.load_workbook(XLSX, read_only=True, data_only=True)
    ws = wb["Alle Ergebnisse"]
    rows = list(ws.iter_rows(min_row=2, values_only=True))

    cols = {"X": (2, x_handle), "Instagram": (3, ig_handle),
            "Facebook": (4, fb_handle), "Bluesky": (5, bsky_handle)}

    seen = set()
    handles = []           # dedupt, kanaluebergreifend, Reihenfolge erhalten
    per_channel = {}
    for ch, (idx, fn) in cols.items():
        cnt = 0
        for r in rows:
            if not r[idx]:
                continue
            h = fn(r[idx])
            if not h or re.fullmatch(r"[0-9.]+", h):
                continue  # rein-numerisch = ID, kann author: nicht matchen -> channelId:
            cnt += 1
            if h not in seen:
                seen.add(h)
                handles.append(h)
        per_channel[ch] = cnt

    clause = "OR author:(" + " OR ".join(handles) + ")"
    OUT.write_text(clause, encoding="utf-8")

    print("=== BDEW author:()-Query ===")
    for ch in cols:
        print(f"  {ch:10s}: {per_channel[ch]} Handles extrahiert")
    print(f"  -> unique kanaluebergreifend: {len(handles)}")
    print(f"  -> Zeichen gesamt: {len(clause)}  (Saved-Search-Limit 100.000)")
    print(f"  -> geschrieben: {OUT}")


if __name__ == "__main__":
    main()
