# Script Descriptions

Dieses Dokument beschreibt **was jedes Notebook tut** — Ziel, Input, Output. Die
Notebooks liegen in [`scripts/`](../scripts/) und sind numerisch in
Ausführungsreihenfolge benannt (`01_…` bis `09_…`).

Gedankliches Modell:

- **Notebook 01** ist die Datenfabrik: es macht aus drei sehr unterschiedlich
  strukturierten Quelldateien eine saubere, einheitliche Tabelle
  (`data/accounts.csv`).
- **Notebooks 02–09** verbrauchen nur noch `accounts.csv`. Sie greifen **nie**
  wieder auf die Rohquellen zu. Dadurch gibt es genau eine Stelle für
  Datenbereinigung und Kategorisierung.

```
┌── 01 ──► accounts.csv ──┬── 02 ──► FB/IG-Upload-CSVs
                          │
                          ├── 03 ──► MdB_query.txt
                          ├── 04 ──► politics_query.txt
                          ├── 05 ──► organisations_query.txt
                          ├── 06 ──► journalists_query.txt
                          ├── 07 ──► news_query.txt
                          ├── 08 ──► behoerden_news_query.txt
                          └── 09 ──► mdb_journalists_query.txt
```

Details zu den Quelldateien → [Datenquellen.md](Datenquellen.md). Details zur
Query-Syntax → [brandwatch_query_syntax.md](brandwatch_query_syntax.md).

---

## 01 — `01_build_accounts.ipynb` — Single Source of Truth bauen

**Ziel.** Aus den drei Rohquellen + zwei Rank-Listen eine einheitliche
Long-Format-Tabelle [`data/accounts.csv`](../data/accounts.csv) bauen. Eine Zeile
pro `(Account, Kanal)`-Kombi. Diese Datei ist die Single Source of Truth für alle
Folge-Notebooks.

**Input:**

- [`data/adresspaket_pk.xlsx`](../data/adresspaket_pk.xlsx) — 630 MdBs mit Handles
- [`data/dboes.csv`](../data/dboes.csv) — ~7.700 öffentliche Sprecher
- [`data/stiftungen.csv`](../data/stiftungen.csv) — 13 Stiftungen
- [`data/Facebook_ranked.csv`](../data/Facebook_ranked.csv) — Reichweiten-Ranking Facebook
- [`data/Instagram_ranked.csv`](../data/Instagram_ranked.csv) — Reichweiten-Ranking Instagram

**Was passiert:**

1. MdBs aus dem Adresspaket einlesen — Kanäle: `x`, `facebook`, `instagram`,
   `tiktok`, `youtube`.
2. DBoeS einlesen und nach `Kategorie` × `Typ` splitten:
   - Kat 1 (News) → `category=News`, `label` aus dem Medien-Typ.
   - Kat 2 (Organisationen) → Typ 9 = Parteigliederung (`label=<Partei>`),
     Typ 15 = Behörde (`label=Behörde`).
   - Kat 3 (Personen) → Typ 20 = Journalist:in (`category=News`,
     `label=Journalist`); Typ 21 = Politiker:in (mit Dublettencheck gegen
     MdB — schon vorhandene Handles werden übersprungen).
3. Stiftungen einlesen → `category=Stiftung`, `label=<Partei>`.
4. Alle Teildatensätze konkatenieren, Zeilen ohne Handle droppen.
5. Rank-Listen matchen — pro FB/IG-Zeile wird ein numerischer `rank` ergänzt
   (fehlt → leer). Facebook-Matching läuft sowohl über den Slug als auch über
   die numerische FB-ID aus der URL, damit DBoeS-Einträge ohne sprechenden Slug
   trotzdem gematcht werden.
6. Sanity-Checks (Kategorien, Channels, Labels).

**Output:**

- [`data/accounts.csv`](../data/accounts.csv) — Schema: `name, channel, handle, url, category, label, rank`.

---

## 02 — `02_export_csv_uploads.ipynb` — FB/IG-Upload-CSVs exportieren

**Ziel.** CSV-Dateien im Brandwatch-Content-Source-Upload-Format erzeugen
(**eine Spalte, kein Header, ein Handle pro Zeile**) — damit kann Brandwatch die
Facebook-Pages und Instagram-Accounts direkt in eine Sammlung aufnehmen.

**Input:**

- [`data/accounts.csv`](../data/accounts.csv)

**Was passiert:**

1. Facebook-Handles aus `accounts.csv` filtern (`channel == "facebook"`),
   deduplizieren, alphabetisch sortieren → `output/csv_uploads/facebook_alle.csv`.
2. Zusätzlich in 100er-Blöcke aufteilen (Brandwatch akzeptiert Uploads mit
   max. 100 Einträgen pro Datei) → `facebook_handles_1.csv`, `…_2.csv`, … `…_N.csv`.
3. Gleiches Spiel für Instagram → `instagram_alle.csv` + `instagram_handles_1..N.csv`.

**Output:**

