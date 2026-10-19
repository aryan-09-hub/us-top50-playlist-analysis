"""KPI calculations and small, reusable EDA summaries."""

from __future__ import annotations

from datetime import date, datetime

import pandas as pd


def _require(data: pd.DataFrame, columns: set[str]) -> None:
    missing = columns - set(data.columns)
    if missing:
        raise ValueError(f"Missing columns required for analysis: {', '.join(sorted(missing))}")


def song_kpis(data: pd.DataFrame) -> pd.DataFrame:
    """Calculate track-level rank and, when available, popularity summaries.

    Track identity combines artist and title. Volatility uses sample standard deviation
    standard deviation of observed ranks; lower values indicate steadier ranks.
    """
    _require(data, {"date", "song", "artist", "position"})
    if data.empty:
        return pd.DataFrame(columns=["song", "artist", "days_on_chart", "average_rank", "best_rank", "rank_volatility"])
    aggregations = {
        "days_on_chart": ("date", "nunique"),
        "average_rank": ("position", "mean"),
        "best_rank": ("position", "min"),
        "rank_volatility": ("position", "std"),
    }
    if "popularity" in data:
        aggregations["average_popularity"] = ("popularity", "mean")
        aggregations["popularity_volatility"] = ("popularity", "std")
    if "duration_minutes" in data:
        aggregations["average_duration_minutes"] = ("duration_minutes", "mean")
    result = data.groupby(["song", "artist"], dropna=False).agg(**aggregations).reset_index()
    result["rank_volatility"] = result["rank_volatility"].fillna(0.0)
    if "popularity_volatility" in result:
        result["popularity_volatility"] = result["popularity_volatility"].fillna(0.0)
    return result.sort_values(["days_on_chart", "best_rank"], ascending=[False, True]).reset_index(drop=True)


def artist_leaderboard(data: pd.DataFrame) -> pd.DataFrame:
    """Summarize artist chart appearances and average rank."""
    _require(data, {"artist", "position"})
    aggregations = {
        "chart_appearances": ("position", "size"),
        "average_rank": ("position", "mean"),
        "best_rank": ("position", "min"),
    }
    if "song" in data:
        aggregations["unique_songs"] = ("song", "nunique")
    if "date" in data:
        aggregations["days_present"] = ("date", "nunique")
    return data.groupby("artist", dropna=False).agg(**aggregations).sort_values(
        ["chart_appearances", "best_rank"], ascending=[False, True]
    ).reset_index()


def split_artist_credit(credit: object) -> list[str]:
    """Split a source artist credit into credited performers.

    The source uses `` & `` for collaborations. Preserve the band name
    ``Earth, Wind & Fire`` as one artist while splitting other ampersand groups.
    This is a transparent, dataset-specific parsing rule, not alias matching.
    """
    if pd.isna(credit):
        return []
    band_token = "EARTH_WIND_AND_FIRE"
    text = str(credit).strip().replace("Earth, Wind & Fire", band_token)
    names = [part.strip().replace(band_token, "Earth, Wind & Fire") for part in text.split(" & ")]
    return list(dict.fromkeys(name for name in names if name))


def artist_dominance_over_time(data: pd.DataFrame) -> pd.DataFrame:
    """Measure each credited artist's fractional share of chart slots by date.

    Each chart row contributes one slot, divided equally across artists in a
    collaboration credit. Daily shares sum to 100% when all chart rows are
    included. The denominator is the number of chart rows supplied per date.
    """
    _require(data, {"date", "artist"})
    if data.empty:
        return pd.DataFrame(columns=["date", "artist", "credited_slots", "chart_slots", "share_pct"])

    work = data[["date", "artist"]].dropna(subset=["date", "artist"]).copy()
    work["artists"] = work["artist"].map(split_artist_credit)
    work["credit_count"] = work["artists"].map(len)
    work = work[work["credit_count"] > 0].explode("artists", ignore_index=True)
    work["credited_slots"] = 1 / work["credit_count"]
    daily_slots = data.dropna(subset=["date"]).groupby("date").size().rename("chart_slots")
    result = (
        work.groupby(["date", "artists"], as_index=False)["credited_slots"].sum()
        .rename(columns={"artists": "artist"})
        .merge(daily_slots, on="date", how="left")
    )
    result["share_pct"] = result["credited_slots"] / result["chart_slots"] * 100
    return result.sort_values(["date", "share_pct", "artist"], ascending=[True, False, True]).reset_index(drop=True)


def popularity_rank_summary(data: pd.DataFrame) -> dict[str, float | int | None]:
    """Describe popularity and its correlation with chart position, if available."""
    if "popularity" not in data.columns or "position" not in data.columns:
        return {"rows": 0, "mean_popularity": None, "popularity_rank_correlation": None}
    usable = data[["popularity", "position"]].apply(pd.to_numeric, errors="coerce").dropna()
    corr = usable["popularity"].corr(usable["position"]) if len(usable) >= 2 else None
    return {
        "rows": int(len(usable)),
        "mean_popularity": float(usable["popularity"].mean()) if len(usable) else None,
        "popularity_rank_correlation": float(corr) if pd.notna(corr) else None,
    }


def category_summary(data: pd.DataFrame, category: str, value: str = "position") -> pd.DataFrame:
    """Summarize a category only when both requested fields are present."""
    _require(data, {category, value})
    return (
        data.groupby(category, dropna=False)[value]
        .agg(observations="count", mean="mean", median="median")
        .reset_index()
        .sort_values("observations", ascending=False)
    )


