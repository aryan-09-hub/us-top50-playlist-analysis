import pandas as pd

from src.analysis import artist_leaderboard, filter_chart_data, song_kpis


def test_song_kpis_use_artist_and_title_and_calculate_metrics():
    data = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-01"]),
            "song": ["Track", "Track", "Track"],
            "artist": ["Artist A", "Artist A", "Artist B"],
            "position": [1, 3, 5],
        }
    )
    result = song_kpis(data).set_index("artist")
    assert result.loc["Artist A", "days_on_chart"] == 2
    assert result.loc["Artist A", "average_rank"] == 2
    assert result.loc["Artist A", "best_rank"] == 1
    assert result.loc["Artist B", "days_on_chart"] == 1


def test_artist_leaderboard_counts_chart_appearances():
    result = artist_leaderboard(
        pd.DataFrame({"artist": ["A", "A", "B"], "position": [1, 4, 3]})
    )
    assert result.iloc[0]["artist"] == "A"
    assert result.iloc[0]["chart_appearances"] == 2


def test_dashboard_filters_intersect_and_keep_track_identity():
    data = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-02"]),
            "position": [1, 5, 12],
            "song": ["Track", "Track", "Other"],
            "artist": ["Artist A", "Artist A", "Artist A"],
            "album_type": ["single", "single", "album"],
        }
    )
    result = filter_chart_data(
        data,
        start_date="2024-01-02",
        end_date="2024-01-02",
        artists=["Artist A"],
        tracks=[("Track", "Artist A")],
        rank_range=(1, 10),
        album_types=["single"],
    )
    assert len(result) == 1
    assert result.iloc[0]["position"] == 5


def test_dashboard_filter_rejects_an_inverted_rank_window():
    data = pd.DataFrame({"date": pd.to_datetime(["2024-01-01"]), "position": [1]})
    try:
        filter_chart_data(data, rank_range=(20, 10))
    except ValueError as error:
        assert "lower bound" in str(error)
    else:
        raise AssertionError("Expected an invalid rank window to raise ValueError")
