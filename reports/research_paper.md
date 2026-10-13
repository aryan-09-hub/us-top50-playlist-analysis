# United States Top 50 Playlist Performance and Song Popularity Trend Analysis

## Abstract

This project describes chart placement, observed chart longevity, artist appearances, and supplied popularity scores in a United States Top 50 playlist dataset. The source contains 27,800 rows from May 18, 2024 through November 27, 2025. After removing 10 exact duplicate rows and excluding the malformed March 1, 2025 snapshot, the analysis uses 27,700 observations across 554 valid chart dates. Songs with long observed runs include “Something in the Orange” by Zach Bryan (535 dates) and “Last Night” by Morgan Wallen (491 dates). Taylor Swift has the most chart-row appearances (2,014). Popularity and rank have a weak negative correlation (r = −0.094), while average ranks differ little between explicit and non-explicit observations. Results are descriptive; the source does not document its chart methodology or popularity-score timing.

## 1. Problem statement

Playlist charts change over time as songs enter, leave, and move between positions. A reproducible view of these movements can help describe which tracks remain visible, which artists receive the most chart placements, and how chart rank relates to the available track metadata. The project addresses those questions using the supplied dataset without adding predictive models or inventing missing observations.

## 2. Objectives

1. Inspect the source schema, date coverage, missingness, duplicates, and rank integrity.
2. Calculate observed chart days, average rank, best rank, rank volatility, popularity summaries, and artist appearance counts.
3. Explore ranking timelines, longevity, artist performance, popularity versus rank, explicit status, album type, duration, and release track count where fields are available.
4. Make the analysis accessible through a filterable Streamlit dashboard.
5. Document limitations and practical follow-up steps so findings are not overstated.

## 3. Data and methodology

### 3.1 Source and scope

The analysis uses `data/raw/Atlantic_United_States.csv` as supplied. It contains 27,800 rows and 10 fields: `date`, `position`, `song`, `artist`, `popularity`, `duration_ms`, `album_type`, `total_tracks`, `is_explicit`, and `album_cover_url`. The date field is parsed using day-month-year format. The observed source spans May 18, 2024 to November 27, 2025, with 555 distinct dates and four absent calendar dates in the source sequence.

### 3.2 Cleaning and validation

The raw file is preserved. An in-memory analysis copy converts dates and numeric measures to usable types and removes exact duplicate rows. Ten exact duplicates are found. Chart-date integrity is checked after deduplication: a valid date must contain exactly 50 rows and 50 unique positions. March 1, 2025 has 100 source rows; after removing exact duplicates, 90 rows remain across 50 unique positions, leaving 40 extra conflicting rank rows. The date is excluded in full from rank and trend analysis rather than selecting a version by guess. The resulting analysis contains 27,700 rows across 554 dates.

Track identity is the combination of song title and artist credit because titles are not unique. Multi-artist credits remain grouped as written in the source. No rows or metric values are imputed.

### 3.3 KPI definitions

- **Observed days on chart:** number of distinct valid source dates for a song-artist pair.
- **Average rank:** arithmetic mean of observed chart positions; lower values indicate stronger typical placement.
- **Best rank:** minimum observed chart position; position 1 is best.
- **Rank volatility:** sample standard deviation of the track’s observed positions. It describes spread, not direction.
- **Popularity trend:** average supplied popularity score across chart observations on each date.
- **Artist dominance:** chart-row appearances credited to each artist. This measures representation in the provided chart, not audience share or total streams.
- **Association:** Pearson correlation is shown for continuous field comparisons. Correlation is descriptive and does not establish causation.

### 3.4 Exploratory analysis

The dashboard provides shared filters for date, artist, song, rank, and album type. Its views include overview KPIs and rank timelines, song-level history, an artist leaderboard, field comparisons, and a data-quality page. Comparison views cover popularity versus rank, explicit versus non-explicit observations, album types, duration, and total tracks. Analyses are skipped or marked unavailable if their source field is absent.

## 4. Exploratory findings

All values below describe the 27,700 valid chart observations unless otherwise stated.

### 4.1 Chart movement and longevity

