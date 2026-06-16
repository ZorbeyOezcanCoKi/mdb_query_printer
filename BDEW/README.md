# BDEW — Brandwatch-Upload-CSVs (Instagram & Facebook)

Quelle: `BDEW_SocialMedia_GESAMT.xlsx`, Sheet *Alle Ergebnisse* (2078 Zeilen).
Erzeugt mit [`_generate.py`](_generate.py) — Schritt 1 (Tracking-Sources einpflegen).
Schritt 2 (Query) folgt separat.

## Format (laut Brandwatch-Doku, Kap. 13.2 / „Connecting Channels")

Das Tracking-Backend akzeptiert beim Anlegen von Content Sources
*„Page URLs, usernames, **or** Page IDs, separated by a comma or space"*.
Pro Zeile genau ein Identifier, ein-spaltige CSV, max. 100 Einträge/Datei:

| Kanal | Wert je Zeile | Beispiel |
|---|---|---|
| **Instagram** | Username-Slug (lowercase) | `50hertz` |
| **Facebook** | Vanity-Username, sonst numerische Page-ID | `50HertzTransmission` / `165991243426082` |

Bei Facebook liegt der Großteil als Vanity-Username vor; eine numerische
Page-ID wird nur dort verwendet, wo die URL eine enthält
(`profile.php?id=`, `/pages/…/ID`, `/people/…/ID`, angehängte `-ID`).

## Inhalt

- `instagram/` — `instagram_handles_1..9.csv` (802 unique) + `instagram_alle.csv`
- `facebook/`  — `facebook_handles_1..10.csv` (921 unique) + `facebook_alle.csv`
- `_uebersprungen.csv` — 18 nicht eindeutig zuordenbare Links
  (Post-/Reel-/Story-/Bild-Links, Login-Wall ohne Handle, leere Zellen)

Duplikate sind case-insensitive entfernt, Reihenfolge entspricht der Excel.

## Reproduzieren

```bash
source ../query_venv/bin/activate
python3 _generate.py
```

## Hinweis Tracked-Sources-Limit

Brandwatch erlaubt max. **1.000 Tracked Content Sources** pro Account
(FB + IG + IG-Hashtags + LinkedIn zusammen). 802 IG + 921 FB = 1.723 —
ggf. auf zwei Accounts/Projekte aufteilen oder priorisieren.
