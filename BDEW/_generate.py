#!/usr/bin/env python3
"""
BDEW Social-Media-Handles -> Brandwatch-Upload-CSVs.

Liest BDEW_SocialMedia_GESAMT.xlsx (Sheet "Alle Ergebnisse") und erzeugt
ein-spaltige CSVs mit je max. 100 Eintraegen pro Datei, getrennt nach Kanal:

  - Instagram: Username-Slug (z. B. "50hertz")
  - Facebook : Vanity-Username wo vorhanden, sonst numerische Page-ID
               (aus profile.php?id=, /pages/Name/ID, /people/Name/ID,
                bzw. an den Namen gehaengte -ID).

Format laut Brandwatch-Doku Kap. 13.2 ("Connecting Facebook/Instagram
Channels" / Tracking Content Sources): das Tracking-Backend akzeptiert
Page-URLs, Usernames oder Page-IDs. Fuer den Upload reicht je Zeile ein
Identifier; Duplikate werden entfernt (case-insensitive, Reihenfolge bleibt).

Output: BDEW/instagram/*.csv, BDEW/facebook/*.csv, je ein *_alle.csv und
        _uebersprungen.csv (verworfene/uneindeutige Eintraege).
"""
import csv
import re
from pathlib import Path
from urllib.parse import urlparse, parse_qs, unquote

import openpyxl

ROOT = Path(__file__).resolve().parent.parent
XLSX = ROOT / "BDEW_SocialMedia_GESAMT.xlsx"
OUT = ROOT / "BDEW"
CHUNK = 100

# Pfad-Segmente, die kein Profil bezeichnen
IG_NON_PROFILE = {"p", "reel", "reels", "explore", "stories", "tv", "s", "accounts",
                  "legal", "about", "privacy", "terms", "directory", "developer", "web"}
# FB-System-/Utility-Seiten (keine Marken-Pages)
FB_SYSTEM = {
    "policy.php", "privacy", "photo", "photo.php", "help", "legal", "terms",
    "login", "login.php", "share", "sharer", "sharer.php", "story.php",
    "permalink.php", "watch", "groups", "events", "marketplace", "gaming",
    "media", "public", "bookmarks", "settings", "careers", "business", "ads",
    "l.php", "home.php", "recover", "checkpoint", "notes", "events.php",
}


def unwrap_urldefense(u: str) -> str:
    """Proofpoint-urldefense-Wrapper aufloesen -> innere echte URL."""
    if "urldefense.com" not in u:
        return u
    m = re.search(r"__(https?:/.*?)__;", u)
    if not m:
        return u
    inner = m.group(1)
    # urldefense ersetzt '//' durch '/', wieder herstellen
    inner = re.sub(r"^(https?):/(?!/)", r"\1://", inner)
    return inner


def ig_username(raw: str):
    """-> (username, None) bei Erfolg, sonst (None, grund)."""
    u = unwrap_urldefense(unquote(str(raw).strip()))
    p = urlparse(u if "://" in u else "https://" + u)
    host = p.netloc.lower()
    # Subdomain-Praefixe abstreifen
    host = re.sub(r"^(www|m|de-de|l)\.", "", host)
    if host != "instagram.com":
        return None, f"kein instagram.com-Host ({p.netloc})"
    segs = [s for s in p.path.split("/") if s]
    if not segs:
        return None, "kein Pfad (nur instagram.com/)"
    first = segs[0].lower()
    # Login-Wall-Redirect: /accounts/login/?next=/<handle>/ -> echtes Profil
    if first == "accounts":
        nxt = parse_qs(p.query).get("next", [""])[0]
        cand = [s for s in nxt.split("/") if s]
        if cand and re.fullmatch(r"[A-Za-z0-9._]+", cand[0]) \
                and cand[0].lower() not in IG_NON_PROFILE:
            return cand[0].lower(), None
        return None, f"kein Profil (/{first}/-Link)"
    if first in IG_NON_PROFILE:
        return None, f"kein Profil (/{first}/-Link)"
    if not re.fullmatch(r"[A-Za-z0-9._]+", segs[0]):
        return None, f"ungueltiger Username '{segs[0]}'"
    return segs[0].lower(), None