- [`output/csv_uploads/facebook_alle.csv`](../output/csv_uploads/) — alle FB-Handles in einer Datei
- [`output/csv_uploads/instagram_alle.csv`](../output/csv_uploads/) — alle IG-Handles in einer Datei
- `output/csv_uploads/facebook_handles_{1..N}.csv` — FB in 100er-Blöcken
- `output/csv_uploads/instagram_handles_{1..N}.csv` — IG in 100er-Blöcken

---

## 03 — `03_query_mdb.ipynb` — MdB-Query

**Ziel.** Eine einzige Brandwatch-Saved-Search, die Posts aller 630
Bundestagsabgeordneten auf X, Instagram und Facebook sammelt.

**Input:**

- [`data/accounts.csv`](../data/accounts.csv), gefiltert auf `category == "MdB"` und `channel ∈ {x, instagram, facebook}`.

**Was passiert:**

1. MdB-Zeilen laden, deduplizieren.
2. Query-Struktur: oberste Ebene ist `language:de AND (…)`. Darunter drei
   Plattform-Blöcke (X → Instagram → Facebook), und innerhalb jedes
   Plattform-Blocks ein OR-Sub-Block pro Partei (alphabetisch: AfD, CDU, CSU,
   Grüne, Linke, SPD, Sonstige Parteien).
3. Handles werden als `author:"handle"` geschrieben. `<<< … >>>`-Kommentare
   strukturieren die Query ohne das Matching zu beeinflussen (siehe
   [brandwatch_query_syntax.md](brandwatch_query_syntax.md) §9).

**Output:**

- [`output/queries/MdB_query.txt`](../output/queries/MdB_query.txt)

---

## 04 — `04_query_politics.ipynb` — Politik-Query (mit Rank-Chunks)

**Ziel.** Eine Brandwatch-Query für **Politiker:innen (nicht MdB) + parteinahe
Organisationen** — mit eingebauter Möglichkeit, die Query bei
Längenüberschreitung am Ende abzuschneiden.

**Input:**

- [`data/accounts.csv`](../data/accounts.csv), gefiltert auf:
  - `channel ∈ {x, instagram, facebook}`
  - `category ∈ {Politician, Organisation}`
  - `label != "Behörde"` (Behörden gehören nicht in die Politik-Query)

**Was passiert:**

1. Drei Plattform-Blöcke werden gebaut:
   - **X** — ein einziger OR-Block (X-Accounts haben keine Ranks).
   - **Facebook** — ein Block für Accounts *ohne Ranking* (also die weniger
     reichweitenstarken, die nicht im Ranking stehen), darunter **10
     Rank-Chunks** in aufsteigender Rank-Reihenfolge. Chunkbreite
     = `ceil(max_rank / 10)`.
   - **Instagram** — gleiche Struktur wie Facebook.
2. Die Blöcke werden mit `OR` zusammengefügt, eingebettet in
   `language:de AND (…)`.
