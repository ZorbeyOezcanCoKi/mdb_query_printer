# Whats this?

**Query Printer** — eine kleine Notebook-Pipeline, die aus drei Rohdateien
(ein Excel, zwei CSVs) Social-Media-Handles extrahiert und daraus fertige
[Brandwatch Consumer Research](https://www.brandwatch.com/products/consumer-research/)-Queries
generiert. Die Queries werden in Brandwatch genutzt, um alle Posts der jeweiligen
Handles zu sammeln und für Social Listening weiterzuverarbeiten.

---

## Was macht das Projekt?

**In einem Satz:** aus 3 Quelldateien → eine kanonische Accounts-Tabelle → mehrere
Brandwatch-Queries + Upload-CSVs.

Der Ablauf in drei Schritten:

1. **Einlesen & Vereinheitlichen** — drei sehr unterschiedlich strukturierte
   Quelldateien (MdB-Adresspaket, DBoeS-Datenbank, Stiftungen-Liste) werden
   geparst, ihre Social-Media-URLs werden zu sauberen Handles normalisiert und
   in eine gemeinsame Long-Format-Tabelle [`data/accounts.csv`](../data/accounts.csv)
   geschrieben (eine Zeile pro Account × Kanal).
2. **Kategorisieren** — jeder Account bekommt eine `category` (MdB, News,
   Organisation, Stiftung, Politician) und ein `label` (Partei, Medientyp,
   „Behörde", „Journalist", …). FB- und IG-Accounts werden zusätzlich mit einem
   `rank` (aus externen Ranking-Listen) angereichert, damit große Queries nach
   Reichweite abgeschnitten werden können.
3. **Queries & Uploads erzeugen** — sieben Notebooks ([03_query_mdb](../scripts/03_query_mdb.ipynb)
   bis [09_query_mdb_journalists](../scripts/09_query_mdb_journalists.ipynb)) bauen
   aus `accounts.csv` fertig copy-paste-bare Brandwatch-Boolean-Queries nach
   [author-Operator-Syntax](brandwatch_query_syntax.md). Notebook 02 exportiert
   zusätzlich CSVs im Brandwatch-Content-Source-Upload-Format (für Facebook und
   Instagram).

Output landet in [`output/queries/`](../output/queries/) (Query-Text zum Einfügen
in Brandwatch Saved Searches) und [`output/csv_uploads/`](../output/csv_uploads/)
(CSVs für den FB/IG-Content-Source-Upload).

---

## Ordnerstruktur

```
query_printer/
├── data/                              # Rohdaten (3 Quellen + 2 Rank-Listen + Zwischenergebnis)
│   ├── adresspaket_pk.xlsx            # Quelle 1: 630 Bundestagsabgeordnete
│   ├── dboes.csv                      # Quelle 2: ~7.700 öffentliche Sprecher (DBoeS)
│   ├── stiftungen.csv                 # Quelle 3: 13 politische Stiftungen
│   ├── Facebook_ranked.csv            # Externe Rank-Liste (Facebook-Reichweite)
│   ├── Instagram_ranked.csv           # Externe Rank-Liste (Instagram-Reichweite)
│   └── accounts.csv                   # Zwischenergebnis (Schritt 1) — Single Source of Truth
│
├── scripts/                           # Jupyter-Notebooks, nummeriert in Ausführungsreihenfolge
│   ├── 01_build_accounts.ipynb        # 3 Quellen → accounts.csv
│   ├── 02_export_csv_uploads.ipynb    # accounts.csv → FB/IG-Upload-CSVs
│   ├── 03_query_mdb.ipynb             # MdB-Query
│   ├── 04_query_politics.ipynb        # Politiker + parteinahe Organisationen (mit Rank-Chunks)
│   ├── 05_query_organisations.ipynb   # Organisationen ohne Parteien (Behörden, Kirchen, …)
│   ├── 06_query_journalists.ipynb     # Journalist:innen
│   ├── 07_query_news.ipynb            # News ohne Journalist:innen
│   ├── 08_query_behoerden_news.ipynb  # Kombi: Behörden + News
│   └── 09_query_mdb_journalists.ipynb # Kombi: MdB + Journalist:innen
│
├── output/
│   ├── queries/                       # Brandwatch-Query-Texte (1 Datei pro Notebook 03–09)
│   │   ├── MdB_query.txt
│   │   ├── politics_query.txt
│   │   ├── organisations_query.txt
│   │   ├── journalists_query.txt
│   │   ├── news_query.txt
│   │   ├── behoerden_news_query.txt
│   │   └── mdb_journalists_query.txt
│   └── csv_uploads/                   # CSVs für Brandwatch Content Source Upload (FB + IG)
│       ├── facebook_alle.csv
│       ├── instagram_alle.csv
│       ├── facebook_handles_1..N.csv  # Facebook in 100er-Blöcken
│       └── instagram_handles_1..N.csv # Instagram in 100er-Blöcken
│
├── wiki/                              # Diese Dokumentation
│   ├── Whats_this.md                  # Du bist hier.
│   ├── Datenquellen.md                # Beschreibung der 3 Rohdatenquellen
│   ├── script_descriptions.md         # Was macht welches Notebook, Input → Output
│   └── brandwatch_query_syntax.md     # Referenz zur Brandwatch-Query-Sprache
│
├── requirements.txt                   # pandas, openpyxl
└── query_venv/                        # Lokales venv (nicht commiten)
```

---

## Setup — das Repo zum Laufen bringen

**Voraussetzungen:** Python 3.10+ und Jupyter (oder VS Code mit Jupyter-Extension).

### 1. Repo klonen und ins Projekt wechseln

```bash
git clone <repo-url> query_printer
cd query_printer
```

### 2. Virtuelles Environment anlegen und Abhängigkeiten installieren

```bash
python -m venv query_venv
source query_venv/bin/activate        # macOS / Linux
# oder: query_venv\Scripts\activate   # Windows
pip install -r requirements.txt
pip install jupyter                   # falls Notebooks direkt ausgeführt werden sollen
```

`requirements.txt` enthält nur `pandas` und `openpyxl` — das ist alles, was die
Notebooks brauchen.

### 3. Rohdaten bereitstellen

Die drei Quelldateien müssen in `data/` liegen:

- `data/adresspaket_pk.xlsx`
- `data/dboes.csv`
- `data/stiftungen.csv`
- `data/Facebook_ranked.csv`
- `data/Instagram_ranked.csv`

Details zu Format und Inhalt → siehe [Datenquellen.md](Datenquellen.md).

### 4. Notebooks der Reihe nach ausführen

Die Notebooks sind mit Präfix `01_…` bis `09_…` durchnummeriert — einfach in
dieser Reihenfolge ausführen.

Reihenfolge:

1. [`01_build_accounts.ipynb`](../scripts/01_build_accounts.ipynb) — baut
   `data/accounts.csv` (Pflicht, alle folgenden Notebooks lesen diese Datei).
2. [`02_export_csv_uploads.ipynb`](../scripts/02_export_csv_uploads.ipynb) —
   schreibt die FB/IG-Upload-CSVs nach `output/csv_uploads/`.
3. [`03_query_mdb.ipynb`](../scripts/03_query_mdb.ipynb) bis
   [`09_query_mdb_journalists.ipynb`](../scripts/09_query_mdb_journalists.ipynb) —
   schreiben je eine Query-Datei nach `output/queries/`. Reihenfolge innerhalb
   03–09 ist egal; jedes Notebook ist unabhängig.

Was welches Notebook macht → siehe [script_descriptions.md](script_descriptions.md).

### 5. Output in Brandwatch nutzen

- **Queries** aus `output/queries/*.txt` → in Brandwatch als *Saved Search*
  einfügen. Syntax-Referenz: [brandwatch_query_syntax.md](brandwatch_query_syntax.md).
- **Upload-CSVs** aus `output/csv_uploads/` → in Brandwatch unter *Content
  Source Upload* hochladen, um Facebook-Pages und Instagram-Accounts manuell
  zur Sammlung hinzuzufügen.

---

## Weiterführende Dokumentation

- [Datenquellen.md](Datenquellen.md) — welche Daten liegen in welcher Quelldatei, welche Felder nutzt die Pipeline.
- [script_descriptions.md](script_descriptions.md) — was macht jedes Notebook, was ist der Input, was der Output.
- [brandwatch_query_syntax.md](brandwatch_query_syntax.md) — Referenz zur Brandwatch-Query-Sprache (Operatoren, Limits, Fallstricke).
