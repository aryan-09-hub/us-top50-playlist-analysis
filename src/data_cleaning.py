"""Loading, validating, and cleaning the playlist chart dataset.

The expected columns below match the inspected CSV. Date, position, song, and
artist are needed for core chart analysis; other fields are optional and kept
when available. Unknown columns are retained.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "Atlantic_United_States.csv"
EXPECTED_COLUMNS = {
    "date",
    "position",
    "song",
    "artist",
    "popularity",
    "duration_ms",
    "album_type",
    "total_tracks",
    "is_explicit",
    "album_cover_url",
}
CORE_COLUMNS = {"date", "position", "song", "artist"}


def load_dataset(path: str | Path = DEFAULT_DATA_PATH) -> pd.DataFrame:
    """Load a CSV file without changing it; dates are parsed during cleaning."""
    source = Path(path).expanduser()
    if not source.is_file():
        raise FileNotFoundError(
            f"Dataset not found: {source}. Set PLAYLIST_DATA_PATH or pass a path."
        )
    return pd.read_csv(source)


def validate_dataset(
    data: pd.DataFrame,
    required_columns: Iterable[str] = CORE_COLUMNS,
) -> list[str]:
    """Return human-readable validation issues; an empty list means no issues."""
    issues: list[str] = []
    missing_columns = sorted(set(required_columns) - set(data.columns))
    if missing_columns:
        issues.append(f"Missing required columns: {', '.join(missing_columns)}")
        return issues

    if data.empty:
        issues.append("Dataset contains no rows.")
        return issues

    dates = pd.to_datetime(data["date"], format="%d-%m-%Y", errors="coerce")
    if dates.isna().any():
        issues.append(f"{int(dates.isna().sum())} date value(s) could not be parsed.")

    positions = pd.to_numeric(data["position"], errors="coerce")
    if positions.isna().any():
        issues.append("Position contains missing or non-numeric values.")
    elif ((positions < 1) | (positions > 50)).any():
        issues.append("Position contains values outside the expected range 1–50.")

    if data.duplicated().any():
        issues.append(f"{int(data.duplicated().sum())} exact duplicate row(s) found.")
    return issues


def clean_dataset(data: pd.DataFrame) -> pd.DataFrame:
    """Return a cleaned copy with parsed dates and exact duplicates removed.

    Conflicting rows (including same-date rank collisions) are preserved for
    review rather than silently choosing a rank.
    """
    issues = validate_dataset(data)
    missing_columns = sorted(CORE_COLUMNS - set(data.columns))
    if missing_columns:
        raise ValueError("Cannot clean dataset. " + issues[0])

    cleaned = data.copy()
    cleaned["date"] = pd.to_datetime(
        cleaned["date"], format="%d-%m-%Y", errors="coerce"
    )
    cleaned["position"] = pd.to_numeric(cleaned["position"], errors="coerce")
    for column in ("popularity", "duration_ms", "total_tracks"):
        if column in cleaned:
            cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce")
    if "is_explicit" in cleaned:
        cleaned["is_explicit"] = cleaned["is_explicit"].astype("boolean")
    for column in ("song", "artist", "album_type"):
        if column not in cleaned:
            continue
        cleaned[column] = cleaned[column].astype("string").str.strip()

    cleaned = cleaned.drop_duplicates().reset_index(drop=True)
    return cleaned


def chart_date_quality(data: pd.DataFrame, expected_size: int = 50) -> pd.DataFrame:
    """Report dates that do not contain one unique row for each chart rank."""
    if not {"date", "position"}.issubset(data.columns):
        return pd.DataFrame(columns=["date", "rows", "unique_positions", "min_position", "max_position", "duplicate_positions", "is_valid"])
    rows = data.groupby("date", dropna=False).agg(
        rows=("position", "size"),
        unique_positions=("position", "nunique"),
        min_position=("position", "min"),
        max_position=("position", "max"),
    )
    rows = rows.reset_index()
    rows["duplicate_positions"] = rows["rows"] - rows["unique_positions"]
    rows["is_valid"] = (
        rows["date"].notna()
        & (rows["rows"] == expected_size)
        & (rows["unique_positions"] == expected_size)
        & (rows["min_position"] == 1)
        & (rows["max_position"] == expected_size)
    )
    return rows


def analysis_ready_data(data: pd.DataFrame, expected_size: int = 50) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return valid chart dates for analysis and a report of excluded dates.

    Exact duplicate rows are removed first. Dates with missing or conflicting
    ranks are excluded as a whole from rank comparisons and returned separately.
    """
    cleaned = clean_dataset(data)
    quality = chart_date_quality(cleaned, expected_size=expected_size)
    invalid_dates = quality.loc[~quality["is_valid"], "date"]
    excluded = cleaned[cleaned["date"].isin(invalid_dates)].copy()
    ready = cleaned[~cleaned["date"].isin(invalid_dates)].copy().reset_index(drop=True)
    return ready, quality.loc[~quality["is_valid"]].reset_index(drop=True)


def load_and_clean(path: str | Path = DEFAULT_DATA_PATH) -> pd.DataFrame:
    """Load and clean a dataset from ``path``."""
    return clean_dataset(load_dataset(path))
