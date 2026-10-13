# Executive Summary

## United States Top 50 Playlist Performance and Song Popularity Trend Analysis

### Purpose

This project describes how songs rank and persist in the supplied United States Top 50 playlist data, how chart appearances are distributed among artists, and how rank relates to popularity and available track metadata.

### Dataset and method

The source contains 27,800 rows from May 18, 2024 through November 27, 2025. Ten exact duplicate rows were removed in the analysis copy. The March 1, 2025 snapshot contained 90 remaining rows across 50 ranks after deduplication, so that date was excluded because its ranks conflict. The analysis uses 27,700 chart observations across 554 valid dates. Four dates are missing from the original calendar sequence.

### Key findings

- **Longest observed run:** “Something in the Orange” by Zach Bryan appears on 535 valid chart dates. “Last Night” by Morgan Wallen follows with 491.
- **Artist appearances:** Taylor Swift leads with 2,014 credited chart rows, followed by Zach Bryan with 1,854 and Morgan Wallen with 1,666. The top 10 artist credits make up about 39.6% of valid rows.
- **Popularity and rank:** Mean popularity is 87.7/100. Popularity has a weak negative correlation with rank (r = −0.094); the relationship is descriptive and small.
- **Explicit status:** Average ranks are nearly identical: 25.60 for non-explicit observations and 25.39 for explicit observations.
- **Album type:** Single observations average rank 23.99; album observations 26.10; compilation observations 33.19. Compilation has only 42 observations, so its average is less stable.
- **Duration and release size:** Duration and rank are weakly associated (r = −0.045). Release track count has a weak positive association with rank (r = 0.116) and a weak negative association with supplied popularity (r = −0.18). These results do not indicate cause and effect.

### How to use the dashboard

Use the Overview for filtered KPIs, popularity movement, song rank timelines, and artist appearances. Songs and Artists provide detail views. Compare explores popularity, explicit status, album type, duration, and release size. Data quality explains excluded dates and source limitations. Shared filters let you narrow by date, artist, song, rank, and album type.

### What to verify next

Confirm the source’s chart methodology and refresh cadence, investigate the malformed March 1 snapshot, and document when popularity scores were measured. Until then, treat all results as descriptive. “Days on chart” means observed dates in this file and does not guarantee a continuous run.
