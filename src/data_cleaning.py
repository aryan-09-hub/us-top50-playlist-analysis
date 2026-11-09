"""Loading, validating, and cleaning the playlist chart dataset.

The expected columns below match the inspected CSV. Date, position, song, and
artist are needed for core chart analysis; other fields are optional and kept
when available. Unknown columns are retained.
"""

from __future__ import annotations

from pathlib import Path
from collections import Counter, defaultdict
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
ALLOWED_ALBUM_TYPES = {"album", "single", "compilation"}
MAX_DURATION_MS = 3_600_000  # One hour; flags implausible duration values for review.


def _split_artist_credit(credit: object) -> list[str]:
    """Split common collaboration credits while preserving Earth, Wind & Fire."""
    if pd.isna(credit):
        return []
    marker = "__EARTH_WIND_AND_FIRE__"
    protected = str(credit).replace("Earth, Wind & Fire", marker)
    return [part.strip().replace(marker, "Earth, Wind & Fire") for part in protected.split(" & ") if part.strip()]


def standardize_artist_credits(values: pd.Series) -> pd.Series:
    """Normalize exact case/whitespace variants to the most common source spelling.

    This deliberately does not guess aliases or misspellings. A verified alias
    map is required to merge names that differ beyond case and whitespace.
    """
    components = values.dropna().map(_split_artist_credit)
    counts: Counter[str] = Counter()
    spellings: dict[str, Counter[str]] = defaultdict(Counter)
    for names in components:
        for name in names:
            key = " ".join(name.split()).casefold()
            counts[key] += 1
            spellings[key][" ".join(name.split())] += 1
    canonical = {
        key: sorted(forms, key=lambda form: (-forms[form], form.casefold(), form))[0]
        for key, forms in spellings.items()
    }

    def normalize_credit(credit: object) -> object:
        if pd.isna(credit):
            return pd.NA
        return " & ".join(canonical.get(" ".join(name.split()).casefold(), name) for name in _split_artist_credit(credit))

    return values.map(normalize_credit).astype("string")


