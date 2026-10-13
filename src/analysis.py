"""KPI calculations and small, reusable EDA summaries."""

from __future__ import annotations

from datetime import date, datetime

import pandas as pd


def _require(data: pd.DataFrame, columns: set[str]) -> None:
    missing = columns - set(data.columns)
    if missing:
        raise ValueError(f"Missing columns required for analysis: {', '.join(sorted(missing))}")


def song_kpis(data: pd.DataFrame) -> pd.DataFrame:
    """Calculate observed chart days, average/best rank, and rank volatility.

    Track identity combines artist and title. Volatility is the population
    standard deviation of observed ranks; lower values indicate steadier ranks.
    """
    _require(data, {"date", "song", "artist", "position"})
    if data.empty:
        return pd.DataFrame(columns=["song", "artist", "days_on_chart", "average_rank", "best_rank", "rank_volatility"])
    result = (
        data.groupby(["song", "artist"], dropna=False)
        .agg(
            days_on_chart=("date", "nunique"),
            average_rank=("position", "mean"),
            best_rank=("position", "min"),
            rank_volatility=("position", "std"),
        )
        .reset_index()
    )
    result["rank_volatility"] = result["rank_volatility"].fillna(0.0)
    return result.sort_values(["days_on_chart", "best_rank"], ascending=[False, True]).reset_index(drop=True)


def artist_leaderboard(data: pd.DataFrame) -> pd.DataFrame:
    """Summarize artist chart appearances and average rank."""
    _require(data, {"artist", "position"})
    return (
        data.groupby("artist", dropna=False)
        .agg(chart_appearances=("position", "size"), average_rank=("position", "mean"), best_rank=("position", "min"))
        .sort_values(["chart_appearances", "best_rank"], ascending=[False, True])
        .reset_index()
    )


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
    """Aggregate chart-level activity and popularity by observed date."""
    _require(data, {"date", "position"})
    aggregations = {"chart_entries": ("position", "size"), "average_rank": ("position", "mean")}
    if "popularity" in data.columns:
        aggregations["average_popularity"] = ("popularity", "mean")
    if "song" in data.columns:
        aggregations["unique_songs"] = ("song", "nunique")
    return data.groupby("date").agg(**aggregations).reset_index().sort_values("date")


def rank_movement(data: pd.DataFrame) -> pd.DataFrame:
    """Calculate rank change between consecutive observations per track."""
    _require(data, {"date", "song", "artist", "position"})
    result = data.sort_values("date").copy()
    result["rank_change"] = result.groupby(["song", "artist"])["position"].diff()
    return result


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
