# Datenquellen

Dieses Projekt erzeugt Brandwatch-Queries aus **drei Quelldateien** (ein Excel,
zwei CSVs), die im Ordner [`data/`](../data/) liegen. Diese Datei beschreibt,
**welche Daten in welcher Datei liegen** und welche Felder die Pipeline daraus
verwendet.

Verwandte Wiki-Seiten:

- [Whats_this.md](Whats_this.md) — Projektüberblick, Ordnerstruktur, Setup.
- [script_descriptions.md](script_descriptions.md) — was macht welches Notebook mit diesen Daten.
- [brandwatch_query_syntax.md](brandwatch_query_syntax.md) — Syntax der erzeugten Queries.

## Überblick

| Datei | Format | Zeilen | Inhalt |
|---|---|---|---|
| [`data/dboes.csv`](../data/dboes.csv) | CSV | ~7.700 | DBoeS-Datenbank: deutsche öffentliche Sprecher — Medien, Journalisten, Parteigliederungen, Politiker, Behörden |
| [`data/adresspaket_pk.xlsx`](../data/adresspaket_pk.xlsx) | Excel | 630 | Adresspaket Bundestagsabgeordnete (MdB) mit Partei und Social-Media-Handles |
| [`data/stiftungen.csv`](../data/stiftungen.csv) | CSV | 13 | Parteinahe und unabhängige politische Stiftungen |
| [`data/Facebook_ranked.csv`](../data/Facebook_ranked.csv) | CSV | — | Externe Rank-Liste (Facebook-Reichweite) — wird von [Notebook 01](../scripts/01_build_accounts.ipynb) zum Anreichern von `accounts.csv` genutzt |
| [`data/Instagram_ranked.csv`](../data/Instagram_ranked.csv) | CSV | — | Externe Rank-Liste (Instagram-Reichweite) — dito |
| `data/accounts.csv` | CSV | — | **Zwischenergebnis** aus [Notebook 01](../scripts/01_build_accounts.ipynb) — nicht selbst pflegen, wird generiert. Single Source of Truth für alle Query-Notebooks (03–09) |

---

## 1. `dboes.csv` — DBoeS-Datenbank

