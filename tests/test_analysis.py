import pandas as pd
import pytest

from src.analysis import (
    artist_dominance_over_time,
    artist_leaderboard,
    chart_transition_details,
    chart_transition_window,
    daily_chart_transitions,
    daily_rank_distribution,
    daily_summary,
    explicit_content_share,
    filter_chart_data,
    popularity_by_rank_cohort,
    popularity_cohort_distribution,
    popularity_stability_summary,
    rank_movement,
    song_kpis,
    song_popularity_trend,
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


def test_single_observation_rank_volatility_is_unavailable():
    result = song_kpis(pd.DataFrame({
        "date": pd.to_datetime(["2024-01-01"]),
        "song": ["Track"], "artist": ["Artist"], "position": [8],
        "popularity": [75],
    }))
    assert pd.isna(result.loc[0, "rank_volatility"])
    assert pd.isna(result.loc[0, "popularity_volatility"])


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


def test_artist_leaderboard_credits_songs_and_appearances_to_each_collaborator():
    result = artist_leaderboard(pd.DataFrame({
        "date": pd.to_datetime(["2024-01-01", "2024-01-02"]),
        "artist": ["Artist A & Artist B", "Artist A"],
        "song": ["Collaboration", "Solo track"],
        "position": [4, 8],
    })).set_index("artist")
    assert result.loc["Artist A", "chart_appearances"] == 2
    assert result.loc["Artist A", "unique_songs"] == 2
    assert result.loc["Artist B", "chart_appearances"] == 1
    assert result.loc["Artist B", "unique_songs"] == 1


def test_explicit_content_share_uses_known_chart_observations_only():
    result = explicit_content_share(pd.DataFrame({"is_explicit": [True, False, True, None]}))
    assert result == {
        "explicit_observations": 2,
        "known_observations": 3,
        "unknown_observations": 1,
        "explicit_share_pct": pytest.approx(200 / 3),
    }


def test_explicit_content_share_handles_missing_field_and_all_unknown_values():
    assert explicit_content_share(pd.DataFrame({"position": [1]}))["explicit_share_pct"] is None
    result = explicit_content_share(pd.DataFrame({"is_explicit": [None, pd.NA]}))
    assert result["known_observations"] == 0
    assert result["unknown_observations"] == 2
    assert result["explicit_share_pct"] is None


def test_explicit_content_share_parses_supported_boolean_strings():
    result = explicit_content_share(pd.DataFrame({"is_explicit": ["YES", "no", "unknown"]}))
    assert result["explicit_observations"] == 1
    assert result["known_observations"] == 2
    assert result["unknown_observations"] == 1
    assert result["explicit_share_pct"] == 50


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


def test_song_popularity_trend_groups_duplicate_dates_and_smooths_observed_values():
    data = pd.DataFrame({
        "date": pd.to_datetime(["2024-01-01", "2024-01-01", "2024-01-04", "2024-01-05"]),
        "popularity": [20, 40, 60, None],
    })
    result = song_popularity_trend(data, window=2)
    assert result["date"].tolist() == [pd.Timestamp("2024-01-01"), pd.Timestamp("2024-01-04")]
    assert result["popularity"].tolist() == [30, 60]
    assert result["popularity_trend_score"].tolist() == [30, 45]


def test_song_popularity_trend_rejects_nonpositive_window():
    data = pd.DataFrame({"date": pd.to_datetime(["2024-01-01"]), "popularity": [40]})
    with pytest.raises(ValueError, match="window"):
        song_popularity_trend(data, window=0)


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


def test_transition_details_identify_entering_and_exiting_tracks_with_ranks():
    data = pd.DataFrame({
        "date": pd.to_datetime(["2024-01-01", "2024-01-01", "2024-01-02", "2024-01-02", "2024-01-04"]),
        "song": ["A", "B", "B", "C", "D"],
        "artist": ["X", "X", "X", "Y", "Z"],
        "position": [5, 10, 8, 1, 2],
    })
    result = chart_transition_details(data)
    assert len(result) == 2
    entrant = result[result["transition"].eq("Entry")].iloc[0]
    exiter = result[result["transition"].eq("Exit")].iloc[0]
    assert (entrant["song"], entrant["artist"], entrant["position"]) == ("C", "Y", 1)
    assert (exiter["song"], exiter["artist"], exiter["previous_position"]) == ("A", "X", 5)


def test_transition_window_uses_full_chart_and_prior_snapshot_at_window_start():
    first_day = pd.DataFrame({
        "date": pd.Timestamp("2024-01-01"),
        "position": range(1, 51),
        "song": [f"Track {rank:02d}" for rank in range(1, 51)],
        "artist": ["Artist"] * 50,
        "album_type": ["album"] * 50,
    })
    second_day = first_day.copy()
    second_day["date"] = pd.Timestamp("2024-01-02")
    second_day.loc[49, "song"] = "New Entry"
    third_day = second_day.copy()
    third_day["date"] = pd.Timestamp("2024-01-03")
    third_day.loc[19, "position"], third_day.loc[20, "position"] = 21, 20
    full_chart = pd.concat([first_day, second_day, third_day], ignore_index=True)

    counts, details = chart_transition_window(
        full_chart, start_date="2024-01-02", end_date="2024-01-03"
    )

    assert counts["date"].tolist() == [pd.Timestamp("2024-01-02"), pd.Timestamp("2024-01-03")]
    assert counts.loc[0, "entries"] == 1
    assert counts.loc[0, "exits"] == 1
    assert counts.loc[1, "entries"] == 0
    assert counts.loc[1, "exits"] == 0
    assert details["date"].tolist() == [pd.Timestamp("2024-01-02")] * 2
    assert set(details.loc[details["transition"].eq("Entry"), "song"]) == {"New Entry"}
    assert set(details.loc[details["transition"].eq("Exit"), "song"]) == {"Track 50"}


def test_transition_window_rejects_reversed_date_range():
    data = pd.DataFrame({
        "date": pd.to_datetime(["2024-01-01"]), "song": ["Track"], "artist": ["Artist"]
    })
    with pytest.raises(ValueError, match="start_date"):
        chart_transition_window(data, "2024-01-02", "2024-01-01")


def test_daily_rank_distribution_and_popularity_cohorts():
    data = pd.DataFrame({
        "date": pd.to_datetime(["2024-01-01"] * 50),
        "position": range(1, 51), "popularity": range(1, 51),
    })
    distribution = daily_rank_distribution(data)
    assert distribution["observations"].tolist() == [10, 10, 10, 10, 10]
    cohorts = popularity_by_rank_cohort(data)
    assert cohorts["observations"].tolist() == [10, 20, 50]
    assert cohorts.loc[0, "p25_popularity"] == 3.25
    assert cohorts.loc[0, "p75_popularity"] == 7.75
    distribution = popularity_cohort_distribution(data)
    assert distribution.groupby("cohort").size().tolist() == [10, 20, 50]
    assert distribution.groupby("cohort")["popularity"].max().tolist() == [10, 20, 50]


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
