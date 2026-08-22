# Wikidata Lexeme Pronunciation Queries

## Overview

These SPARQL queries are for the **Wikidata Query Service (WDQS)** and focus on **English lexemes** (`wd:Q1860`).

The work covers:
- Counting English lexemes with and without pronunciation audio.
- Retrieving English lexemes that have pronunciation audio.
- Retrieving each lexeme's lemma, gloss, and pronunciation audio.
- Processing lexemes in batches of 100.

---

## 1. Statistics: Lexemes With and Without Pronunciation Audio

This query counts **all English lexemes**. It does not filter by a particular lemma or prefix.

```sparql
SELECT
  (COUNT(DISTINCT ?lexemeId) AS ?totalLexemes)
  (COUNT(DISTINCT ?withAudio) AS ?lexemesWithAudio)
  (COUNT(DISTINCT ?withoutAudio) AS ?lexemesWithoutAudio)
WHERE {
  ?lexemeId dct:language wd:Q1860 ;
            wikibase:lemma ?lemma .

  OPTIONAL {
    ?lexemeId wdt:P443 ?audio .
    BIND(?lexemeId AS ?withAudio)
  }

  OPTIONAL {
    FILTER NOT EXISTS {
      ?lexemeId wdt:P443 ?audio2 .
    }
    BIND(?lexemeId AS ?withoutAudio)
  }
}
```

### Summary

- `wd:Q1860` represents **English**.
- `wdt:P443` is used to find **pronunciation audio**.
- `OPTIONAL` ensures lexemes without audio are still counted.
- `COUNT(DISTINCT ...)` prevents duplicate counting when a lexeme has multiple audio files.

The result contains:

| Column | Meaning |
|---|---|
| `totalLexemes` | Total English lexemes |
| `lexemesWithAudio` | English lexemes with pronunciation audio |
| `lexemesWithoutAudio` | English lexemes without pronunciation audio |

---

## 2. English Lexemes With Audio and Gloss

This query retrieves up to **100 English lexemes that have pronunciation audio**, together with their gloss.

```sparql
SELECT DISTINCT ?lexemeId ?lemma ?gloss ?audio WHERE {
  ?lexemeId dct:language wd:Q1860 ;
            wikibase:lemma ?lemma ;
            wdt:P443 ?audio ;
            ontolex:sense ?sense .

  ?sense skos:definition ?gloss .

  FILTER(LANG(?gloss) = "en")
}
ORDER BY ?lemma
LIMIT 100
```

### Returned fields

| Field | Meaning |
|---|---|
| `lexemeId` | Wikidata Lexeme ID |
| `lemma` | The English word |
| `gloss` | English definition/gloss |
| `audio` | Pronunciation audio URL |

### Important detail

The query uses:

```sparql
wdt:P443 ?audio
```

without `OPTIONAL`, so only lexemes **with pronunciation audio** are returned.

The gloss is obtained through the lexeme's sense:

```sparql
?lexemeId ontolex:sense ?sense .
?sense skos:definition ?gloss .
```

---

## 3. Why the Original Audio Query Was Incorrect

The original pattern was:

```sparql
?audio p:P443
```

This does not correctly retrieve the pronunciation audio value.

For the actual pronunciation audio value, use:

```sparql
?lexemeId wdt:P443 ?audio
```

For example:

```sparql
OPTIONAL {
  ?lexemeId wdt:P443 ?audio .
}
```

Use `OPTIONAL` when you want lexemes **with and without audio**. Omit `OPTIONAL` when you want **only lexemes with audio**.

---

## 4. Batching Results

For the query that retrieves lexemes, use `LIMIT` and `OFFSET` to process results in batches.

First 100:

```sparql
LIMIT 100
```

Second 100:

```sparql
LIMIT 100
OFFSET 100
```

Third 100:

```sparql
LIMIT 100
OFFSET 200
```

This allows an application to process lexemes in groups of 100 rather than retrieving everything at once.

---

## Key Wikidata Properties

| Property | Purpose |
|---|---|
| `wd:Q1860` | English language |
| `dct:language` | Lexeme language |
| `wikibase:lemma` | Lexeme lemma |
| `wdt:P443` | Pronunciation audio |
| `ontolex:sense` | Lexeme senses |
| `skos:definition` | Sense gloss/definition |

## Recommended Approach

For statistics, use the first query to determine the overall coverage of pronunciation audio among English lexemes.

For data collection, use the second query and process the results in batches of 100 using `LIMIT` and `OFFSET`.

When retrieving audio, avoid filtering on a specific lemma prefix unless the task specifically requires it. The earlier `^popu.*` filter was only useful for testing a small subset and is not part of the final all-English queries.