def daily_summary(data: pd.DataFrame) -> pd.DataFrame:
    """Aggregate chart-level activity and a trailing 7-snapshot popularity mean."""
    _require(data, {"date", "position"})
    aggregations = {"chart_entries": ("position", "size"), "average_rank": ("position", "mean")}
    if "popularity" in data.columns:
        aggregations["average_popularity"] = ("popularity", "mean")
    if "song" in data.columns:
        aggregations["unique_songs"] = ("song", "nunique")
    summary = data.groupby("date").agg(**aggregations).reset_index().sort_values("date")
    if "average_popularity" in summary:
        summary["popularity_trend_score"] = summary["average_popularity"].rolling(7, min_periods=1).mean()
    return summary


def rank_movement(data: pd.DataFrame, max_gap_days: int = 1) -> pd.DataFrame:
    """Calculate daily rank changes, leaving gaps across missing dates undefined.

    Negative rank change means a rise (movement toward rank 1); positive means
    a decline. A movement requires consecutive calendar dates by default.
    """
    _require(data, {"date", "song", "artist", "position"})
    result = data.sort_values("date").copy()
    track = result.groupby(["song", "artist"], dropna=False)
    previous_rank = track["position"].shift()
    previous_date = track["date"].shift()
    elapsed_days = (result["date"] - previous_date).dt.days
    result["rank_change"] = (result["position"] - previous_rank).where(elapsed_days <= max_gap_days)
    result["days_since_previous"] = elapsed_days
    return result


def daily_rank_distribution(data: pd.DataFrame) -> pd.DataFrame:
    """Count filtered chart rows in five rank bands for each observed date."""
    _require(data, {"date", "position"})
    labels = ["1–10", "11–20", "21–30", "31–40", "41–50"]
    work = data[["date", "position"]].copy()
    work["rank_band"] = pd.cut(work["position"], bins=[0, 10, 20, 30, 40, 50], labels=labels)
    result = work.groupby(["date", "rank_band"], observed=False).size().rename("observations").reset_index()
    return result.sort_values(["date", "rank_band"]).reset_index(drop=True)


def daily_chart_transitions(data: pd.DataFrame, max_gap_days: int = 1) -> pd.DataFrame:
    """Count new and missing song-artist keys between adjacent snapshots only."""
    _require(data, {"date", "song", "artist"})
    daily = {
        day: set(group[["song", "artist"]].itertuples(index=False, name=None))
        for day, group in data.groupby("date")
    }
    dates = sorted(daily)
    rows = []
    for previous_day, current_day in zip(dates, dates[1:]):
        elapsed = (current_day - previous_day).days
        if elapsed > max_gap_days:
            continue
        previous, current = daily[previous_day], daily[current_day]
        rows.append({
            "date": current_day,
            "entries": len(current - previous),
            "exits": len(previous - current),
            "days_between_snapshots": elapsed,
        })
    return pd.DataFrame(rows, columns=["date", "entries", "exits", "days_between_snapshots"])


def popularity_by_rank_cohort(data: pd.DataFrame) -> pd.DataFrame:
    """Summarize source popularity across cumulative Top 10, Top 20 and Top 50."""
    _require(data, {"position", "popularity"})
    cohorts = [("Top 10", 10), ("Top 20", 20), ("Top 50", 50)]
    rows = []
    for label, ceiling in cohorts:
        values = pd.to_numeric(data.loc[data["position"].between(1, ceiling), "popularity"], errors="coerce").dropna()
        rows.append({
            "cohort": label,
            "observations": int(values.size),
            "mean_popularity": float(values.mean()) if not values.empty else float("nan"),
            "median_popularity": float(values.median()) if not values.empty else float("nan"),
        })
    return pd.DataFrame(rows)


def popularity_stability_summary(data: pd.DataFrame) -> tuple[pd.DataFrame, float | None]:
    """Relate per-track popularity spread to rank volatility descriptively."""
    _require(data, {"date", "song", "artist", "position", "popularity"})
    tracks = song_kpis(data)
    if "popularity_volatility" not in tracks or len(tracks) < 2:
        return tracks, None
    usable = tracks[["popularity_volatility", "rank_volatility"]].dropna()
    corr = usable["popularity_volatility"].corr(usable["rank_volatility"]) if len(usable) >= 2 else None
    return tracks, float(corr) if pd.notna(corr) else None


def filter_chart_data(
    data: pd.DataFrame,
    start_date: date | datetime | pd.Timestamp | None = None,
    end_date: date | datetime | pd.Timestamp | None = None,
    artists: list[str] | None = None,
    tracks: list[tuple[str, str]] | None = None,
    rank_range: tuple[int, int] = (1, 50),
    album_types: list[str] | None = None,
) -> pd.DataFrame:
    """Apply the dashboard's shared filters and return a new dataframe."""
    _require(data, {"date", "position"})
    result = data.copy()
    dates = pd.to_datetime(result["date"], errors="coerce")
    if start_date is not None:
        result = result[dates.dt.date >= pd.Timestamp(start_date).date()]
        dates = pd.to_datetime(result["date"], errors="coerce")
    if end_date is not None:
        result = result[dates.dt.date <= pd.Timestamp(end_date).date()]
    if artists:
        _require(result, {"artist"})
        result = result[result["artist"].isin(artists)]
    if tracks:
        _require(result, {"song", "artist"})
        selected = set(tracks)
        identities = list(result[["song", "artist"]].itertuples(index=False, name=None))
        result = result[[identity in selected for identity in identities]]
    low, high = rank_range
    if low > high:
        raise ValueError("rank_range lower bound must not exceed its upper bound")
    result = result[result["position"].between(low, high)]
    if album_types:
        _require(result, {"album_type"})
        result = result[result["album_type"].isin(album_types)]
    return result.copy().reset_index(drop=True)
