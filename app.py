"""Interactive Streamlit dashboard for the US Top 50 playlist project."""

from __future__ import annotations

import os
import importlib
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from src import analysis, data_cleaning

# Reload local project modules so Streamlit's running process picks up edits in
# src/ during development, even when the server was started before this build.
analysis = importlib.reload(analysis)
data_cleaning = importlib.reload(data_cleaning)
artist_leaderboard = analysis.artist_leaderboard
filter_chart_data = analysis.filter_chart_data
popularity_rank_summary = analysis.popularity_rank_summary
song_kpis = analysis.song_kpis
DEFAULT_DATA_PATH = data_cleaning.DEFAULT_DATA_PATH
analysis_ready_data = data_cleaning.analysis_ready_data
load_dataset = data_cleaning.load_dataset
validate_dataset = data_cleaning.validate_dataset

st.set_page_config(
    page_title="US Top 50 | Listening Intelligence",
    page_icon="♫",
    layout="wide",
    initial_sidebar_state="expanded",
)

INK = "#E1E2EB"
MUTED = "#94A3B8"
TEAL = "#00DCE6"
CORAL = "#FF2A85"
GOLD = "#FFB800"
PALETTE = [TEAL, CORAL, GOLD, "#7C3AED", "#10B981", "#FF8A5B", "#9AA7B8"]

