import pandas as pd

from src.analysis import (
    artist_dominance_over_time,
    artist_leaderboard,
    daily_chart_transitions,
    daily_rank_distribution,
    daily_summary,
    filter_chart_data,
    popularity_by_rank_cohort,
    popularity_stability_summary,
    rank_movement,
    song_kpis,
    split_artist_credit,
)


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
        pd.DataFrame({
            "artist": ["A", "A", "B"], "position": [1, 4, 3],
            "song": ["One", "Two", "One"],
            "date": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-01"]),
        })
    )
    assert result.iloc[0]["artist"] == "A"
    assert result.iloc[0]["chart_appearances"] == 2
    assert result.iloc[0]["unique_songs"] == 2
    assert result.iloc[0]["days_present"] == 2


def test_artist_dominance_splits_collaborations_and_conserves_chart_slots():
    data = pd.DataFrame({
        "date": pd.to_datetime(["2024-01-01", "2024-01-01"]),
        "artist": ["Artist A", "Artist A & Artist B"],
    })
    result = artist_dominance_over_time(data).set_index("artist")
    assert result.loc["Artist A", "share_pct"] == 75
    assert result.loc["Artist B", "share_pct"] == 25
    assert result["share_pct"].sum() == 100


def test_artist_credit_parser_keeps_earth_wind_and_fire_together():
    assert split_artist_credit("Earth, Wind & Fire & Guest Artist") == [
        "Earth, Wind & Fire", "Guest Artist"
    ]


def test_daily_summary_adds_trailing_seven_observation_popularity_mean():
    dates = pd.date_range("2024-01-01", periods=8)
    data = pd.DataFrame({"date": dates, "position": [1] * 8, "popularity": range(10, 90, 10)})
    result = daily_summary(data)
    assert result.loc[0, "popularity_trend_score"] == 10
    assert result.loc[6, "popularity_trend_score"] == 40
    assert result.loc[7, "popularity_trend_score"] == 50


def test_rank_movement_does_not_bridge_missing_calendar_dates():
    data = pd.DataFrame({
        "date": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-04"]),
        "song": ["Track"] * 3, "artist": ["Artist"] * 3, "position": [20, 12, 2],
    })
    result = rank_movement(data)
    assert pd.isna(result.loc[0, "rank_change"])
    assert result.loc[1, "rank_change"] == -8
    assert pd.isna(result.loc[2, "rank_change"])


def test_transition_counts_only_adjacent_daily_snapshots():
    data = pd.DataFrame({
        "date": pd.to_datetime(["2024-01-01", "2024-01-01", "2024-01-02", "2024-01-02", "2024-01-04"]),
        "song": ["A", "B", "B", "C", "C"], "artist": ["X"] * 5,
    })
    result = daily_chart_transitions(data)
    assert len(result) == 1
    assert result.iloc[0]["entries"] == 1
    assert result.iloc[0]["exits"] == 1


def test_daily_rank_distribution_and_popularity_cohorts():
    data = pd.DataFrame({
        "date": pd.to_datetime(["2024-01-01"] * 50),
        "position": range(1, 51), "popularity": range(1, 51),
    })
    distribution = daily_rank_distribution(data)
    assert distribution["observations"].tolist() == [10, 10, 10, 10, 10]
    cohorts = popularity_by_rank_cohort(data)
    assert cohorts["observations"].tolist() == [10, 20, 50]


def test_popularity_stability_summary_returns_track_level_results():
    data = pd.DataFrame({
        "date": pd.to_datetime(["2024-01-01", "2024-01-02"] * 2),
        "song": ["A", "A", "B", "B"], "artist": ["X"] * 4,
        "position": [10, 8, 30, 35], "popularity": [80, 82, 60, 55],
    })
    tracks, correlation = popularity_stability_summary(data)
    assert len(tracks) == 2
    assert "popularity_volatility" in tracks
    assert correlation is not None


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