def fb_identifier(raw: str):
    """-> (identifier, None) bei Erfolg, sonst (None, grund).

    identifier = Vanity-Username ODER numerische Page-ID.
    """
    u = unwrap_urldefense(unquote(str(raw).strip()))
    p = urlparse(u if "://" in u else "https://" + u)
    host = p.netloc.lower()
    if "facebook.com" not in host:
        return None, f"kein facebook.com-Host ({p.netloc})"

    # 1) profile.php?id=NUM  (auch ?viewas=..&id=..)
    q = parse_qs(p.query)
    if "id" in q and q["id"][0].isdigit():
        return q["id"][0], None

    segs = [s for s in p.path.split("/") if s]
    if not segs:
        return None, "kein Pfad (nur facebook.com/)"

    # 2) eigenstaendiges numerisches Segment (/pages/Name/ID, /people/Name/ID)
    for s in reversed(segs):
        s0 = s.split("?")[0]
        if s0.isdigit() and len(s0) >= 6:
            return s0, None

    # 3) an den Namen geklebte -ID, in irgendeinem Segment
    #    (z. B. /pages/Stadtwerke-Stendal-176838711108143,
    #     /pg/AmperVerband-103558031582929/posts/)
    for s in reversed(segs):
        m = re.search(r"-(\d{9,})$", s.split("?")[0])
        if m:
            return m.group(1), None

    # 4) Vanity-Username:  facebook.com/<vanity>
    first = segs[0]
    if first.lower() in {"pages", "people", "profile.php", "pg", "category", "p"}:
        # Page-/People-/p-Form ohne extrahierbare ID -> kein verlaesslicher Identifier
        return None, f"Page-/People-Pfad ohne numerische ID ({p.path})"
    if first.lower() in FB_SYSTEM:
        return None, f"FB-System-/Utility-Seite (/{first})"
    if not re.fullmatch(r"[A-Za-z0-9._-]+", first):
        return None, f"ungueltiger Vanity-Name '{first}'"
    return first, None


def dedupe(pairs):
    """pairs: list[(value, name)]. Case-insensitive dedupe, Reihenfolge erhalten."""
    seen = {}
    out = []
    for val, name in pairs:
        k = val.lower()
        if k in seen:
            continue
        seen[k] = name
        out.append(val)
    return out


def write_chunks(values, subdir, stem):
    d = OUT / subdir
    d.mkdir(parents=True, exist_ok=True)
    # alte Generate-Outputs in diesem Unterordner aufraeumen
    for old in d.glob("*.csv"):
        old.unlink()
    # _alle
    with (d / f"{stem}_alle.csv").open("w", newline="", encoding="utf-8") as f:
        for v in values:
            f.write(v + "\n")
    # Chunks
    n = 0
    for i in range(0, len(values), CHUNK):
        n += 1
        with (d / f"{stem}_handles_{n}.csv").open("w", newline="", encoding="utf-8") as f:
            for v in values[i:i + CHUNK]:
                f.write(v + "\n")
    return n


def main():
    wb = openpyxl.load_workbook(XLSX, read_only=True, data_only=True)
    ws = wb["Alle Ergebnisse"]
    rows = list(ws.iter_rows(min_row=2, values_only=True))

    ig_ok, fb_ok, skipped = [], [], []
    for r in rows:
        name = r[0]
        if r[3]:
            val, why = ig_username(r[3])
            (ig_ok.append((val, name)) if val else
             skipped.append(("Instagram", name, str(r[3]), why)))
        if r[4]:
            val, why = fb_identifier(r[4])
            (fb_ok.append((val, name)) if val else
             skipped.append(("Facebook", name, str(r[4]), why)))

    ig_vals = dedupe(ig_ok)
    fb_vals = dedupe(fb_ok)

    OUT.mkdir(exist_ok=True)
    n_ig = write_chunks(ig_vals, "instagram", "instagram")
    n_fb = write_chunks(fb_vals, "facebook", "facebook")

    with (OUT / "_uebersprungen.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Kanal", "Name", "URL", "Grund"])
        w.writerows(skipped)

    print("=== BDEW Brandwatch-Upload-Export ===")
    print(f"Instagram: {len(ig_ok)} extrahiert -> {len(ig_vals)} unique -> {n_ig} CSV(s)")
    print(f"Facebook : {len(fb_ok)} extrahiert -> {len(fb_vals)} unique -> {n_fb} CSV(s)")
    print(f"Uebersprungen: {len(skipped)} (siehe BDEW/_uebersprungen.csv)")


if __name__ == "__main__":
    main()
