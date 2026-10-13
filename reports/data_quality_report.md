# Data Quality Report

> Update this report after each data refresh. Keep the raw source unchanged.

## Source and scope

- **File:** `data/raw/Atlantic_United_States.csv`
- **Dataset owner/source:** To be confirmed
- **Inspection date:** 2026-10-13
- **Rows / columns:** 27,800 / 10
- **Date coverage:** 2024-05-18 to 2025-11-27 (555 distinct dates)

## Schema and types

| Column | Observed meaning | Observed type | Notes |
|---|---|---|---|
| date | Chart observation date | text, day-month-year | Parse with `%d-%m-%Y` |
| position | Chart rank | integer | Values 1–50 |
| song | Track title | text | Unicode punctuation is preserved as supplied |
| artist | Artist credit | text | Multi-artist credits are combined strings |
| popularity | Popularity score | integer | Values 0–100; measurement date/source undocumented |
| duration_ms | Track duration | integer | Positive values; milliseconds |
| album_type | Album release type | text | album, single, compilation |
| total_tracks | Tracks on release | integer | Positive values |
| is_explicit | Explicit flag | boolean | Both values present |
| album_cover_url | Cover image URL | text | Spotify image host in inspected file |

## Quality findings

- Missing values: none detected in the inspected source.
- Exact duplicate rows: 10. These are dropped from the in-memory analysis copy.
- After exact duplicate removal, 2025-03-01 contains 90 rows covering 50 ranks; 40 rank positions have an extra conflicting row. This date is excluded from ranking analysis.
- Four dates are absent from the otherwise daily date sequence.
- Popularity, duration, album type, and cover URL can vary for a song over time. Treat these as observation-level metadata until source semantics are confirmed.
- Use both `song` and `artist` for track identity. The same title may belong to different artists.

## Cleaning decisions

| Issue | Decision | Rationale / follow-up |
|---|---|---|
| Exact duplicate rows | Remove from the in-memory analysis copy | No information is lost; retain raw source |
| Conflicting rank rows | Preserve in the raw source; exclude the entire malformed date from analysis | Do not infer which rank is correct |
| Unparseable dates | Report and exclude from date analyses | Preserve row in source and surface issue |
| Missing optional analysis fields | Skip affected analysis | Do not fabricate values |

## Limitations and open questions

- Confirm the playlist/chart source and whether each date is a daily snapshot.
- Confirm the meaning and timestamp of popularity scores.
- Confirm how same-day rank conflicts should be resolved, especially 2025-03-01.
- The dashboard contains 27,700 observations across 554 valid chart dates after duplicate removal and excluding 2025-03-01.
- “Days on chart” means distinct observed chart dates, not necessarily consecutive days.

## Refresh checklist

- [ ] Record source, retrieval date, and file name.
- [ ] Compare schema and date coverage with the prior refresh.
- [ ] Check missing values, exact duplicates, key collisions, and range violations.
- [ ] Update findings and cleaning decisions above.