3. Warum die Rank-Chunks? Brandwatch hat ein **100k-Zeichen-Limit pro Query**
   (siehe [brandwatch_query_syntax.md](brandwatch_query_syntax.md) §14). Bei
   tausenden Handles kann die Query zu lang werden. Dadurch, dass die
   schwächsten Ranks (und „ohne Ranking") zuletzt stehen, kann man einfach die
   letzten Blöcke aus der TXT-Datei löschen, ohne die reichweitenstarken
   Accounts zu verlieren.

**Output:**

- [`output/queries/politics_query.txt`](../output/queries/politics_query.txt) —
  am Ende des Notebooks wird eine Block-für-Block-Größentabelle gedruckt, aus
  der hervorgeht, ab welchem Block das 100k-Limit gerissen wird.

---

## 05 — `05_query_organisations.ipynb` — Organisationen ohne Parteien

**Ziel.** Eine Brandwatch-Query für alle **Organisationen, die keine Parteien
sind** — also Behörden, Kirchen, Gewerkschaften, wirtschaftsnahe Verbände usw.

**Input:**

- [`data/accounts.csv`](../data/accounts.csv), gefiltert auf:
  - `category == "Organisation"`
  - `label ∉ {AfD, BSW, CDU, CSU, FDP, Grüne, Linke, SPD, Sonstige Parteien}`
  - `channel ∈ {x, instagram, facebook}`

**Was passiert:**

1. Ein OR-Block **pro `label`** (z. B. `Behörde`, `Evangelische Kirche`, …) —
   Labels alphabetisch, Handles innerhalb des Blocks alphabetisch.
2. Platzsparendes Format: alle Handles eines Blocks auf einer Zeile.
3. Eingebettet in `language:de AND (…)`.

**Output:**

- [`output/queries/organisations_query.txt`](../output/queries/organisations_query.txt)

---

## 06 — `06_query_journalists.ipynb` — Journalist:innen

**Ziel.** Eine Brandwatch-Query für alle Journalist:innen im Datensatz.

**Input:**

- [`data/accounts.csv`](../data/accounts.csv), gefiltert auf:
  - `category == "News"` UND `label == "Journalist"`
  - `channel ∈ {x, instagram, facebook}`

**Was passiert:**

1. Ein OR-Block pro Plattform (Reihenfolge X → Instagram → Facebook), leere
   Plattformen werden übersprungen.
2. Eingebettet in `language:de AND (…)`.

**Output:**

- [`output/queries/journalists_query.txt`](../output/queries/journalists_query.txt)

---

## 07 — `07_query_news.ipynb` — News ohne Journalist:innen

**Ziel.** Eine Brandwatch-Query für alle **News-Einträge außer Journalist:innen**
— also Zeitungen, Rundfunksender, Nachrichtenprogramme, Online-Only,
Nachrichtenagenturen und Entertainment.

**Input:**

- [`data/accounts.csv`](../data/accounts.csv), gefiltert auf:
  - `category == "News"` UND `label != "Journalist"`
  - `channel ∈ {x, instagram, facebook}`

**Was passiert:**

1. Ein OR-Block **pro `label`** (z. B. `Zeitung`, `Rundfunksender`,
   `Online_Only`, …), Labels alphabetisch.
2. Eingebettet in `language:de AND (…)`.
3. Die Query kann bei ~3.300 Handles am 100k-Limit kratzen — das Notebook
   loggt die Größe am Ende.

**Output:**

- [`output/queries/news_query.txt`](../output/queries/news_query.txt)

---

## 08 — `08_query_behoerden_news.ipynb` — Kombi: Behörden + News

**Ziel.** Eine Brandwatch-Query, die die Inhalte aus Notebook 05 (nur Behörden)
und Notebook 07 (News ohne Journalist:innen) per `OR` zusammenführt. Nützlich,
wenn man beide Gruppen in einer einzigen Saved Search beobachten will.

**Input:**

- [`data/accounts.csv`](../data/accounts.csv). Zwei Filterpässe:
  - **Teil A — Behörden:** `category == "Organisation"` UND `label == "Behörde"`.
  - **Teil B — News:** `category == "News"` UND `label != "Journalist"`.
  - Beide: `channel ∈ {x, instagram, facebook}`.

**Was passiert:**

1. Ein Behörden-Block + ein OR-Block pro News-`label` (alphabetisch).
2. Eingebettet in `language:de AND (…)`.

**Output:**

- [`output/queries/behoerden_news_query.txt`](../output/queries/behoerden_news_query.txt)

---

## 09 — `09_query_mdb_journalists.ipynb` — Kombi: MdB + Journalist:innen

**Ziel.** Eine Brandwatch-Query, die MdBs und Journalist:innen in einer Saved
Search bündelt — quasi die „Politik-↔-Presse"-Achse auf einen Blick.

**Input:**

- [`data/accounts.csv`](../data/accounts.csv). Zwei Filterpässe:
  - **Teil A — MdB:** `category == "MdB"`.
  - **Teil B — Journalist:innen:** `category == "News"` UND `label == "Journalist"`.
  - Beide: `channel ∈ {x, instagram, facebook}`.

**Was passiert:**

1. MdB-Blöcke pro Partei (Reihenfolge: AfD, CDU, CSU, Grüne, Linke, SPD,
   Sonstige Parteien), danach ein einzelner Journalist:innen-Block.
2. Eingebettet in `language:de AND (…)`.

**Output:**

- [`output/queries/mdb_journalists_query.txt`](../output/queries/mdb_journalists_query.txt)

---

## Gemeinsame Konventionen der Query-Notebooks (03–09)

Alle Query-Notebooks halten sich an dieselben Regeln — hier einmal zentral:

- **Author-Operator, immer gequotet.** Handles werden als `author:"handle"`
  geschrieben. Quotes auch bei einfachen Slugs, weil Handles Punkte und
  Bindestriche enthalten können (z. B. `spiegel.tv`).
- **Sprachfilter.** Jede Query ist in `language:de AND (…)` eingebettet.
- **Kanäle.** Nur `x`, `instagram`, `facebook`. Kein Websites/URLs, kein
  YouTube, kein TikTok — die liegen zwar teilweise in `accounts.csv`, werden
  aber hier nicht genutzt.
- **Dedup.** Immer nach `(channel, handle)` deduplizieren.
- **Kommentare.** `<<< … >>>` markiert Kommentare, die Brandwatch beim Parsen
  ignoriert (siehe [brandwatch_query_syntax.md](brandwatch_query_syntax.md) §9).
  Sie dienen ausschließlich der Lesbarkeit in der TXT-Datei.
- **Platzsparendes Layout.** Handles eines Blocks stehen auf einer Zeile,
  getrennt mit `OR`. Ein `\n` pro Block. Grund: das 100k-Zeichen-Limit von
  Brandwatch pro Query.
- **Größencheck.** Jedes Query-Notebook druckt am Ende die finale Dateigröße
  und warnt, wenn 100.000 Zeichen überschritten werden.