“Something in the Orange” by Zach Bryan appears on 535 distinct valid chart dates, the longest observed run in this dataset; its average rank is 26.3 and its best rank is 9. “Last Night” by Morgan Wallen appears on 491 dates and reaches rank 1. “I Remember Everything (feat. Kacey Musgraves)” by Zach Bryan appears on 445 dates, with an average rank of 13.9 and a best rank of 1. “See You Again (feat. Kali Uchis)” by Tyler, The Creator appears on 443 dates.

These counts measure dates observed in the file, not uninterrupted real-world chart presence. The four missing source dates and the excluded March 1 snapshot further limit claims about continuous duration.

### 4.2 Artist performance

Taylor Swift has the most credited chart appearances (2,014), followed by Zach Bryan (1,854), Morgan Wallen (1,666), Sabrina Carpenter (966), and Drake (838). The top 10 artist credits account for approximately 39.6% of the valid chart rows. This share is based on row appearances; it does not assign a fractional credit to each artist on a multi-artist row.

### 4.3 Popularity and rank

Mean supplied popularity is 87.7 on the 0–100 scale. Popularity and chart position have a weak negative correlation (r = −0.094), meaning higher scores are slightly associated with numerically lower, better positions in this sample. The relationship is small and cannot be interpreted as an effect. The source does not identify when the popularity score was recorded or how it was calculated.

### 4.4 Explicit status

Non-explicit observations have an average rank of 25.60; explicit observations average 25.39. The difference is approximately 0.21 rank positions, which is small in this dataset. This descriptive comparison does not control for artist, song age, release type, or other factors.

### 4.5 Album type

Single observations average rank 23.99, album observations 26.10, and compilation observations 33.19. The compilation category contains only 42 valid observations, far fewer than albums (19,672) and singles (7,986), so its mean is comparatively unstable. These group averages are not adjusted for song, artist, or time.

### 4.6 Duration and release size

Track duration has a weak negative correlation with rank (r = −0.045). Release track count has a weak positive correlation with rank (r = 0.116), meaning releases with more tracks are slightly associated with numerically higher positions in the observed rows. Track count has a weak negative correlation with supplied popularity (r = −0.18). These weak associations are not evidence that duration or album size changes chart performance.

## 5. Limitations

- The source owner, collection method, playlist rules, and chart refresh schedule are undocumented.
- Popularity is supplied but its measurement timestamp and methodology are unknown; it may not represent the same moment as each chart date.
- March 1, 2025 has rank conflicts and is excluded, so that date cannot support rank conclusions.
- Four calendar dates are absent from the original source. The chart is therefore not a fully continuous daily record.
- “Days on chart” is a count of observed dates and does not imply uninterrupted presence.
- Artist credits are strings and can contain multiple names; the analysis does not parse or fractionally allocate them.
- Metadata can vary for the same song-artist pair. Popularity, duration, album type, track count, and artwork are treated as recorded observation-level values.
- Chart observations are repeated measurements of songs and are not independent samples. Category comparisons are descriptive, not inferential.
- Correlations and average ranks may conceal differences in song age, genre, artist, release timing, and exposure.

## 6. Recommendations

1. Confirm the playlist source, collection cadence, rank tie rules, and the cause of the March 1 duplicate snapshot before using the analysis for external claims.
2. Confirm when popularity is captured and whether it is a track-level score or a date-specific observation. Label it as source-provided until its definition is known.
3. Preserve the raw source and run the same duplicate and 50-position integrity checks after each refresh. Keep malformed dates visible in the data-quality view.
4. Describe longevity as “observed chart dates” and include date gaps whenever discussing duration.
5. Treat artist appearances and field comparisons as descriptive context. Avoid causal explanations without a suitable design and additional evidence.
6. Extend the project with documented genre or release-date context only if a trusted source becomes available; do not infer these fields from titles.

## 7. Conclusion

The dataset supports a useful descriptive account of chart visibility, song longevity, artist representation, and associations with supplied metadata. Long observed runs are concentrated among several tracks, and a small set of artists accounts for a substantial share of row appearances. Popularity, explicit status, release type, duration, and track count show descriptive patterns, but the source limitations prevent causal interpretation. Resolving the chart-source and popularity definitions would improve the strength of future analysis.

## Reproducibility

Run the Streamlit app from the project environment with `streamlit run app.py`. KPI and filter calculations are in `src/analysis.py`; dataset loading, validation, and chart-date exclusion are in `src/data_cleaning.py`. The raw source remains unchanged.