**Herkunft:** [Leibniz-HBI DBoeS-data](https://github.com/Leibniz-HBI/DBoeS-data) — Datenbank öffentlicher Sprecher.

**Genutzt von:** [`01_build_accounts.ipynb`](../scripts/01_build_accounts.ipynb).

### Spalten (wichtigste)

| Spalte | Inhalt |
|---|---|
| `Name` | Name des Akteurs (z. B. „Aachener Zeitung", „Tagesschau") |
| `Typ` | Numerischer Typ-Code — siehe Tabelle unten |
| `SM_XURL` | X/Twitter-URL |
| `SM_FacebookURL` | Facebook-URL |
| `SM_InstagramURL` | Instagram-URL |
| `SM_TikTokURL` | TikTok-URL (aktuell nicht genutzt) |
| `T_Partei` | Parteizugehörigkeit (für Typ 9 Parteigliederungen und Typ 21 Politiker) |
| `Kategorie` | Numerische High-Level-Gruppierung (1 = News, 2 = Organisationen, 3 = Personen) |

Daneben existieren noch Metadaten: `KomplettID`, `ListenID_24_12`, `SM_XID`, `SM_FacebookID`, `K_Geschlecht`, `T_Abgeordneter`, `T_Domaene_Behoerde`, `K_Ursprungsgattung`, `K_Finanzierung`, `T_Mitglied_in_BPK`.

### Typ-Codes

| Typ | Bedeutung | Nutzung in Pipeline |
|---:|---|---|
| 1 | Zeitung (Tages-/Wochenzeitungen) | ✅ genutzt (→ `category=News`, `label=Zeitung`) |
| 3 | Rundfunksender (TV/Radio) | ✅ genutzt (→ `category=News`, `label=Rundfunksender`) |
| 4 | Nachrichtenprogramm (Tagesschau, heute …) | ✅ genutzt (→ `category=News`, `label=Nachrichtenprogramm`) |
| 5 | Entertainmentprogramm | ✅ genutzt (→ `category=News`, `label=Entertainment`) |
| 6 | Online_Only (reine Online-Medien) | ✅ genutzt (→ `category=News`, `label=Online_Only`) |
| 7 | Nachrichtenagentur (dpa, Reuters …) | ✅ genutzt (→ `category=News`, `label=Nachrichtenagentur`) |
| 9 | Parteigliederung (Landes-/Kreisverbände) | ✅ genutzt (→ `category=Organisation`, `label=<Partei>`) |
| 15 | Behörde | ✅ genutzt (→ `category=Organisation`, `label=Behörde`) |
| 20 | Journalist | ✅ genutzt (→ `category=News`, `label=Journalist`) |
| 21 | Politiker | ✅ genutzt, aber **nur wenn nicht schon im Adresspaket** (→ `category=Politician`) |

### Verteilung (aktueller Stand)

| Typ | Anzahl |
|---:|---:|
| 1 — Zeitung | 590 |
| 3 — Rundfunksender | 758 |
| 4 — Nachrichtenprogramm | 105 |
| 5 — Entertainment | 854 |
| 6 — Online_Only | 317 |
| 7 — Nachrichtenagentur | 12 |
| 9 — Parteigliederung | 371 |
| 15 — Behörde | 378 |
| 20 — Journalist | 1.551 |
| 21 — Politiker | 2.807 |
| **gesamt** | **7.743** |

---

## 2. `adresspaket_pk.xlsx` — MdB-Adresspaket

Liste der 630 Bundestagsabgeordneten (Parlamentskreis) mit Partei und
Social-Media-Accounts.

**Genutzt von:** [`01_build_accounts.ipynb`](../scripts/01_build_accounts.ipynb).

### Genutzte Spalten

| Spalte | Inhalt |
|---|---|
| `VORNAME`, `NACHNAME` | Name des MdB |
| `PARTEI` | Partei (z. B. „CDU", „Bündnis 90/Die Grünen", „DIE LINKE") |
| `TWITTER` | X/Twitter-URL |
| `Instagram` | Instagram-URL |
| `FACEBOOK` | Facebook-URL |
| `TikTok` | TikTok-URL |
| `Youtube` | YouTube-URL |

MdBs bekommen `category=MdB`. Dublettencheck: wenn ein Typ-21-Politiker aus
`dboes.csv` denselben Handle wie ein MdB hat, wird der dboes-Eintrag
übersprungen — ein Account erscheint also immer nur einmal.

---

## 3. `stiftungen.csv` — Politische Stiftungen

13 parteinahe und unabhängige politische Stiftungen (KAS, FES, HSS, FNF, HBS,
RLS, …).

**Genutzt von:** [`01_build_accounts.ipynb`](../scripts/01_build_accounts.ipynb).

### Spalten

| Spalte | Inhalt |
|---|---|
| `Stiftung` | Voller Name (z. B. „Konrad-Adenauer-Stiftung (KAS)") |
| `Partei` | Nahestehende Partei (CDU, SPD, …) oder „unabhängig" |
| `Instagram_Handle`, `Instagram_URL` | Instagram-Account |
| `Facebook_Handle`, `Facebook_URL` | Facebook-Page |
| `X_Twitter_Handle`, `X_Twitter_URL` | X/Twitter-Account |

Stiftungen bekommen `category=Stiftung`, `label=<Partei>`.

---

## 4. `Facebook_ranked.csv` und `Instagram_ranked.csv` — Rank-Listen

Externe Rankings, die Facebook-Pages und Instagram-Accounts nach Reichweite
sortieren. Relevant sind nur zwei Spalten:

| Spalte | Inhalt |
|---|---|
| `Rank` | Numerischer Rang (1 = reichweitenstärkster) |
| `Account Handle` | Handle / Slug — zum Matching gegen `accounts.handle` |

Bei Facebook nutzt [Notebook 01](../scripts/01_build_accounts.ipynb) zusätzlich
noch die URL-Spalte der Rank-Liste, um über die numerische `SM_FacebookID` zu
matchen — viele DBoeS-Einträge haben nur diese ID, keinen lesbaren Slug.

Der Rank wandert als Spalte `rank` nach `accounts.csv`. [Notebook 04](../scripts/04_query_politics.ipynb)
nutzt ihn, um die Politik-Query in Rank-Chunks aufzuteilen, sodass man bei
überlangen Queries einfach die schwächsten Accounts abschneiden kann.

---

## 5. `accounts.csv` — Zwischenergebnis (Single Source of Truth)

Wird von [Notebook 01](../scripts/01_build_accounts.ipynb) aus allen obigen
Dateien gebaut. **Alle Query-Notebooks (02–09) lesen ausschließlich diese
Datei** — damit gibt es genau eine Stelle, an der Datenbereinigung und
Kategorisierung stattfindet.

### Schema (Long-Format: eine Zeile pro Account × Kanal)

| Spalte | Inhalt |
|---|---|
| `name` | Klarname des Akteurs (z. B. „Friedrich Merz", „Tagesschau") |
| `channel` | `x`, `facebook`, `instagram`, `tiktok` oder `youtube` |
| `handle` | Normalisierter Handle (ohne `@`, ohne URL-Kram) |
| `url` | Original-URL aus der Quelldatei |
| `category` | `MdB`, `News`, `Organisation`, `Politician` oder `Stiftung` |
| `label` | Feinkategorie — Partei (z. B. `CDU`), Medientyp (z. B. `Zeitung`), `Behörde`, `Journalist`, … |
| `rank` | Numerischer Rank aus den Rank-Listen (nur für `facebook` und `instagram`), sonst leer |

---

## Wer kommt aus welcher Quelle?

| Akteur | Quelle | `category` in `accounts.csv` |
|---|---|---|
| MdB | **nur** `adresspaket_pk.xlsx` | `MdB` |
| Politiker, die keine MdBs sind | `dboes.csv` Typ 21 (mit Dublettencheck gegen MdB) | `Politician` |
| Medien, Journalist:innen | `dboes.csv` Typen 1, 3, 4, 5, 6, 7, 20 | `News` |
| Parteigliederungen | `dboes.csv` Typ 9 | `Organisation` |
| Behörden | `dboes.csv` Typ 15 | `Organisation` (`label=Behörde`) |
| Politische Stiftungen | **nur** `stiftungen.csv` | `Stiftung` |

## Pipeline-Fluss

```
adresspaket_pk.xlsx ─┐
dboes.csv ───────────┤
stiftungen.csv ──────┼──► 01_build_accounts.ipynb ──► data/accounts.csv
Facebook_ranked.csv ─┤                                         │
Instagram_ranked.csv ┘                                         │
                                                               ▼
                                         ┌──── 02_export_csv_uploads.ipynb ──► output/csv_uploads/
                                         │
                                         ├──── 03_query_mdb.ipynb             ──► output/queries/MdB_query.txt
                                         ├──── 04_query_politics.ipynb        ──► output/queries/politics_query.txt
                                         ├──── 05_query_organisations.ipynb   ──► output/queries/organisations_query.txt
                                         ├──── 06_query_journalists.ipynb     ──► output/queries/journalists_query.txt
                                         ├──── 07_query_news.ipynb            ──► output/queries/news_query.txt
                                         ├──── 08_query_behoerden_news.ipynb  ──► output/queries/behoerden_news_query.txt
                                         └──── 09_query_mdb_journalists.ipynb ──► output/queries/mdb_journalists_query.txt
```

Was jedes dieser Notebooks genau tut → [script_descriptions.md](script_descriptions.md).
