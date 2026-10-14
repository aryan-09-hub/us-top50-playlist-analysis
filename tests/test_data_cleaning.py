import pandas as pd

from src.data_cleaning import analysis_ready_data, clean_dataset, validate_dataset


def sample_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": ["18-05-2024", "18-05-2024"],
            "position": [1, 1],
            "song": ["Track", "Track"],
            "artist": ["Artist", "Artist"],
            "popularity": [80, 80],
            "duration_ms": [180000, 180000],
            "album_type": ["single", "single"],
            "total_tracks": [1, 1],
            "is_explicit": [False, False],
            "album_cover_url": ["https://example.com/cover.jpg"] * 2,
        }
    )


def test_validation_reports_exact_duplicates():
    issues = validate_dataset(sample_data())
    assert any("exact duplicate" in issue for issue in issues)


def test_cleaning_parses_date_and_drops_exact_duplicates():
    cleaned = clean_dataset(sample_data())
    assert len(cleaned) == 1
    assert pd.api.types.is_datetime64_any_dtype(cleaned["date"])


def test_validation_reports_missing_required_columns():
    issues = validate_dataset(pd.DataFrame({"song": ["Track"]}))
    assert issues and "Missing required columns" in issues[0]


def test_optional_fields_can_be_missing_without_blocking_cleaning():
    data = sample_data().drop(columns=["popularity", "duration_ms", "total_tracks", "is_explicit", "album_type", "album_cover_url"])
    assert not any("Missing required columns" in issue for issue in validate_dataset(data))
    cleaned = clean_dataset(data)
    assert "position" in cleaned.columns
    assert "popularity" not in cleaned.columns


def test_analysis_excludes_a_date_with_conflicting_positions():
    data = sample_data().iloc[[0]].copy()
    second = data.copy()
    second["song"] = "Another track"
    data["position"] = 1
    second["position"] = 1
    ready, invalid = analysis_ready_data(pd.concat([data, second], ignore_index=True), expected_size=2)
    assert ready.empty
    assert len(invalid) == 1
    assert invalid.iloc[0]["duplicate_positions"] == 1


def test_analysis_excludes_unparseable_dates_and_out_of_range_ranks():
    rows = []
    for date, position, song in [
        ("18-05-2024", 1, "A"),
        ("18-05-2024", 51, "B"),
        ("not-a-date", 1, "C"),
        ("not-a-date", 2, "D"),
    ]:
        row = sample_data().iloc[0].copy()
        row["date"], row["position"], row["song"] = date, position, song
        rows.append(row)
    ready, invalid = analysis_ready_data(pd.DataFrame(rows), expected_size=2)
    assert ready.empty
    assert len(invalid) == 2


def test_cleaning_standardizes_artist_whitespace_without_changing_case():
    data = sample_data().iloc[[0]].copy()
    data["artist"] = "  arTist   Name  "
    cleaned = clean_dataset(data)
    assert cleaned.loc[0, "artist"] == "arTist Name"


def test_duplicate_song_artist_date_invalidates_snapshot_even_with_unique_ranks():
    data = sample_data().iloc[[0]].copy()
    other = data.copy()
    data["position"] = 1
    other["position"] = 2
    other["popularity"] = 81
    raw = pd.concat([data, other], ignore_index=True)
    issues = validate_dataset(raw)
    assert any("duplicate song-artist-date" in issue for issue in issues)
    ready, invalid = analysis_ready_data(raw, expected_size=2)
    assert ready.empty
    assert invalid.loc[0, "duplicate_track_dates"] == 1
