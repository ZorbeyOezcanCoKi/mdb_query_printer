# Brandwatch Consumer Intelligence — Query Syntax Reference

Stand: April 2026. Quelle: offizielle Brandwatch-Hilfeseiten (help.brandwatch.com,
social-media-management-help.brandwatch.com, developers.brandwatch.com) sowie offizielle
Brandwatch-Blog-/PR-Artikel. Alle verifizierten Operatoren stammen aus dem Artikel
["Building Advanced Queries in Listen"](https://social-media-management-help.brandwatch.com/hc/en-us/articles/4553865146781-Building-Advanced-Queries-in-Listen)
und verwandten Knowledge-Base-Seiten (siehe Referenzen am Ende).

Diese Referenz gilt fuer **Brandwatch Consumer Intelligence (CI)** – frueher *Brandwatch Analytics /
Consumer Research* – und das eng verwandte Produkt **Brandwatch Listen** (Teil von Social Media
Management). Die Query-Sprache ist zwischen beiden Produkten weitgehend identisch; die Listen-Hilfe
ist oeffentlich einsehbar und wird daher hier als primaere Quelle zitiert. Die Syntax unterscheidet sich
**nicht** von der des damaligen *Crimson Hexagon* / *ForSight* (anderes Produkt, andere Syntax) – dort
ist vieles aehnlich, aber nicht gleich.

> Wichtig: Unsichere Stellen sind explizit als `WARN Unverified` markiert. Diese bitte im
> Produkt-UI des Kunden-Accounts gegenchecken, bevor sie produktiv verwendet werden.

---

## Inhaltsverzeichnis

1. [Grundlagen](#1-grundlagen)
2. [Boolesche Operatoren: AND / OR / NOT](#2-boolesche-operatoren-and--or--not)
3. [Gruppierung, Praezedenz und typische Fehler](#3-gruppierung-praezedenz-und-typische-fehler)
4. [Exakte Phrasen mit Anfuehrungszeichen](#4-exakte-phrasen-mit-anfuehrungszeichen)
5. [Proximity-Operatoren: Tilde, NEAR/x, NEAR/xf](#5-proximity-operatoren-tilde-nearx-nearxf)
6. [Wildcards und Replacement: `*` und `?`](#6-wildcards-und-replacement--und-)
7. [Gross-/Kleinschreibung und `{...}`-Operator](#7-gross-kleinschreibung-und--operator)
8. [Sonderzeichen, Akzente und `raw:`-Operator](#8-sonderzeichen-akzente-und-raw-operator)
9. [Kommentare in Queries `<<< ... >>>`](#9-kommentare-in-queries----)
10. [Source-Operatoren (site, url, title, author, domain, subreddit, channelId, ...)](#10-source-operatoren)
11. [Location-Operatoren (continent, country, region, city, language, latitude, longitude)](#11-location-operatoren)
12. [Autor-/Engagement-/Medien-Operatoren](#12-autor-engagement-medien-operatoren)
13. [Facebook- und Instagram-Autoren / Seiten](#13-facebook-und-instagram-autoren--seiten)
14. [Zeichen- und Performance-Limits](#14-zeichen--und-performance-limits)
15. [Raw Mentions vs. Filtered Mentions](#15-raw-mentions-vs-filtered-mentions)
16. [Common Pitfalls](#16-common-pitfalls)
17. [Referenzen](#17-referenzen)

---

## 1. Grundlagen

- Eine Query ist ein Boolean-Keyword-Search, der Mentions aus Social-Media-Quellen und offenen
  Webseiten zurueckliefert. Brandwatch spricht von ca. **22 Boolean-Operatoren** – aktuell den
  groessten Umfang am Markt (Quelle: Brandwatch-Pressemitteilung).
- Operator-Keywords (`AND`, `OR`, `NOT`, `NEAR/x`) muessen **GROSSGESCHRIEBEN** geschrieben werden.
  Brandwatch formuliert es so: *"Operators require exact capitalization (uppercase)."*
- Die Standardsuche ist **nicht case-sensitive** – ausser, man benutzt den `{...}`-Operator
  (siehe Abschnitt 7). Zitat aus FAQ Listen: *"Search results are not case sensitive unless you use
  the brackets `{}` operator."*
- Leerzeichen zwischen Operator und Term sind Pflicht (`apple AND juice`, nicht `appleANDjuice`).
- Metadaten-/Feld-Operatoren wie `site:`, `author:`, `language:` werden **klein** geschrieben,
  **direkt** gefolgt von `:` und dem Wert ohne Leerzeichen: `site:bbc.com`.

---

## 2. Boolesche Operatoren: AND / OR / NOT

| Operator | Bedeutung | Beispiel |
|---|---|---|
| `AND` | beide Begriffe muessen im Mention vorkommen | `"apple juice" AND straw` |
| `OR` | mindestens einer der Begriffe muss vorkommen | `"apple juice" OR "orange juice"` |
| `NOT` | der folgende Begriff darf **nicht** vorkommen | `apple NOT juice` |

Hinweise:

- `NOT` wirkt immer auf den **unmittelbar folgenden** Term bzw. die folgende Klammergruppe.
- `NOT` darf vor Source-Operatoren wie `site:`, `title:`, `author:` stehen. Es funktioniert
  laut Brandwatch-Doku **nicht** in Kombination mit `url:`.
- `NOT` ganz am Anfang der Query erzeugt in der Regel einen Fehler – man braucht mindestens einen
  positiven Ausdruck davor, z. B. `* NOT spam` ist nicht zulaessig, stattdessen `(apple OR pear) NOT spam`.

---

## 3. Gruppierung, Praezedenz und typische Fehler

Mit Klammern `(...)` werden Begriffe gruppiert:

```
(apple AND juice) OR (orange AND juice)
Dominos AND (pizza OR takeaway)
Apple AND (mac OR iphone)
Airpods NOT (offer OR discount)
```

Empfohlene Praxis laut Brandwatch:

- **Immer explizit klammern**, auch wenn man auf die Praezedenz vertraut.
- Praezedenz (de facto, mehrfach in der Doku implizit): `NOT` > `AND` > `OR`.
  Deshalb wird *ohne Klammer* `a OR b AND c` als `a OR (b AND c)` interpretiert – eine haeufige
  Fehlerquelle, die Brandwatch explizit nennt.
- Alle Klammern **muessen geschlossen** sein – unmatched parentheses sind der haeufigste Query-Fehler
  ("Unclosed or mismatched brackets").

---

## 4. Exakte Phrasen mit Anfuehrungszeichen

Zitat: *"Quotations `" "` — Mentions will include the phrase as written in the quotations."*

```text
"apple juice"
"customer service"
"mercedes benz"
```

- Phrasen in `"..."` matchen genau diese Wortfolge.
- Bindestriche, Apostrophes und Punkte innerhalb der Phrase werden **wie Whitespace** behandelt
  (d. h. `"it's"` matcht auch `it s`) – wer auf der Punktuation bestehen muss, braucht `raw:`
  (Abschnitt 8).
- Phrasen koennen mit `~n` zu einer Proximity-Phrase erweitert werden: `"apple juice"~5` (Abschnitt 5).

---

## 5. Proximity-Operatoren: Tilde, NEAR/x, NEAR/xf

Brandwatch unterscheidet drei Proximity-Schreibweisen:

| Schreibweise | Verhalten | Beispiel |
|---|---|---|
| `"... ..."~n` | alle Woerter der Phrase innerhalb von `n` Woertern voneinander | `"apple juice"~5` |
| `A NEAR/n B` | beide Terme innerhalb von `n` Woertern, **Reihenfolge egal** | `Falcon NEAR/5 Brandwatch` |
| `A NEAR/nf B` | `A` muss **vor** `B` stehen, innerhalb von `n` Woertern | `Falcon NEAR/5f Brandwatch` |

Weitere Regeln / Empfehlungen aus den Docs:

- `NEAR/x` steht laut Listen-Doku nur in **Saved Searches / Advanced Queries** zur Verfuegung
  (nicht in allen Quick-Search-Eingaben).
- Empfehlung von Brandwatch: *"Setting the NEAR operator between 10 and 15 can be a good starting point."*
  Die Zahl `n` wird dabei grob an der durchschnittlichen Satzlaenge orientiert.
- Die Operatoren koennen auch auf Gruppen angewendet werden:
  `(pizza OR pasta) NEAR/10 (Dominos OR "Pizza Hut")`.
- `~n` und `NEAR/n` sind semantisch aehnlich; `NEAR/n` ist allerdings flexibler, weil beide Seiten
  selbst wieder Ausdruecke/Gruppen sein koennen, waehrend `~n` an `"..."` gebunden ist.

---

## 6. Wildcards und Replacement: `*` und `?`

| Operator | Bedeutung | Beispiel |
|---|---|---|
| `*` (Wildcard) | ersetzt 0..n Zeichen am Wortende (und laut Doku auch als Infix zugelassen) | `complain*` -> complain, complaint, complaints, complaining |
| `?` (Replacement) | ersetzt **genau ein** Zeichen | `Licen?e` -> license, licence |

Einschraenkungen (aus der offiziellen Brandwatch-Doku):

- Der Stamm vor `*` bzw. `?` **muss mindestens 2 weitere Zeichen** enthalten. Zitat:
  *"The term must have at least 2 other characters to allow usage of the wildcard operator."*
- `?` darf **nicht am Anfang** eines Terms stehen: *"The replacement operator cannot be used at
  the beginning of a term, but can be used anywhere in the middle or at the end of a term."*
- Fuer sehr kurze Wildcards (2-Zeichen-Stamm) gilt ein **Limit von 150 expandierten Varianten**:
  *"There is a limit of 150 on short wildcards (2 characters)."* Wird das Limit ueberschritten,
  verweigert Brandwatch die Query.
- Wildcards werden nicht auf Phrasen innerhalb `"..."` angewandt (Literal-Matching).

Praxis-Tipps:

- Statt `*foo*` (Prefix-Wildcard) lieber explizite Formen aufzaehlen: `(foo OR foobar OR xfoo)`.
  Praefix-Wildcards gehen performance-technisch oft nicht.
- Fuer Umlaut/Nicht-Umlaut-Varianten: `Muenchen OR München` oder mit `?`: `M?nchen`
  (trifft auch `Munchen`).

---

## 7. Gross-/Kleinschreibung und `{...}`-Operator

- Standard-Matching ist **case-insensitive**.
- Mit `{...}` erzwingt man Case-Sensitivity. Beispiel aus der Brandwatch-Doku:
  `{AC/DC}` -> matcht *AC/DC*, aber **nicht** *ac/dc* oder *Ac/Dc*.
- Einschraenkung (verifiziert in der Listen-Doku): *"terms must be less than 5 characters"* – d. h.
  `{...}` ist nur fuer **Terme unter 5 Zeichen** erlaubt. Laengere Begriffe muss man via `raw:` case-
  sensitive matchen (siehe Abschnitt 8).
- Operator-Keywords wie `AND/OR/NOT` muessen unabhaengig davon grossgeschrieben werden.

---

## 8. Sonderzeichen, Akzente und `raw:`-Operator

Standardmaessig werden **nicht-alphanumerische Zeichen** (Punkte, Plus, Slash, Hashes etc.) im Query
wie Whitespace behandelt. Der Mention-Index ist ebenfalls so tokenisiert. Um solche Zeichen *buchstaeblich*
zu suchen (und optional case-sensitive), verwendet man den `raw:`-Operator.

```text
raw:Google+
raw:(Google+ OR google+ OR "Google +" OR "google +")
```

Regeln:

- `raw:` klein, direkt gefolgt von `:`, ohne Leerzeichen.
- `raw:` ist **case-sensitive** auf Wunsch: man schreibt den Term genau so, wie er gematcht werden soll.
- Mehrere `raw:`-Varianten in Klammern zusammenfassen.
- **Einschraenkung:** `raw:` ist *nicht* kompatibel mit asiatischen Sprachen (CJK).

Akzente:

- Mit Akzent geschrieben (z. B. `niño`) matcht Brandwatch in der Regel nur die akzentuierte Variante.
  Ohne Akzent (`nino`) werden beide Formen gefunden.
- Fuer gezielte Varianten: `(niño OR nino)`.

---

## 9. Kommentare in Queries `<<< ... >>>`

Verifiziert aus der offiziellen Listen-Doku:

> *"Angle Brackets `<<<  >>>`: Information contained inside six angle brackets will not be considered
> part of your search."*

Syntax:

```text
<<< Das ist ein Kommentar und wird ignoriert. >>>
```

Regeln und Details:

- Kommentare werden durch **drei** oeffnende (`<<<`) und **drei** schliessende (`>>>`) spitze
  Klammern eingeschlossen. Das ergibt zusammen "six angle brackets".
- Alles zwischen `<<<` und `>>>` wird vom Query-Parser ignoriert – auch Operatoren, die dort stehen.
- Kommentare koennen **mehrzeilig** sein (wichtig fuer lange, strukturierte Saved Searches).
- Kommentare koennen an beliebigen Stellen zwischen Tokens stehen – sie sollten aber **nicht
  mitten in einem Token / einer Phrase** platziert werden (also nicht innerhalb `"..."`).
- Typische Verwendung laut Brandwatch: *"Use notes with `<<<>>>` to structure complex queries for
  readability."*
- `<<< ... >>>` ist die einzige offiziell dokumentierte Kommentar-Syntax. `/* ... */` und `# ...`
  werden **nicht** unterstuetzt. Wer in Python/etc. generiert: nur `<<< ... >>>` erzeugen.

Beispiel aus der Praxis:

```text
<<< Brand-Core: offizielle Schreibweisen, Typos und Handles >>>
(
  "Mercedes-Benz" OR Mercedes OR
  <<< haeufige Verschreiber >>>
  (Merce?es OR "Mercedes Bens")
)

<<< Kontext: Auto, damit wir nicht auf Mercedes-die-Person matchen >>>
AND (Auto OR Fahrzeug OR PKW OR Car)

<<< Ausschluesse: Spiele, Personen, Musik >>>
NOT (GTA OR Rapper OR "Mercedes Sosa")
```

---

## 10. Source-Operatoren

Alle in der Listen-Doku aufgelisteten Source-Operatoren. Syntax immer `name:wert` **ohne** Leerzeichen.
Mehrwort-Werte gehen in doppelte Anfuehrungszeichen.

| Operator | Zweck | Beispiel |
|---|---|---|
| `site:` | Mentions von einer Domain. **Ohne** `https://` oder `www.` | `site:bbc.com` |
| `url:` | Mentions von einer bestimmten URL/Pfadpraefix | `url:"bbc.com/news"` |
| `title:` | Term muss im **Titel** der Seite vorkommen | `title:Astrazeneca` |
| `domain:` | wie `site:`, aber als strukturiertes Filterfeld in der API | `domain:bbc.co.uk` |
| `links:` | Mention enthaelt einen Link auf die Domain | `links:falcon.io` |
| `weblogTitle:` | Name des Blogs / weblog | `weblogTitle:falconio` |
| `topLevelDomain:` | TLD-Filter | `topLevelDomain:.com` |
| `author:` | exakter Autoren-Match (Handle / Username) | `author:philrudd` |
| `subreddit:` | Reddit-Subreddit. **Case-sensitive, exakter Name** | `subreddit:Damnthatsinteresting` |
| `channelId:` | interne Brandwatch-Channel-ID (z. B. FB-Page-ID, YT-Channel-ID) | `channelId:141273439246434` |
| `guid:` | eindeutige Mention-ID | `guid:1445054562897911823` |
| `title:` + `NOT` | Ausschluss von Titeln | `NOT title:Werbung` |

Wichtig:

- `author:` matcht **exakt** das Handle / den Username. Also `author:philrudd`, nicht `author:"Phil Rudd"`.
  Fuer Anzeigenamen gibt es (je nach API-Level) zusaetzlich `fullname`/`exactAuthor` als Filterfeld.
- Mehrere Werte immer mit Klammer + `OR`: `author:(MarriottIntl OR Marriott)`.
- `site:` und `url:` schliessen sich praktisch aus – `url:"bbc.com/news"` ist strenger als `site:bbc.com`.
- `channelId:` ist der Schluessel fuer einzelne, *verbundene* FB/IG/LinkedIn/YT-Kanaele (siehe
  Abschnitt 13).

Nur-Source-Queries sind zulaessig: Eine Query darf ausschliesslich aus einem Source-Operator
bestehen (z. B. `url:bbc.com/news`), ohne weitere Keyword-Bedingung. Zitat aus der Doku:
*"It's possible to search using only a Source Operator without the need to add any further keywords
or terms to limit your results."*

---

## 11. Location-Operatoren

| Operator | Werteformat | Beispiel |
|---|---|---|
| `continent:` | Grossbuchstabige Kontinent-Konstante | `continent:EUROPE` |
| `country:` | ISO-3166-alpha-3 (Grossbuchstaben) | `country:GBR` |
| `region:` | `"LAND.Region"` (Land als Praefix, Punkt-getrennt) | `region:"GBR.Northern Ireland"` |
| `city:` | `"LAND.Region.Stadt"` | `city:"GBR.Northern Ireland.Belfast"` |
| `latitude:` + `longitude:` | Range-Syntax `[min TO max]` | `latitude:[41 TO 44] AND longitude:[-73 TO -69]` |
| `language:` | ISO-639-1 (zweistellig, klein) | `language:en`, `language:de` |

Regeln:

- Mehrwortige Regionen/Staedte **immer in `"..."`** (z. B. `region:"GBR.Northern Ireland"`).
- Punkt zwischen Land/Region/Stadt ist **Teil der Syntax**, kein Domain-Punkt.
- Sprachcodes folgen ISO 639 – auf der Brandwatch-Seite wird auf die externe ISO-Liste verwiesen.
- `country:` akzeptiert ueblicherweise **Alpha-3**-Codes (`GBR`, `DEU`, `USA`) – das ist in der
  Listen-Doku beispielhaft genau so belegt.

---

## 12. Autor-/Engagement-/Medien-Operatoren

Verifiziert aus der Listen-Doku:

| Operator | Bedeutung | Beispiel |
|---|---|---|
| `authorGender:` | `F` / `M` / `unisex` (Brandwatch-Inference) | `authorGender:F` |
| `authorVerified:` | `true` / `false` (X/Twitter) | `authorVerified:true` |
| `authorFollowers:` | Range | `authorFollowers:[200-2000]` |
| `engagementType:` | `COMMENT` \| `REPLY` \| `RETWEET` \| `QUOTE` | `engagementType:COMMENT` |
| `engagingWith:` | Replies/Retweets, die mit einem Handle interagieren | `engagingWith:acdc` |
| `engagingWithGuid:` | Interaktionen mit einer bestimmten Post-GUID | `engagingWithGuid:1445054562897911823` |
| `imageType:` | bildbasierte Mentions (`image`) | `imageType:image` |
| `publisherSubType:` | **Nur Instagram**: `IMAGE` oder `VIDEO` | `publisherSubType:IMAGE` |
| `rating:` | Review-Score-Range | `rating:[3 TO 5]` |
| `itemReview:` | Produktname in Reviews | `itemReview:"Ring Doorbell"` |
| `minuteOfDay:` | UTC-Minuten (Range) | `minuteOfDay:[1110 TO 1140]` (18:30–19:00 UTC) |
| `hashtags:` | ohne `#` schreiben, case-insensitive | `hashtags:(epicwin OR epicfail OR epic)` |
| `at_mentions:` | X-Handles, die via `@` erwaehnt werden | `at_mentions:brandwatch` |

Zusaetzlich (aus `/docs/available-filters` der Developer-Docs, gelten als API-Filter, die in der
Boolean-Query zum Teil verwendbar sind – im UI aber teils nur als Filter-Panel):

- `exactAuthor` / `xexactAuthor` (negativ-Form jeweils mit `x`-Praefix)
- `authorGroup` / `xauthorGroup`
- `twitterAuthorId` / `xtwitterAuthorId`
- `facebookAuthorId` / `xfacebookAuthorId`
- `threadAuthor` / `xthreadAuthor`
- `facebookRole` / `xfacebookRole` (`owner` vs. `audience`)
- `facebookSubtype` / `xfacebookSubtype` (`link`, `photo`, `status`, `video`)
- `siteGroup` / `xsiteGroup`
- `sentiment`, `status`, `xstatus`

> `WARN Unverified` – Die `x`-Negations-Varianten (z. B. `xauthor`) und die reinen Feld-Filter
> (`facebookAuthorId`, `twitterAuthorId`) werden offiziell als *Filter* dokumentiert (API-Ebene
> und UI-Seitenleiste). Ob sie 1:1 als Boolean-Operator innerhalb des Query-Strings funktionieren,
> haengt vom Produkt-Build ab. Im **Saved-Search-Query-String** bewaehrt sind `author:`, `site:`,
> `url:`, `title:`, `domain:`, `links:`, `subreddit:`, `channelId:` und die Location-Operatoren.
> Zweifelsfaelle bitte im UI gegenchecken.

---

## 13. Facebook- und Instagram-Autoren / Seiten

Dieser Bereich ist in der offentlichen Brandwatch-Doku **nicht so sauber dokumentiert wie die
Basis-Operatoren**. Hier sind die verifizierten Fakten, klar getrennt von Dingen, die der Kunde im
Produkt-UI verifizieren muss.

### 13.1 Konzept: Channels vs. Queries

Aus der offiziellen Terminologie-Seite:

> *"Channel — A search for all results associated with a specific Twitter handle, Facebook or
> Instagram page."*

Brandwatch unterscheidet also zwischen:

- **Query** – Keyword-/Boolean-Search gegen den kompletten Index.
- **Channel** – ein *verbundener* (authentifizierter oder getrackter) Account, dessen Posts +
  Kommentare in den Index aufgenommen werden.

Fuer FB/IG bedeutet das: Bevor man einen bestimmten Account als *Author* im Query-String sauber
treffen kann, **muss er als Channel bzw. Tracked Content Source angelegt sein**. Zitat aus
"Tracking Content Sources in Listen":

> *"In Listen, it's possible to track a tracked content source for Facebook, Instagram, and
> LinkedIn, such as an owned Facebook Page, an owned Instagram account, an Instagram hashtag,
> or an owned LinkedIn Company Page."*

Ohne Tracking hat Brandwatch zwar **ca. 200.000 oeffentliche FB-Pages** und
**ca. 720.000 oeffentliche IG-Accounts** im Standard-Index ("non-owned public data"), aber die
Tiefe (Kommentare, Tags, Mentions) ist nur fuer *getrackte* Accounts verfuegbar.

### 13.2 Einzelne FB-Page / IG-Account im Query-String: `channelId`

Der offiziell dokumentierte Weg, um Mentions von **einer bestimmten Facebook-Page oder einem
bestimmten Instagram-Account** als Autor anzusprechen, ist der Operator `channelId:` (in der
Listen-Hilfe auch als `channelid` geschrieben – case-insensitive).

> *"To search for mentions on a specific channel, use the `channelid` operator in your search and
> specify your channel ID."* – Listen-Doku, *Creating and Saving Searches*.

Beispiele:

```text
<<< Nur Posts + Kommentare dieser einen Facebook-Page >>>
channelId:141273439246434

<<< Mehrere FB-Pages ODER IG-Accounts kombiniert >>>
channelId:(141273439246434 OR 17841400000000000)

<<< Keyword-Query eingeschraenkt auf zwei getrackte Kanaele >>>
(Mercedes OR "Mercedes-Benz") AND channelId:(141273439246434 OR 17841400000000000)
```

- Die **Channel-ID fuer Facebook-Pages** entspricht der **numerischen Facebook-Page-ID**
  (z. B. 15- bis 17-stellig). Brandwatch verweist fuer das Auffinden auf
  <https://www.facebook.com/help/>.
- Fuer **Instagram** ist die Channel-ID die **numerische IG-Business-/Creator-Account-ID** (aus
  der Graph API). Brandwatch erzeugt sie beim Verbinden des Accounts automatisch. In der
  Social-Media-Management-Oberflaeche findet man sie unter **Channel Admin Settings**.
- Mehrere IDs im Listen-Query-Format entweder via `channelId:(a OR b OR c)` oder durch mehrere
  `channelId:`-Klauseln mit `OR` verbunden.
- Beim Tracken mehrerer Pages/Accounts im UI erlaubt Brandwatch die Eingabe als
  *"Facebook Page URLs, usernames, or Facebook Page IDs separated by a comma or space"*; fuers
  Query-String-Targeting ist aber die numerische ID der zuverlaessige Schluessel.

### 13.3 Beitraege *von* einer Seite vs. *ueber* eine Seite

Wichtig und von Brandwatch explizit hervorgehoben:

- `channelId:<FB_PAGE_ID>` liefert **Mentions, die von genau diesem Channel stammen** (Posts der
  Page + Kommentare unter diesen Posts). Bei *owned* Pages zusaetzlich: *tags and mentions of the
  account* (fuer IG) bzw. *page's posts and ads along with all comments* (fuer FB).
- Wer stattdessen **Erwaehnungen einer Marke** finden will (Posts *ueber* die Marke, egal von wem),
  benutzt Keywords / `at_mentions:` (fuer X) bzw. `hashtags:` und Standard-Text-Matching.

Konkretes Muster:

```text
<<< Was veroeffentlicht MB selbst? >>>
channelId:141273439246434

<<< Was sagen andere ueber MB? >>>
("Mercedes-Benz" OR @MercedesBenz OR hashtags:MercedesBenz)
  NOT channelId:141273439246434
```

### 13.4 `author:` bei FB / IG

- `author:` ist laut Listen-Doku primaer fuer Plattformen relevant, auf denen ein stabiles, eindeutiges
  Handle existiert (X/Twitter, Reddit-User, Blog-Autor). Beispiel: `author:philrudd`.
- Fuer FB/IG funktioniert `author:<pagename>` **nicht zuverlaessig**, weil Brandwatch intern mit
  numerischen IDs arbeitet und Facebook-Page-Usernames nicht garantiert eindeutig sind.
  Brandwatch nennt zwar Beispiele wie `author:(MarriottIntl OR Marriott)` – das funktioniert primaer
  auf X/Twitter, nicht als FB-Page-Filter.
- Empfehlung: Fuer FB / IG **immer `channelId:`** benutzen, nicht `author:`.

> `WARN Unverified` – Ob in einem konkreten Account-Build `author:<fb_username>` als Page-Ziel
> akzeptiert wird, haengt von der Brandwatch-Konfiguration und dem FB-API-Status ab. Wenn
> `channelId:` verfuegbar ist, ist es **immer die robustere Wahl** und sollte bevorzugt werden.

### 13.5 Voraussetzungen / Caveats

- Die Page/das Konto muss als Content Source getrackt (und ggf. authentifiziert) sein, sonst gibt
  es keine Mentions in der Query.
- Brandwatch-Limit: max. **1.000 Tracked Sources** (FB-Pages + IG-Accounts + IG-Hashtags +
  LinkedIn-Pages zusammen).
- Fuer *owned* Accounts bekommt man Posts, Kommentare, Tags, @Mentions. Fuer *non-owned* Accounts
  **nur Posts** (keine Kommentare), was FB und IG gleichermassen trifft.
- Instagram-Public-Pool-Daten fuer neue Queries existieren erst **ab Februar 2025**.
- Historische Daten: Consumer Research kann bis zu **400 Tage** fuer owned/non-owned FB-Pages
  historisch nachziehen.

---

## 14. Zeichen- und Performance-Limits

Verifiziert aus der offiziellen Doku:

- **Quick Searches**: max. **600 Zeichen**.
- **Saved Searches**: max. **100.000 Zeichen**.
- **Import aus Consumer Research -> Listen**: ebenfalls 100.000 Zeichen Limit.
- **Short-Wildcards (`*` nach 2-Zeichen-Stamm)**: max. **150 expandierte Treffer-Terme**.
- Max. **1.000 Tracked Content Sources** pro Account.
- Public-Data-Historie Instagram: Mentions ab **Feb. 2025** (fuer neu angelegte Queries).

Performance-Tipps (aus diversen Brandwatch-Blogposts):

- `NEAR/10..15` statt `AND` fuer kontextuelle Praezision. Reduziert False Positives messbar.
- Lange Keyword-Listen in thematische Gruppen splitten und per `OR` verbinden statt eine einzige
  riesige Disjunktion zu bauen.
- `raw:` sparsam verwenden – es ist teurer als Normal-Matching und nicht CJK-kompatibel.
- Prefix-Wildcards (`*foo`) vermeiden.

---

## 15. Raw Mentions vs. Filtered Mentions

Aus der Developer-Doku:

- **Raw Mentions** (auch *unfiltered*): alle Mentions, die die Query trifft – inkl. Spam, Low-Impact,
  Off-Topic.
- **Filtered Mentions**: nach Anwendung der im UI/via API gesetzten **Filter** (Language, Region,
  Sentiment, Spam-Filter etc.) – kleinere, qualitativ bessere Menge.

Im Query-String selbst macht man inhaltliche Filter ueber Operatoren wie `language:`, `country:`,
`NOT`-Ausdruecke. Saubere Trennung: Query definiert *was matcht*, Filter definiert *was in diesem
Report angezeigt wird*.

---

## 16. Common Pitfalls

Aus der offiziellen Brandwatch-Doku und mehreren offiziellen Blog-Artikeln zusammengefasst:

1. **Operatoren kleinschreiben** (`and`, `or`, `not`). -> Immer `AND`, `OR`, `NOT` in Grossbuchstaben.
2. **Unausgeglichene Klammern**. Laengere Queries *immer* in einem Editor mit Bracket-Matching
   schreiben.
3. **Vergessen zu klammern** bei gemischten `AND`/`OR`:
   - *Falsch:* `Apple OR Orange AND Juice` -> wird zu `Apple OR (Orange AND Juice)`.
   - *Richtig:* `(Apple OR Orange) AND Juice`.
4. **Mehrwort-Phrasen ohne Anfuehrungszeichen**: `Mercedes Benz` matcht *Mercedes* UND *Benz* im
   selben Dokument beliebig weit auseinander. -> `"Mercedes-Benz"` oder `"Mercedes Benz"`.
5. **Sonderzeichen ohne `raw:`**: `Google+` wird wie `Google` behandelt. -> `raw:Google+`.
6. **Prefix-Wildcards**: `*phone` ist zu breit / oft blockiert. -> Suffix-Wildcards oder Aufzaehlung.
7. **Wildcard-Stamm zu kurz**: `a*` ist illegal (min. 2 Zeichen Stamm + mind. 1 weiterer).
8. **`NOT` am Query-Anfang**: Nicht zulaessig; Query braucht mindestens einen positiven Term.
9. **`NOT` mit `url:`**: funktioniert nicht. Stattdessen `NOT site:` oder `NOT domain:` verwenden.
10. **`{...}` fuer lange Begriffe**: Nur fuer Terme < 5 Zeichen. Fuer laengere case-sensitive Matches
    `raw:` verwenden.
11. **FB/IG via `author:`**: unzuverlaessig; stattdessen `channelId:` nutzen und Account vorher als
    Content Source tracken.
12. **Kommentare innerhalb Phrasen**: `"Mercedes <<< comment >>> Benz"` zerstoert den Phrase-Match.
    Kommentare **zwischen** Tokens platzieren.
13. **Query > 100k Zeichen**: wird vom Save-Workflow abgelehnt. Zerlegen.
14. **Channel nicht getrackt**: `channelId:<ID>` liefert 0 Ergebnisse, wenn die Page nicht als
    Content Source verbunden ist.
15. **Zu viele Tracked Sources**: harte Grenze von 1.000.
16. **Akzente**: `niño` und `nino` sind unterschiedlich indiziert. Wenn beide gewuenscht: explizit
    `(niño OR nino)`.

---

## 17. Referenzen

Primaer genutzt:

- [Building Advanced Queries in Listen – Brandwatch Social Media Management Help Center](https://social-media-management-help.brandwatch.com/hc/en-us/articles/4553865146781-Building-Advanced-Queries-in-Listen)
- [Building Advanced Queries in Listen (neue URL-Form)](https://social-media-management-help.brandwatch.com/en/articles/12767966-building-advanced-queries-in-listen)
- [Creating and Saving Searches](https://social-media-management-help.brandwatch.com/hc/en-us/articles/4553852217245-Creating-and-Saving-Searches)
- [Creating and Saving Searches (neue URL-Form)](https://social-media-management-help.brandwatch.com/en/articles/12767965-creating-and-saving-searches)
- [Tracking Content Sources in Listen](https://social-media-management-help.brandwatch.com/hc/en-us/articles/4556879622301-Tracking-Content-Sources-in-Listen)
- [Tracking Content Sources in Listen (neue URL-Form)](https://social-media-management-help.brandwatch.com/en/articles/12767962-tracking-content-sources-in-listen)
- [Sources for Listen Mentions](https://social-media-management-help.brandwatch.com/hc/en-us/articles/4556945084701-Sources-for-Listen-Mentions)
- [FAQ: Listen](https://social-media-management-help.brandwatch.com/hc/en-us/articles/4556980111645-FAQ-Listen)
- [Connecting Facebook Channels](https://social-media-management-help.brandwatch.com/en/articles/12768084-connecting-facebook-channels)
- [Connecting Instagram Channels](https://social-media-management-help.brandwatch.com/en/articles/12768085-connecting-instagram-channels)
- [Channel Admin Settings](https://social-media-management-help.brandwatch.com/en/articles/12768093-channel-admin-settings)
- [How Social Media Management Partners with Social Networks](https://social-media-management-help.brandwatch.com/hc/en-us/articles/6095510074397-How-Does-Social-Media-Management-Partner-with-Social-Networks)

Brandwatch Developer Docs (API):

- [Queries (API-Overview)](https://developers.brandwatch.com/docs/queries)
- [Creating Queries](https://developers.brandwatch.com/docs/creating-queries)
- [Editing Queries](https://developers.brandwatch.com/docs/editing-queries)
- [Retrieving Queries](https://developers.brandwatch.com/docs/retrieving-queries)
- [Retrieving Mentions](https://developers.brandwatch.com/docs/retrieving-mentions)
- [Mention Metadata Field Definitions](https://developers.brandwatch.com/docs/mention-metadata-field-definitions)
- [Available Filters](https://developers.brandwatch.com/docs/available-filters)
- [Top Authors](https://developers.brandwatch.com/docs/top-authors)
- [Terminology](https://developers.brandwatch.com/docs/terminology)

Brandwatch-Blog und Training (offiziell, aber redaktionell):

- [The Ultimate Guide to Query-building Operators](https://www.brandwatch.com/blog/ultimate-guide-to-query-building-operators/)
- [How to Write a Good Query](https://www.brandwatch.com/blog/how-to-write-a-good-query/)
- [Brandwatch Launches New Boolean Operators for Advanced Query Searching (PR)](https://www.brandwatch.com/press/press-releases/brandwatch-launches-new-boolean-operators-advanced-query-searching/)
- [Introducing Brandwatch's new Query Editor](https://www.brandwatch.com/blog/query-editor/)
- [How to Get the Best Instagram Data Coverage with Brandwatch](https://www.brandwatch.com/blog/best-instagram-coverage/)
- [Boolean Explained: Location Data (Community)](https://community.brandwatch.com/boolean-explained-84/boolean-explained-location-data-457)
- [Brandwatch Academy – Consumer Research Path](https://academy.brandwatch.com/path/consumer-research)
- [Brandwatch Study Guide (PDF)](https://www.brandwatch.com/wp-content/themes/brandwatch/src/other/assets/Brandwatch-For-Students-Study-Guide.pdf)
- [Brandwatch Query Tips v2 (PDF)](https://www.brandwatch.com/wp-content/uploads/2013/08/Brandwatch-Query-Tips-v2.pdf)
- [Master Boolean for Advanced Social Media Monitoring](https://www.brandwatch.com/blog/the-social-media-monitoring-cheat-sheet/)
- [What is Boolean search? – Brandwatch Glossary](https://www.brandwatch.com/social-media-glossary/boolean-search/)

Produkt-Hubs (fuer Kontext, nicht fuer Syntax):

- [Brandwatch Consumer Research – Features](https://www.brandwatch.com/products/consumer-research/features/)
- [Brandwatch Data Networks – Facebook](https://www.brandwatch.com/datanetworks/facebook/)

> Hinweis: Brandwatch migriert seit 2024 Hilfeseiten von `/hc/en-us/articles/<id>-Slug` auf
> `/en/articles/<id>-slug`. Beide URL-Formen liefern identischen Inhalt; die aeltere Form ist
> oft besser von Google indiziert, die neue ist das kanonische Ziel.
