# Analytical Methodology Coverage Checklist

Use this checklist to confirm which requested analyses are implemented and what the dataset supports. Items marked **Implemented** are available in the cleaning/analysis code or Streamlit app. Results remain descriptive; no prediction models are used.

## Data ingestion and validation

- [x] Load daily playlist snapshots from the configured CSV path (`src/data_cleaning.py`, `app.py`).
- [x] Validate chart positions against 1–50 and report malformed dates, missing values, and exact duplicates (`validate_dataset`).
- [x] Check duplicate song–artist–date keys; exclude a chart date from analysis when rank coverage or track-date integrity is invalid (`chart_date_quality`, `analysis_ready_data`).
- [x] Normalize leading/trailing and repeated whitespace in song, artist, and album-type fields on a copy. Exact artist case/whitespace variants are standardized to the most frequent source spelling; unverified aliases are not merged.
- [x] Validate available optional values: popularity 0–100, positive duration (maximum one hour), positive whole-number `total_tracks`, known album-type labels, and recognized explicit flags. Invalid optional measures are missing in the analysis copy and reported in validation notes.

## Feature engineering and KPIs

- [x] Observed days on chart = distinct valid observed dates per song–artist pair (`song_kpis`). This does not prove uninterrupted presence.
- [x] Average rank = mean observed position (`song_kpis`).
- [x] Best rank = minimum observed position (`song_kpis`).
- [x] Rank volatility = sample standard deviation of observed positions (`song_kpis`).
- [x] Rank volatility is unavailable for one-observation tracks; a sample standard deviation is not defined for one value.
- [x] Popularity trend = daily mean source score and trailing mean over up to seven observed snapshots (`daily_summary`, Popularity page). This is smoothing, not a forecast.
- [x] Duration minutes = `duration_ms / 60,000` on the cleaned copy. No source fields are overwritten.
- [x] Explicit-content share = explicit chart observations divided by observations with a known explicit flag (`explicit_content_share`, Overview KPI); missing or unrecognized flags are excluded from the denominator.

## Playlist ranking analysis

- [x] Daily rank distribution in five bands: 1–10 through 41–50 (`daily_rank_distribution`, Trends page).
- [x] Rank movement per track between adjacent calendar-day snapshots (`rank_movement`); changes across date gaps are left undefined.
- [x] Full Top 50 entry and exit counts plus song/artist identities and entry/last chart positions between adjacent valid snapshots (`chart_transition_window`; Trends page). Transitions are computed from the complete analysis-ready chart before the selected event-date window is applied, so non-date global filters cannot turn rank crossings or filter changes into playlist entries/exits. Gaps and excluded snapshots are not treated as transitions.
- [x] Fast risers and slow decliners: latest comparable snapshot, threshold of at least 10 rank places (Trends page). The threshold is an explicit display rule, not a statistical classification.

## Song-level performance

- [x] Longest observed chart presence and song rank summaries (`song_kpis`, Songs page).
- [x] Highest mean popularity when the popularity field exists (Songs page).
- [x] Selected song's dated popularity observations and trailing mean over up to seven observed dates (Song explorer). The source popularity timestamp is undocumented, so dates indicate playlist observations rather than verified score capture dates.
- [x] Best-rank versus observed-days comparison (Songs page). The chart uses track-level summaries; gaps in observed history may exist.

## Artist performance

- [x] Unique song credits per credited performer when song is available (`artist_leaderboard`); supported ` & ` collaboration credits are attributed to each named artist.
- [x] Credited chart appearances and distinct observed dates per performer (`artist_leaderboard`). A collaboration row counts once for every named performer, so appearance totals can exceed playlist rows. “Total days” is distinct dates, not summed continuous tenure.
- [x] Artist dominance over time is shown as daily share of eligible chart slots, with multiple artists comparable in one view (`artist_dominance_over_time`, Artists page). Collaboration slots are divided equally among names split on ` & `; the known band name `Earth, Wind & Fire` is preserved. Per-date shares sum to 100% when all chart rows are included.
- [x] Case/whitespace-only artist spelling variants are standardized to the most frequent source spelling in the cleaned copy and used by the leaderboard and dominance view.
- [ ] Artist aliases and genuine spelling variants: **Require a verified alias mapping source**. Names that differ beyond case/whitespace are not guessed or merged.

## Popularity score analytics

- [x] Popularity versus rank correlation and scatterplot when popularity is available (`popularity_rank_summary`, Popularity page).
- [x] Popularity distributions within cumulative Top 10, Top 20, and Top 50 cohorts using box plots with outliers and P10/P25/P50/P75/P90 summaries (`popularity_cohort_distribution`, `popularity_by_rank_cohort`, Popularity page). Cohorts overlap by design; the same observation appears in each applicable group.
- [x] Track-level popularity stability versus rank volatility using per-track sample standard deviations (`popularity_stability_summary`, Popularity page). Correlation is shown only when estimable.
- [ ] Popularity score provenance and timestamp: **Unavailable in supplied fields/documentation**. Treat popularity as a source-provided score; do not claim it is synchronized to the chart date.

## Content attributes

- [x] Explicit versus non-explicit rank summaries and distributions; popularity summary when available (Attributes page), plus explicit observation share among known flags (Overview KPI). This is not unique-song share or listener share.
- [x] Album-type rank comparisons when album type exists (Attributes page), explicitly labeled as release-level type.
- [ ] Single release versus a single track taken from an album: **Not derivable from the supplied fields**. The dataset has no track release-role field; the dashboard states this limitation instead of inferring it from `album_type`.
- [x] Track duration versus rank, and versus popularity when available (Attributes page).
- [x] Release `total_tracks` versus popularity and rank (Attributes page).

## Project outputs and verification

- [x] Interactive date, artist, song, rank, and album-type filters apply across analysis views (`app.py`).
- [x] Missing optional fields produce unavailable messages or skip dependent views rather than fabricate values.
- [x] Unit tests cover data validation, KPI calculations, filters, transitions, cohort summaries, and edge cases (`tests/`).
- [ ] Refresh this checklist after adding a new source or changing metric definitions.

## Dataset-specific interpretation limits

The currently inspected source has 27,800 raw rows and 10 fields. Exact duplicate rows are dropped in memory. The March 1, 2025 snapshot has conflicting rank rows after exact deduplication and is excluded as a whole; four calendar dates are absent in the source sequence. Analysis is limited to valid snapshots and observed records. The chart source rules, refresh method, and popularity-score definition/timestamp are undocumented. All relationships and category comparisons are descriptive, not causal.