st.markdown(
    """
    <style>
      :root { --ink:#E1E2EB; --muted:#94A3B8; --teal:#00DCE6; --line:#252B38; --panel:#181C24; --dock:#12151B; }
      html, body, [class*="css"] { font-family: 'Segoe UI', Arial, sans-serif; }
      .stApp { background:#0B0D11; color:var(--ink); }
      [data-testid="stHeader"] { background:rgba(11,13,17,.94); }
      [data-testid="stSidebar"] { background:#101319; border-right:1px solid #252B38; }
      [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color:var(--ink); }
      .block-container { padding-top:2rem; padding-bottom:2.5rem; max-width:1600px; }
      h1, h2, h3 { font-family:'Segoe UI', Arial, sans-serif; letter-spacing:-.025em; color:var(--ink); }
      h1 { font-size:2rem !important; font-weight:750 !important; }
      h2 { font-size:1.3rem !important; font-weight:700 !important; }
      h3 { font-size:1.02rem !important; font-weight:700 !important; }
      [data-testid="stMetric"] { background:#181C24; border:1px solid #2E3646; border-top-color:#3A494B; border-radius:8px; padding:14px 17px; box-shadow:none; }
      [data-testid="stMetricLabel"] { color:#94A3B8; font-size:.72rem; text-transform:uppercase; letter-spacing:.07em; }
      [data-testid="stMetricValue"] { color:#F8FAFC; font-family:Consolas, 'Courier New', monospace; font-size:1.55rem; font-weight:700; }
      [data-testid="stPlotlyChart"] { background:#12151B; border:1px solid #252B38; border-radius:8px; padding:5px 8px 0; box-shadow:none; }
      [data-testid="stDataFrame"] { background:#12151B; border:1px solid #252B38; border-radius:8px; overflow:hidden; }
      [data-testid="stDateInput"] input, [data-baseweb="select"] > div { background:#12151B !important; color:#E1E2EB !important; border-color:#3A494B !important; }
      [data-testid="stWidgetLabel"] p, .stApp label { color:#B9CACB !important; }
      [data-testid="stCaptionContainer"] { color:#94A3B8; }
      [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color:#B9CACB; }
      [data-testid="stSidebar"] hr { border-color:#252B38; }
      [data-testid="stSegmentedControl"] { background:#12151B; border:1px solid #252B38; border-radius:6px; padding:4px; }
      [data-testid="stSegmentedControl"] button { color:#B9CACB; border-radius:4px; }
      [data-testid="stSegmentedControl"] button[aria-pressed="true"] { background:#00DCE6; color:#0B0D11; font-weight:700; }
      [data-testid="stTabs"] [role="tablist"] { gap:5px; border-bottom:1px solid #252B38; }
      [data-testid="stTabs"] button[role="tab"] { color:#94A3B8; }
      [data-testid="stTabs"] button[role="tab"][aria-selected="true"] { color:#00DCE6; border-bottom-color:#00DCE6; }
      div[data-testid="stAlert"] { border-radius:6px; background:#181C24; }
      .hero { background:#12151B; border:1px solid #252B38; border-left:3px solid #00DCE6; color:#F8FAFC; border-radius:8px; padding:19px 23px; margin:0 0 12px; box-shadow:none; }
      .hero p { max-width:100%; overflow-wrap:anywhere; line-height:1.45; margin:0; color:#B9CACB; font-size:.91rem; }
      .hero-eyebrow { color:#00DCE6; font-family:Consolas, monospace; font-size:.65rem; letter-spacing:.12em; text-transform:uppercase; font-weight:700; margin-bottom:5px; }
      .hero h1 { color:#F8FAFC !important; margin:0 0 4px !important; }
      .hero-meta { margin-top:11px; color:#94A3B8; font: .72rem Consolas, monospace; }
      .section-kicker { color:#00DCE6; text-transform:uppercase; letter-spacing:.12em; font:700 .64rem Consolas, monospace; margin:8px 0 3px; }
      .section-note { color:#94A3B8; font-size:.82rem; margin-top:-7px; margin-bottom:12px; }
      .small-note { color:#94A3B8; font-size:.74rem; }
      .stButton button { border-radius:5px; border-color:#3A494B; }
      .stButton button[kind="primary"] { background:#00DCE6; color:#0B0D11; border-color:#00DCE6; }
      .stRadio [role="radiogroup"] { gap:8px; }
      a { color:#00DCE6; }
      @media (max-width: 760px) {
        .block-container { padding-left:.8rem; padding-right:.8rem; }
        .stHorizontalBlock { flex-wrap:wrap; gap:.55rem; }
        .stHorizontalBlock > [data-testid="stColumn"] { flex:1 1 calc(50% - .55rem) !important; min-width:calc(50% - .55rem) !important; }
        [data-testid="stMetric"] { padding:11px 12px; }
        [data-testid="stMetricLabel"] { white-space:normal; line-height:1.25; font-size:.66rem; }
        [data-testid="stMetricValue"] { overflow-wrap:anywhere; font-size:1.25rem; }
        .hero { padding:16px; }
        .hero h1 { font-size:1.6rem !important; }
      }
      footer { visibility:hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner="Loading and checking the playlist data…")
def read_source(path_string: str) -> tuple[pd.DataFrame, pd.DataFrame, list[str], int]:
    raw = load_dataset(path_string)
    issues = validate_dataset(raw)
    optional_missing = sorted(
        data_cleaning.EXPECTED_COLUMNS - set(raw.columns) - data_cleaning.CORE_COLUMNS
    )
    if optional_missing:
        issues.append("Optional fields unavailable; related analyses are skipped: " + ", ".join(optional_missing))
    ready, invalid_dates = analysis_ready_data(raw)
    return ready, invalid_dates, issues, len(raw)


@st.cache_data(show_spinner=False)
def source_profile(path_string: str) -> tuple[pd.DataFrame, pd.Series]:
    raw = load_dataset(path_string)
    profile = pd.DataFrame({
        "Column": raw.columns,
        "Type": raw.dtypes.astype(str).values,
        "Missing values": raw.isna().sum().values,
    })
    dates = pd.to_datetime(raw["date"], format="%d-%m-%Y", errors="coerce") if "date" in raw else pd.Series(dtype="datetime64[ns]")
    return profile, dates


def format_track(row: pd.Series) -> str:
    return f"{row['song']}  ·  {row['artist']}"


def base_chart(fig, height: int = 370):
    fig.update_layout(
        height=height,
        margin=dict(l=16, r=18, t=48, b=16),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Segoe UI, Arial, sans-serif", color=INK, size=11),
        title=dict(x=0.02, xanchor="left", font=dict(size=14, color=INK)),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, title=None),
        hoverlabel=dict(bgcolor="#1F242F", bordercolor="#3A494B", font_color="#F8FAFC", font_size=12),
    )
    fig.update_xaxes(showgrid=False, linecolor="#252B38", zeroline=False, tickfont_color="#B9CACB")
    fig.update_yaxes(gridcolor="#252B38", zeroline=False, tickfont_color="#B9CACB")
    return fig


def chart(fig, height: int = 370):
    st.plotly_chart(base_chart(fig, height), width="stretch", config={"displaylogo": False})


def rank_axis(fig):
    """Keep chart position 1 at the top and position 50 at the bottom."""
    fig.update_yaxes(
        autorange="reversed",
        range=[1, 50.5],
        tickmode="array",
        tickvals=[1, 10, 20, 30, 40, 50],
    )
    return fig


def section(title: str, note: str | None = None, kicker: str | None = None):
    if kicker:
        st.markdown(f'<div class="section-kicker">{kicker}</div>', unsafe_allow_html=True)
    st.subheader(title)
    if note:
        st.markdown(f'<div class="section-note">{note}</div>', unsafe_allow_html=True)


def empty_state(message: str):
    st.info(message)


data_path = Path(os.environ.get("PLAYLIST_DATA_PATH", str(DEFAULT_DATA_PATH))).expanduser()
try:
    data, invalid_dates, validation_issues, raw_row_count = read_source(str(data_path))
except (FileNotFoundError, ValueError, pd.errors.ParserError) as error:
    st.title("United States Top 50 Playlist Analysis")
    st.error(f"Could not load the dataset: {error}")
    st.markdown("Place the CSV at `data/raw/Atlantic_United_States.csv` or set `PLAYLIST_DATA_PATH` to its location.")
    st.stop()

if data.empty:
    st.error("No complete chart dates are available for analysis. Review the source data and data quality report.")
    st.stop()

# Sidebar: compact, persistent controls shared across all analytical views.
with st.sidebar:
    st.markdown("### ♫  PLAYLIST INTELLIGENCE")
    st.caption("UNITED STATES  /  TOP 50 ARCHIVE")
    st.divider()
    st.markdown("**FILTER THE CHART**")
    min_day, max_day = data["date"].min().date(), data["date"].max().date()
    chosen_dates = st.date_input(
        "Chart date range", value=(min_day, max_day), min_value=min_day, max_value=max_day
    )
    if isinstance(chosen_dates, (tuple, list)) and len(chosen_dates) == 2:
        start_day, end_day = chosen_dates
    elif isinstance(chosen_dates, (tuple, list)) and len(chosen_dates) == 1:
        start_day = end_day = chosen_dates[0]
    else:
        start_day = end_day = chosen_dates

    artist_options = sorted(data["artist"].dropna().unique().tolist()) if "artist" in data else []
    selected_artists = st.multiselect("Artist", artist_options, placeholder="All artists")
    song_pool = data if not selected_artists else data[data["artist"].isin(selected_artists)]
    song_options = song_pool[["song", "artist"]].drop_duplicates().sort_values(["song", "artist"])
    track_options = list(song_options.itertuples(index=False, name=None))
    selected_tracks = st.multiselect(
        "Song", track_options, format_func=lambda x: f"{x[0]} · {x[1]}", placeholder="All songs"
    )
    rank_range = st.slider("Chart position", 1, 50, (1, 50), help="Lower numbers represent higher chart positions.")
    album_options = sorted(data["album_type"].dropna().unique().tolist()) if "album_type" in data else []
    selected_albums = st.multiselect("Album type", album_options, placeholder="All release types")
    st.divider()
    st.caption(f"SOURCE  /  {data_path.name}")
    st.caption(f"{data['date'].nunique():,} valid snapshots · {len(data):,} rows")
    st.markdown('<div class="small-note">One anomalous snapshot is excluded from rank analysis. See Data quality.</div>', unsafe_allow_html=True)

filtered = filter_chart_data(
    data,
    start_date=start_day,
    end_date=end_day,
    artists=selected_artists,
    tracks=selected_tracks,
    rank_range=rank_range,
    album_types=selected_albums,
)

# Main hierarchy: one title, scope, then a small set of shared view tabs.
st.markdown(
    f"""
    <div class="hero">
      <div class="hero-eyebrow">Playlist intelligence / source-backed analysis</div>
      <h1>United States Top 50</h1>
      <p>Track chart movement, observed longevity, artist presence, and recorded popularity.</p>
      <div class="hero-meta">DATA WINDOW  {start_day.strftime('%b %d, %Y')} — {end_day.strftime('%b %d, %Y')} &nbsp; / &nbsp; {len(filtered):,} OBSERVATIONS IN VIEW</div>
    </div>
    """,
    unsafe_allow_html=True,
)
view_label = st.segmented_control(
    "Dashboard section",
    ["Overview & Volatility", "Song Longevity", "Artist Dominance", "Attribute Lab", "Data Quality"],
    default="Overview & Volatility",
    label_visibility="collapsed",
) or "Overview & Volatility"
view = {
    "Overview & Volatility": "Overview",
    "Song Longevity": "Songs",
    "Artist Dominance": "Artists",
    "Attribute Lab": "Compare",
    "Data Quality": "Data quality",
}[view_label]

if filtered.empty and view != "Data quality":
    empty_state("No chart observations match these filters. Broaden the date range, rank range, or selected songs and artists.")
    st.stop()

if view == "Overview":
    section("At a glance", "A filtered view of chart presence and recorded popularity.", "Snapshot")
    unique_tracks = filtered[["song", "artist"]].drop_duplicates().shape[0]
    avg_rank = filtered["position"].mean()
    avg_pop = filtered["popularity"].mean() if "popularity" in filtered else float("nan")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Chart observations", f"{len(filtered):,}")
    k2.metric("Songs represented", f"{unique_tracks:,}")
    k3.metric("Average chart position", f"{avg_rank:.1f}" if pd.notna(avg_rank) else "—", help="A lower average position means a higher typical chart placement.")
    k4.metric("Average popularity", f"{avg_pop:.1f} / 100" if pd.notna(avg_pop) else "Unavailable", help="Popularity is supplied in the dataset; its timestamp and methodology are undocumented.")

    st.write("")
    c1, c2 = st.columns([1.55, 1])
    with c1:
        section("Chart movement", "Daily ranks for the most frequently observed songs in the selected population.")
        kpis = song_kpis(filtered)
        timeline_keys = list(kpis.head(6)[["song", "artist"]].itertuples(index=False, name=None))
        timeline = filtered[["date", "position", "song", "artist"]].copy()
        timeline = timeline[[tuple(x) in set(timeline_keys) for x in timeline[["song", "artist"]].itertuples(index=False, name=None)]]
        if timeline.empty:
            empty_state("No song timeline is available for this selection.")
        else:
            timeline["track"] = timeline["song"] + " · " + timeline["artist"]
            fig = px.line(timeline, x="date", y="position", color="track", color_discrete_sequence=PALETTE,
                          markers=False, labels={"date": "Date", "position": "Chart position", "track": "Song"})
            rank_axis(fig)
            chart(fig, 410)
    with c2:
        section("Artist presence", "Most frequent credited artist entries in the filtered chart observations.")
        board = artist_leaderboard(filtered).head(10).sort_values("chart_appearances")
        fig = px.bar(board, x="chart_appearances", y="artist", orientation="h", color_discrete_sequence=[TEAL],
                     labels={"chart_appearances": "Chart observations", "artist": "Artist"}, text="chart_appearances")
        fig.update_traces(textposition="outside", cliponaxis=False)
        chart(fig, 410)

    st.write("")
    section("Popularity through time", "Mean supplied popularity score across the chart entries recorded on each date.")
    if "popularity" in filtered:
        popularity_by_day = filtered.groupby("date", as_index=False).agg(average_popularity=("popularity", "mean"))
        fig = px.line(popularity_by_day, x="date", y="average_popularity", markers=False,
                      labels={"date": "Date", "average_popularity": "Average popularity (0–100)"},
                      color_discrete_sequence=[GOLD])
        fig.update_yaxes(range=[0, 100])
        chart(fig, 330)
    else:
        empty_state("Popularity is not available in this dataset.")

    st.write("")
    section("Songs with the longest observed runs", "Days on chart counts distinct dates present in this dataset; gaps in the source do not prove continuous chart presence.")
    leaders = song_kpis(filtered).head(12).rename(columns={
        "song": "Song", "artist": "Artist", "days_on_chart": "Observed days",
        "average_rank": "Average rank", "best_rank": "Best rank", "rank_volatility": "Rank volatility",
    })
    st.dataframe(leaders, hide_index=True, width="stretch", column_config={
        "Average rank": st.column_config.NumberColumn(format="%.1f"),
        "Rank volatility": st.column_config.NumberColumn(format="%.1f"),
    })

elif view == "Songs":
    section("Song explorer", "Inspect a track’s rank history and lifetime summary in the selected date window.", "Track detail")
    track_table = filtered[["song", "artist"]].drop_duplicates().sort_values(["song", "artist"])
    track_keys = list(track_table.itertuples(index=False, name=None))
    chosen_track = st.selectbox("Choose a track", track_keys, format_func=lambda x: f"{x[0]} · {x[1]}")
    track_data = filtered[(filtered["song"] == chosen_track[0]) & (filtered["artist"] == chosen_track[1])].sort_values("date")
    track_metrics = song_kpis(track_data).iloc[0]
    a, b, c, d = st.columns(4)
    a.metric("Observed days", f"{int(track_metrics['days_on_chart']):,}")
    b.metric("Best rank", f"#{int(track_metrics['best_rank'])}")
    c.metric("Average rank", f"{track_metrics['average_rank']:.1f}")
    d.metric("Rank volatility", f"{track_metrics['rank_volatility']:.1f}", help="Standard deviation of observed ranks; lower values mean less spread in rank.")
    fig = px.line(track_data, x="date", y="position", markers=True,
                  labels={"date": "Date", "position": "Chart position"}, color_discrete_sequence=[TEAL])
    rank_axis(fig)
    chart(fig, 430)
    detail_cols = [c for c in ["date", "position", "popularity", "album_type", "duration_ms", "total_tracks", "is_explicit"] if c in track_data]
    st.dataframe(track_data[detail_cols].sort_values("date", ascending=False), hide_index=True, width="stretch")

elif view == "Artists":
    section("Artist leaderboard", "Artist credits are counted as supplied in the source; multi-artist credits are not split into individual contributors.", "Artist detail")
    leaderboard = artist_leaderboard(filtered)
    c1, c2 = st.columns([1.2, 1])
    with c1:
        top = leaderboard.head(15).sort_values("chart_appearances")
        fig = px.bar(top, x="chart_appearances", y="artist", orientation="h", color="average_rank",
                     color_continuous_scale=[TEAL, GOLD, CORAL],
                     labels={"chart_appearances": "Chart observations", "artist": "Artist", "average_rank": "Avg. rank"},
                     hover_data={"best_rank": True, "average_rank": ":.1f"})
        fig.update_yaxes(categoryorder="total ascending")
        chart(fig, 510)
    with c2:
        artist_choice = st.selectbox("Artist history", leaderboard["artist"].tolist())
        artist_data = filtered[filtered["artist"] == artist_choice]
        artist_daily = artist_data.groupby("date").agg(chart_entries=("position", "size"), average_rank=("position", "mean")).reset_index()
        fig = px.line(artist_daily, x="date", y="chart_entries", labels={"date": "Date", "chart_entries": "Songs charting"},
                      color_discrete_sequence=[CORAL], markers=False)
        chart(fig, 330)
        st.caption("Daily count of this artist’s charting tracks. Multi-artist credits remain grouped as one source entry.")
    st.dataframe(leaderboard.head(50).rename(columns={"artist": "Artist", "chart_appearances": "Chart observations", "average_rank": "Average rank", "best_rank": "Best rank"}), hide_index=True, width="stretch", column_config={"Average rank": st.column_config.NumberColumn(format="%.1f")})

elif view == "Compare":
    section("How does chart position vary with song attributes?", "These are descriptive comparisons across chart observations. They do not establish cause and effect.", "Exploration")
    tab_pop, tab_explicit, tab_release, tab_duration, tab_tracks = st.tabs(["Popularity", "Explicit status", "Album type", "Duration", "Release size"])
    with tab_pop:
        if "popularity" not in filtered:
            empty_state("Popularity is not available in this dataset.")
        else:
            summary = popularity_rank_summary(filtered)
            st.caption(f"Popularity and chart position correlation: {summary['popularity_rank_correlation']:.2f} across {summary['rows']:,} observations. This describes association only; popularity timing and methodology are undocumented.")
            fig = px.scatter(filtered, x="popularity", y="position", color="album_type" if "album_type" in filtered else None,
                             color_discrete_sequence=PALETTE, opacity=.5, hover_data=["song", "artist", "date"],
                             labels={"popularity": "Popularity (0–100)", "position": "Chart position", "album_type": "Album type"})
            rank_axis(fig)
            chart(fig, 500)
    with tab_explicit:
        if "is_explicit" not in filtered:
            empty_state("Explicit status is unavailable in this dataset.")
        else:
            fig = px.box(filtered, x="is_explicit", y="position", color="is_explicit", points=False,
                         color_discrete_map={False: TEAL, True: CORAL},
                         labels={"is_explicit": "Explicit", "position": "Chart position"})
            rank_axis(fig)
            chart(fig, 430)
            st.dataframe(filtered.groupby("is_explicit").agg(observations=("position", "size"), average_rank=("position", "mean"), average_popularity=("popularity", "mean")).reset_index(), hide_index=True, width="stretch", column_config={"average_rank": st.column_config.NumberColumn("Average rank", format="%.1f"), "average_popularity": st.column_config.NumberColumn("Average popularity", format="%.1f")})
    with tab_release:
        if "album_type" not in filtered:
            empty_state("Album type is unavailable in this dataset.")
        else:
            order = filtered.groupby("album_type").position.median().sort_values().index.tolist()
            fig = px.box(filtered, x="album_type", y="position", color="album_type", category_orders={"album_type": order},
                         color_discrete_sequence=PALETTE, points=False,
                         labels={"album_type": "Album type", "position": "Chart position"})
            rank_axis(fig)
            chart(fig, 430)
            st.caption("The compilation category is small in this source; compare its 42 observations with that in mind.")
    with tab_duration:
        if "duration_ms" not in filtered:
            empty_state("Track duration is unavailable in this dataset.")
        else:
            duration = filtered.copy()
            duration["duration_minutes"] = duration["duration_ms"] / 60000
            fig = px.scatter(duration, x="duration_minutes", y="position", color="is_explicit" if "is_explicit" in duration else None,
                             color_discrete_sequence=[TEAL, CORAL], opacity=.45,
                             labels={"duration_minutes": "Track duration (minutes)", "position": "Chart position", "is_explicit": "Explicit"},
                             hover_data=["song", "artist"])
            rank_axis(fig)
            chart(fig, 480)
            st.caption(f"Duration versus rank correlation: {duration['duration_minutes'].corr(duration['position']):.2f}. Descriptive association only.")
    with tab_tracks:
        if "total_tracks" not in filtered:
            empty_state("Release track count is unavailable in this dataset.")
        else:
            fig = px.scatter(filtered, x="total_tracks", y="popularity" if "popularity" in filtered else "position",
                             color="album_type" if "album_type" in filtered else None, color_discrete_sequence=PALETTE,
                             opacity=.45, hover_data=["song", "artist"],
                             labels={"total_tracks": "Tracks on release", "popularity": "Popularity (0–100)", "position": "Chart position", "album_type": "Album type"})
            if "popularity" not in filtered:
                rank_axis(fig)
            chart(fig, 480)
            metric = "popularity" if "popularity" in filtered else "position"
            if "popularity" in filtered:
                st.caption(f"Release size versus popularity correlation: {filtered['total_tracks'].corr(filtered['popularity']):.2f}; versus rank: {filtered['total_tracks'].corr(filtered['position']):.2f}. These are descriptive associations, not causal estimates.")
            else:
                st.caption(f"Release size versus rank correlation: {filtered['total_tracks'].corr(filtered['position']):.2f}. This is not a causal estimate.")

else:  # Data quality
    section("Data quality and coverage", "The dashboard preserves the source and excludes malformed chart dates from ranking analysis.", "Trust & coverage")
    q1, q2, q3, q4 = st.columns(4)
    q1.metric("Raw rows", f"{raw_row_count:,}")
    q2.metric("Exact duplicates removed", f"{raw_row_count - len(data) - int(invalid_dates['rows'].sum()) if not invalid_dates.empty else raw_row_count - len(data):,}")
    q3.metric("Dates excluded", f"{len(invalid_dates):,}")
    q4.metric("Dates analyzed", f"{data['date'].nunique():,}")
    if not invalid_dates.empty:
        st.warning("One or more chart dates do not contain exactly one row at every position from 1 to 50. They are excluded from all rank and trend analysis.")
        st.dataframe(invalid_dates.rename(columns={"date": "Date", "rows": "Rows after exact deduplication", "unique_positions": "Unique positions", "min_position": "Lowest rank", "max_position": "Highest rank", "duplicate_positions": "Extra rank collisions", "is_valid": "Valid snapshot"}), hide_index=True, width="stretch")
    else:
        st.success("Every date contains exactly 50 unique chart positions.")
    st.write("")
    section("Source profile")
    profile, source_dates = source_profile(str(data_path))
    st.dataframe(profile, hide_index=True, width="stretch")
    if source_dates.notna().any():
        expected_days = pd.date_range(source_dates.min(), source_dates.max(), freq="D")
        missing_days = expected_days.difference(pd.DatetimeIndex(source_dates.dropna().unique()))
        st.caption(f"Source date coverage: {source_dates.min():%b %d, %Y} to {source_dates.max():%b %d, %Y}. Missing calendar dates: {len(missing_days)}. These may reflect source collection gaps.")
        if len(missing_days):
            with st.expander("Show dates with no source observation"):
                st.write(", ".join(day.strftime("%b %d, %Y") for day in missing_days))
    if validation_issues:
        with st.expander("Validation notes"):
            for issue in validation_issues:
                st.write(f"- {issue}")
    with st.expander("How to read the metrics"):
        st.markdown("""
        - **Observed days on chart:** distinct dates this song appears in the included source rows; this does not guarantee continuous chart presence.
        - **Average and best rank:** arithmetic mean and minimum of observed chart positions; position 1 is best.
        - **Rank volatility:** standard deviation of observed positions; zero means no variation in the included observations.
        - **Artist presence:** count of chart rows credited to an artist. Combined credits are left intact.
        - **Popularity:** source-provided score on a 0–100 scale. Its timestamp and calculation are unknown.
        - **Invalid-date policy:** exact duplicate rows are dropped in memory; any date not containing one unique entry at every rank 1–50 is excluded from analysis and listed above.
        """)

st.markdown("<div class='small-note' style='text-align:center;margin-top:36px'>United States Top 50 Playlist Performance and Song Popularity Trend Analysis · descriptive analysis of supplied observations</div>", unsafe_allow_html=True)