def load_dataset(path: str | Path = DEFAULT_DATA_PATH) -> pd.DataFrame:
    """Load a CSV file without changing it; dates are parsed during cleaning."""
    source = Path(path).expanduser()
    if not source.is_file() and source.resolve() == DEFAULT_DATA_PATH.resolve():
        # The original project CSV may be checked out at the repository root,
        # while local copies are commonly stored in the ignored data/raw folder.
        root_copy = PROJECT_ROOT / "Atlantic_United_States.csv"
        if root_copy.is_file():
            source = root_copy
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

    for column in ("song", "artist"):
        missing_count = int(data[column].isna().sum())
        if missing_count:
            issues.append(f"{column} contains {missing_count} missing value(s).")

    duplicate_track_dates = int(data.duplicated(["date", "song", "artist"]).sum())
    if duplicate_track_dates:
        issues.append(f"{duplicate_track_dates} duplicate song-artist-date entr(y/ies) found.")

    for column in ("song", "artist"):
        values = data[column].astype("string")
        inconsistent = values.ne(values.str.strip().str.replace(r"\s+", " ", regex=True))
        if inconsistent.fillna(False).any():
            issues.append(f"{column} has whitespace formatting that will be standardized in the cleaned copy.")

    positions = pd.to_numeric(data["position"], errors="coerce")
    if positions.isna().any():
        issues.append("Position contains missing or non-numeric values.")
    if ((positions < 1) | (positions > 50)).any():
        issues.append("Position contains values outside the expected range 1–50.")
    if (positions.notna() & (positions % 1 != 0)).any():
        issues.append("Position contains non-whole-number rank values.")

    optional_numeric_rules = {
        "popularity": (0, 100, False),
        "duration_ms": (1, MAX_DURATION_MS, False),
        "total_tracks": (1, None, True),
    }
    for column, (minimum, maximum, require_integer) in optional_numeric_rules.items():
        if column not in data:
            continue
        values = pd.to_numeric(data[column], errors="coerce")
        missing_count = int(values.isna().sum())
        if missing_count:
            issues.append(f"{column} contains {missing_count} missing or non-numeric value(s).")
        invalid = values.notna() & (values < minimum)
        if maximum is not None:
            invalid |= values.notna() & (values > maximum)
        if require_integer:
            invalid |= values.notna() & (values % 1 != 0)
        if invalid.any():
            bounds = f"{minimum}–{maximum}" if maximum is not None else f"at least {minimum} (whole numbers)"
            issues.append(f"{column} contains {int(invalid.sum())} value(s) outside the valid range {bounds}.")

    if "album_type" in data:
        types = data["album_type"].astype("string").str.strip().str.casefold()
        missing_count = int(types.isna().sum() + types.eq("").sum())
        if missing_count:
            issues.append(f"album_type contains {missing_count} missing value(s).")
        unknown = sorted(set(types.dropna()) - {""} - ALLOWED_ALBUM_TYPES)
        if unknown:
            issues.append("album_type contains unrecognized value(s): " + ", ".join(unknown))

    if "is_explicit" in data:
        values = data["is_explicit"].astype("string").str.strip().str.casefold()
        valid_boolean = values.isin({"true", "false", "1", "0", "yes", "no", "y", "n"})
        invalid_count = int((values.notna() & ~valid_boolean).sum())
        missing_count = int(values.isna().sum())
        if missing_count:
            issues.append(f"is_explicit contains {missing_count} missing value(s).")
        if invalid_count:
            issues.append(f"is_explicit contains {invalid_count} unrecognized boolean value(s).")

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
        boolean_values = cleaned["is_explicit"].astype("string").str.strip().str.casefold()
        boolean_map = {"true": True, "1": True, "yes": True, "y": True, "false": False, "0": False, "no": False, "n": False}
        cleaned["is_explicit"] = boolean_values.map(boolean_map).astype("boolean")
    for column in ("song", "artist", "album_type"):
        if column not in cleaned:
            continue
        cleaned[column] = cleaned[column].astype("string").str.strip().str.replace(r"\s+", " ", regex=True)

    if "album_type" in cleaned:
        cleaned["album_type"] = cleaned["album_type"].str.casefold()
    if "artist" in cleaned:
        cleaned["artist"] = standardize_artist_credits(cleaned["artist"])

    # Invalid optional measures remain visible in validation notes but are
    # excluded from derived summaries in this analysis copy.
    if "popularity" in cleaned:
        invalid = ~cleaned["popularity"].between(0, 100)
        cleaned.loc[invalid, "popularity"] = pd.NA
    if "duration_ms" in cleaned:
        invalid = ~cleaned["duration_ms"].between(1, MAX_DURATION_MS)
        cleaned.loc[invalid, "duration_ms"] = pd.NA
    if "total_tracks" in cleaned:
        invalid = (cleaned["total_tracks"] < 1) | (cleaned["total_tracks"] % 1 != 0)
        cleaned.loc[invalid, "total_tracks"] = pd.NA

    if "duration_ms" in cleaned:
        cleaned["duration_minutes"] = cleaned["duration_ms"] / 60_000

    cleaned = cleaned.drop_duplicates().reset_index(drop=True)
    return cleaned


def chart_date_quality(data: pd.DataFrame, expected_size: int = 50) -> pd.DataFrame:
    """Report dates that do not contain one unique row for each chart rank."""
    required = {"date", "position", "song", "artist"}
    if not required.issubset(data.columns):
        return pd.DataFrame(columns=["date", "rows", "unique_positions", "min_position", "max_position", "duplicate_track_dates", "missing_song", "missing_artist", "duplicate_positions", "is_valid"])
    work = data.copy()
    work["_duplicate_track_date"] = work.duplicated(["date", "song", "artist"], keep="first")
    numeric_positions = pd.to_numeric(work["position"], errors="coerce")
    work["_invalid_position"] = numeric_positions.isna() | ~numeric_positions.between(1, expected_size) | (numeric_positions % 1 != 0)
    work["position"] = numeric_positions
    rows = work.groupby("date", dropna=False).agg(
        rows=("position", "size"),
        unique_positions=("position", "nunique"),
        min_position=("position", "min"),
        max_position=("position", "max"),
        duplicate_track_dates=("_duplicate_track_date", "sum"),
        invalid_positions=("_invalid_position", "sum"),
        missing_song=("song", lambda values: values.isna().sum()),
        missing_artist=("artist", lambda values: values.isna().sum()),
    )
    rows = rows.reset_index()
    rows["duplicate_positions"] = rows["rows"] - rows["unique_positions"]
    rows["is_valid"] = (
        rows["date"].notna()
        & (rows["rows"] == expected_size)
        & (rows["unique_positions"] == expected_size)
        & (rows["min_position"] == 1)
        & (rows["max_position"] == expected_size)
        & (rows["invalid_positions"] == 0)
        & (rows["duplicate_track_dates"] == 0)
        & (rows["missing_song"] == 0)
        & (rows["missing_artist"] == 0)
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
