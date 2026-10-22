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
artist_dominance_over_time = analysis.artist_dominance_over_time
chart_transition_details = analysis.chart_transition_details
daily_chart_transitions = analysis.daily_chart_transitions
daily_rank_distribution = analysis.daily_rank_distribution
daily_summary = analysis.daily_summary
filter_chart_data = analysis.filter_chart_data
popularity_by_rank_cohort = analysis.popularity_by_rank_cohort
popularity_rank_summary = analysis.popularity_rank_summary
popularity_stability_summary = analysis.popularity_stability_summary
rank_movement = analysis.rank_movement
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
      [data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] label { padding:8px 10px; margin:2px 0; border:1px solid transparent; border-radius:6px; transition:background .15s ease,border-color .15s ease; }
      [data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] label:hover { background:#181C24; border-color:#252B38; }
      [data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] label:has(input:checked) { background:#1D2026; border-color:#2E3646; }
      [data-testid="stSidebar"] input[type="radio"] { accent-color:#00DCE6; }
      [data-testid="stSidebar"] hr { border-color:#252B38; }
      [data-testid="stSegmentedControl"] { background:#12151B; border:1px solid #252B38; border-radius:6px; padding:4px; }
      [data-testid="stSegmentedControl"] button { color:#B9CACB; border-radius:4px; }
      [data-testid="stSegmentedControl"] button[aria-pressed="true"] { background:#00DCE6; color:#0B0D11; font-weight:700; }
      [data-testid="stTabs"] [role="tablist"] { gap:5px; border-bottom:1px solid #252B38; }
      [data-testid="stTabs"] button[role="tab"] { color:#94A3B8; }
      [data-testid="stTabs"] button[role="tab"][aria-selected="true"] { color:#00DCE6; border-bottom-color:#00DCE6; }
      .st-key-filter_drawer_layout > [data-testid="stLayoutWrapper"] > [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:first-child { flex:0 0 300px !important; min-width:300px !important; max-width:300px !important; }
      .st-key-filter_drawer_layout > [data-testid="stLayoutWrapper"] > [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:last-child { flex:1 1 0 !important; min-width:0 !important; max-width:none !important; }
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

# Sidebar: navigation stays available independently from the floating filter control.
with st.sidebar:
    st.markdown("### ♫  TOP 50 ANALYTICS")
    st.caption("UNITED STATES · HISTORICAL PLAYLIST INTELLIGENCE")
    st.divider()
    st.markdown("**NAVIGATION**")
    selected_page = st.radio(
        "Application sections",
        [
            "Overview dashboard",
            "Playlist trends",
            "Song explorer",
            "Artist analytics",
            "Popularity analysis",
            "Content attributes",
            "Data quality & methodology",
        ],
        label_visibility="collapsed",
        key="navigation_page",
    )

    st.divider()
    st.caption(f"SOURCE  /  {data_path.name}")
    st.caption(f"{data['date'].nunique():,} valid snapshots · {len(data):,} rows")
    st.markdown('<div class="small-note">One anomalous snapshot is excluded from rank analysis. See Data quality & methodology.</div>', unsafe_allow_html=True)

# Global filters open as an inline panel, which moves the analysis column instead
# of covering it. The toggle stays beside the collapsed sidebar navigation.
min_day, max_day = data["date"].min().date(), data["date"].max().date()
if "applied_global_filters" not in st.session_state:
    st.session_state["applied_global_filters"] = {
        "date_range": (min_day, max_day),
        "artists": [],
        "tracks": [],
        "rank_range": (1, 50),
        "album_types": [],
    }

if "global_filter_panel_open" not in st.session_state:
    st.session_state["global_filter_panel_open"] = False
if st.button(
    "Hide filters" if st.session_state["global_filter_panel_open"] else "Filters",
    icon=":material/filter_alt:",
    help="Show or hide global filters",
    key="toggle_global_filters",
    type="primary",
):
    st.session_state["global_filter_panel_open"] = not st.session_state["global_filter_panel_open"]
    st.rerun()

if st.session_state["global_filter_panel_open"]:
    with st.container(key="filter_drawer_layout"):
        filter_column, main_column = st.columns([0.3, 0.7], gap="medium")
        with filter_column:
            with st.container(border=True):
                st.markdown("### Global filters")
                applied_filters = st.session_state["applied_global_filters"]
                artist_options = sorted(data["artist"].dropna().unique().tolist()) if "artist" in data else []
                album_options = sorted(data["album_type"].dropna().unique().tolist()) if "album_type" in data else []
                form_dates = st.date_input(
                    "Date range", value=applied_filters["date_range"], min_value=min_day, max_value=max_day,
                    key="global_date_range",
                )
                form_artists = st.multiselect(
                    "Artist", artist_options, default=applied_filters["artists"], placeholder="All artists",
                    key="global_artists",
                )
                song_options = data[["song", "artist"]].drop_duplicates()
                if form_artists:
                    song_options = song_options[song_options["artist"].isin(form_artists)]
                song_options = song_options.sort_values(["song", "artist"])
                track_options = list(song_options.itertuples(index=False, name=None))
                # Remove songs made unavailable by a changed artist selection before
                # rendering the multiselect, so the control never retains invalid values.
                selected_song_key = "global_songs"
                current_tracks = st.session_state.get(selected_song_key, applied_filters["tracks"])
                valid_tracks = [track for track in current_tracks if track in track_options]
                if valid_tracks != current_tracks:
                    st.session_state[selected_song_key] = valid_tracks
                form_tracks = st.multiselect(
                    "Song", track_options, default=valid_tracks,
                    format_func=lambda x: f"{x[0]} · {x[1]}", placeholder="All songs",
                    help="Artist and song selections are combined immediately.",
                    key="global_songs",
                )
                form_rank_range = st.slider(
                    "Chart position", 1, 50, value=applied_filters["rank_range"],
                    help="Lower numbers represent higher chart positions.", key="global_rank_range",
                )
                form_albums = st.multiselect(
                    "Album type", album_options, default=applied_filters["album_types"],
                    placeholder="All release types", key="global_album_types",
                )
                if isinstance(form_dates, (tuple, list)) and len(form_dates) == 2:
                    applied_start, applied_end = form_dates
                elif isinstance(form_dates, (tuple, list)) and len(form_dates) == 1:
                    applied_start = applied_end = form_dates[0]
                else:
                    applied_start = applied_end = form_dates
                st.session_state["applied_global_filters"] = {
                    "date_range": (applied_start, applied_end),
                    "artists": list(form_artists),
                    "tracks": list(form_tracks),
                    "rank_range": tuple(form_rank_range),
                    "album_types": list(form_albums),
                }
else:
    main_column = st.container()

applied_filters = st.session_state["applied_global_filters"]
start_day, end_day = applied_filters["date_range"]
selected_artists = applied_filters["artists"]
selected_tracks = applied_filters["tracks"]
rank_range = applied_filters["rank_range"]
selected_albums = applied_filters["album_types"]

filtered = filter_chart_data(
    data,
    start_date=start_day,
    end_date=end_day,
    artists=selected_artists,
    tracks=selected_tracks,
    rank_range=rank_range,
    album_types=selected_albums,
)

view = {
    "Overview dashboard": "Overview",
    "Playlist trends": "Trends",
    "Song explorer": "Songs",
    "Artist analytics": "Artists",
    "Popularity analysis": "Popularity",
    "Content attributes": "Attributes",
    "Data quality & methodology": "Data quality",
}[selected_page]

# Main analysis area: current section, reporting window, then the selected charts.
with main_column:
    st.markdown(
        f"""
        <div class="hero">
          <div class="hero-eyebrow">TOP 50 ANALYTICS · HISTORICAL PLAYLIST INTELLIGENCE</div>
          <h1>{selected_page}</h1>
          <p>United States · Historical playlist intelligence</p>
          <div class="hero-meta">DATA WINDOW  {start_day.strftime('%b %d, %Y')} — {end_day.strftime('%b %d, %Y')} &nbsp; / &nbsp; {len(filtered):,} OBSERVATIONS IN VIEW</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

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
            trend = daily_summary(filtered)
            if "popularity_trend_score" in trend:
                section("Seven-snapshot popularity trend", "Trailing average across up to seven observed snapshots; descriptive smoothing, not a forecast.")
                fig = px.line(trend, x="date", y="popularity_trend_score", labels={"date": "Date", "popularity_trend_score": "Trailing mean popularity"}, color_discrete_sequence=[TEAL])
                fig.update_yaxes(range=[0, 100])
                chart(fig, 300)
            section("Popularity by rank cohort", "Top 10 and Top 20 are cumulative cohorts; Top 50 is the full selected chart population.")
            cohort = popularity_by_rank_cohort(filtered)
            st.dataframe(cohort.rename(columns={"cohort": "Rank cohort", "observations": "Observations", "mean_popularity": "Mean popularity", "median_popularity": "Median popularity"}), hide_index=True, width="stretch", column_config={"Mean popularity": st.column_config.NumberColumn(format="%.1f"), "Median popularity": st.column_config.NumberColumn(format="%.1f")})
            tracks, stability_corr = popularity_stability_summary(filtered)
            section("Popularity stability vs. rank volatility", "Each point is a song–artist pair. Both volatility measures are sample standard deviations across observed dates.")
            if stability_corr is None or tracks.empty:
                empty_state("At least two tracks with repeated popularity and rank observations are needed for this comparison.")
            else:
                st.caption(f"Track-level correlation: {stability_corr:.2f}. Descriptive association only.")
                fig = px.scatter(tracks, x="popularity_volatility", y="rank_volatility", color="average_popularity" if "average_popularity" in tracks else None, color_continuous_scale=[TEAL, GOLD, CORAL], hover_data=["song", "artist", "days_on_chart"], labels={"popularity_volatility": "Popularity volatility", "rank_volatility": "Rank volatility", "average_popularity": "Mean popularity"})
                chart(fig, 380)
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

    elif view == "Trends":
        section("Daily chart signals", "Daily chart position, popularity, and observation volume within the selected filters.", "Chart history")
        daily = daily_summary(filtered).rename(columns={"chart_entries": "chart_observations"})
        t1, t2 = st.columns(2)
        with t1:
            section("Average chart position", "Lower values indicate stronger chart placement; this is the mean of selected observations per date.")
            fig = px.line(daily, x="date", y="average_rank", markers=False,
                          labels={"date": "Date", "average_rank": "Mean chart position"},
                          color_discrete_sequence=[TEAL])
            fig.update_yaxes(range=[50.5, 1], tickmode="array", tickvals=[1, 10, 20, 30, 40, 50])
            chart(fig, 380)
        with t2:
            section("Observations in view", "Counts the rows remaining after the sidebar filters; it is not playlist size unless all filters are cleared.")
            fig = px.area(daily, x="date", y="chart_observations",
                          labels={"date": "Date", "chart_observations": "Selected chart rows"},
                          color_discrete_sequence=[CORAL])
            fig.update_traces(fillcolor="rgba(255,42,133,.14)", line_color=CORAL)
            chart(fig, 380)
        if "average_popularity" in daily:
            section("Popularity signal by date", "The score line is a trailing mean over the latest seven observed snapshots, not a forecast.")
            fig = px.line(daily, x="date", y=["average_popularity", "popularity_trend_score"], markers=False,
                          labels={"date": "Date", "value": "Popularity (0–100)", "variable": "Measure"},
                          color_discrete_map={"average_popularity": GOLD, "popularity_trend_score": TEAL})
            fig.update_yaxes(range=[0, 100])
            chart(fig, 330)
        section("Daily rank distribution", "Counts selected observations in five rank bands. With all 50 tracks selected, each band contains 10 tracks per valid snapshot.")
        band_order = ["1–10", "11–20", "21–30", "31–40", "41–50"]
        distribution = daily_rank_distribution(filtered)
        fig = px.area(distribution, x="date", y="observations", color="rank_band",
                      category_orders={"rank_band": band_order}, color_discrete_sequence=[GOLD, TEAL, "#10B981", "#7C3AED", CORAL],
                      labels={"date": "Date", "observations": "Selected tracks", "rank_band": "Rank band"})
        chart(fig, 350)
        transitions = daily_chart_transitions(filtered)
        section("Observed entries and exits", "Compares adjacent valid calendar-day snapshots only. Gaps and malformed snapshots are skipped, so this does not infer exits during missing dates.")
        if transitions.empty:
            empty_state("No adjacent valid snapshots are available for entry/exit comparisons in this date selection.")
        else:
            transition_long = transitions.melt(id_vars="date", value_vars=["entries", "exits"], var_name="transition", value_name="tracks")
            fig = px.bar(transition_long, x="date", y="tracks", color="transition", barmode="group",
                         color_discrete_map={"entries": TEAL, "exits": CORAL},
                         labels={"date": "Snapshot date", "tracks": "Track count", "transition": "Observed transition"})
            chart(fig, 350)
        transition_details = chart_transition_details(filtered)
        section(
            "Songs entering and leaving",
            "Choose a snapshot date to inspect its song-level changes in the current filtered view. The first date in the selected window has no prior date for comparison; gaps are skipped.",
            "Track-level changes",
        )
        if transition_details.empty:
            empty_state("No song entries or exits can be compared between consecutive valid snapshots in this selection.")
        else:
            transition_dates = sorted(transition_details["date"].unique())
            transition_date = st.selectbox(
                "Snapshot date",
                transition_dates,
                index=len(transition_dates) - 1,
                format_func=lambda day: pd.Timestamp(day).strftime("%b %d, %Y"),
                key="transition_detail_date",
            )
            day_details = transition_details[transition_details["date"].eq(transition_date)]
            entry_rows = day_details.loc[day_details["transition"].eq("Entry"), ["song", "artist", "position"]]
            exit_rows = day_details.loc[day_details["transition"].eq("Exit"), ["song", "artist", "previous_position"]]
            entry_col, exit_col = st.columns(2)
            with entry_col:
                section("Entered the selected view", f"{len(entry_rows):,} song(s) newly present on {pd.Timestamp(transition_date).strftime('%b %d, %Y')}.")
                if entry_rows.empty:
                    st.info("No songs entered on this snapshot.")
                else:
                    st.dataframe(
                        entry_rows.rename(columns={"song": "Song", "artist": "Artist", "position": "Entry rank"}),
                        hide_index=True,
                        width="stretch",
                    )
            with exit_col:
                section("Left the selected view", f"{len(exit_rows):,} song(s) no longer present on {pd.Timestamp(transition_date).strftime('%b %d, %Y')}.")
                if exit_rows.empty:
                    st.info("No songs exited on this snapshot.")
                else:
                    st.dataframe(
                        exit_rows.rename(columns={"song": "Song", "artist": "Artist", "previous_position": "Last rank"}),
                        hide_index=True,
                        width="stretch",
                    )
        movement = rank_movement(filtered)
        latest_date = filtered["date"].max()
        latest_moves = movement.loc[movement["date"].eq(latest_date) & movement["rank_change"].notna()].copy()
        latest_moves["track"] = latest_moves["song"] + " · " + latest_moves["artist"]
        risers = latest_moves[latest_moves["rank_change"] <= -10].nsmallest(10, "rank_change")
        decliners = latest_moves[latest_moves["rank_change"] >= 10].nlargest(10, "rank_change")
        move_left, move_right = st.columns(2)
        with move_left:
            section("Fast risers", "Tracks improving by at least 10 rank places versus the previous consecutive date.")
            st.dataframe(risers[["track", "position", "rank_change"]].rename(columns={"track": "Song · artist", "position": "Current rank", "rank_change": "Rank change"}), hide_index=True, width="stretch")
            if risers.empty:
                st.caption("No tracks meet the 10-place rise threshold on the latest comparable date.")
        with move_right:
            section("Slow decliners", "Tracks falling by at least 10 rank places versus the previous consecutive date.")
            st.dataframe(decliners[["track", "position", "rank_change"]].rename(columns={"track": "Song · artist", "position": "Current rank", "rank_change": "Rank change"}), hide_index=True, width="stretch")
            if decliners.empty:
                st.caption("No tracks meet the 10-place decline threshold on the latest comparable date.")
        section("Song rank trajectories", "The most frequently observed selected songs across the chosen date window.")
        trend_kpis = song_kpis(filtered)
        trend_keys = list(trend_kpis.head(8)[["song", "artist"]].itertuples(index=False, name=None))
        trend_lines = filtered[["date", "position", "song", "artist"]].copy()
        trend_lines = trend_lines[[tuple(x) in set(trend_keys) for x in trend_lines[["song", "artist"]].itertuples(index=False, name=None)]]
        if not trend_lines.empty:
            trend_lines["track"] = trend_lines["song"] + " · " + trend_lines["artist"]
            fig = px.line(trend_lines, x="date", y="position", color="track", color_discrete_sequence=PALETTE,
                          labels={"date": "Date", "position": "Chart position", "track": "Song"})
            rank_axis(fig)
            chart(fig, 430)

    elif view == "Songs":
        section("Selected track", "Inspect a track’s rank history and observed-duration summary in the selected date window.", "Track detail")
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
        st.write("")
        section("Track-level performance comparisons", "Each point represents one song–artist pair in the current filter window.", "Longevity & popularity")
        track_summary = song_kpis(filtered)
        left, right = st.columns([1.2, 1])
        with left:
            scatter_color = "average_popularity" if "average_popularity" in track_summary else None
            fig = px.scatter(track_summary, x="days_on_chart", y="best_rank", color=scatter_color,
                             color_continuous_scale=[TEAL, GOLD, CORAL], opacity=.78,
                             hover_data=["song", "artist", "average_rank"],
                             labels={"days_on_chart": "Observed days on chart", "best_rank": "Best rank",
                                     "average_popularity": "Mean popularity"})
            rank_axis(fig)
            chart(fig, 400)
            st.caption("Peak rank versus observed longevity. A track's observed days may span gaps in source coverage.")
        with right:
            if "average_popularity" in track_summary:
                section("Highest mean popularity", "Average source score per song–artist pair in the current window.")
                popular_tracks = track_summary.nlargest(12, "average_popularity")[["song", "artist", "average_popularity", "days_on_chart"]]
                st.dataframe(popular_tracks.rename(columns={"song": "Song", "artist": "Artist", "average_popularity": "Mean popularity", "days_on_chart": "Observed days"}),
                             hide_index=True, width="stretch",
                             column_config={"Mean popularity": st.column_config.NumberColumn(format="%.1f")})
            else:
                empty_state("Popularity is unavailable; the track popularity leaderboard is skipped.")

    elif view == "Artists":
        section("Artist leaderboard", "Includes chart-row appearances, distinct credited songs, and distinct observed dates. Multi-artist credits remain as supplied.", "Artist detail")
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
        display_columns = [column for column in ["artist", "chart_appearances", "unique_songs", "days_present", "average_rank", "best_rank"] if column in leaderboard]
        st.dataframe(leaderboard.head(50)[display_columns].rename(columns={
            "artist": "Artist", "chart_appearances": "Chart observations", "unique_songs": "Unique songs",
            "days_present": "Observed days present", "average_rank": "Average rank", "best_rank": "Best rank",
        }), hide_index=True, width="stretch", column_config={"Average rank": st.column_config.NumberColumn(format="%.1f")})

        # For a meaningful artist-share denominator, retain the chart population
        # selected by date/rank/song/release filters, but do not apply the artist
        # filter to the denominator. Otherwise selected artists would sum to 100%.
        dominance_population = filter_chart_data(
            data,
            start_date=start_day,
            end_date=end_day,
            tracks=selected_tracks,
            rank_range=rank_range,
            album_types=selected_albums,
        )
        dominance = artist_dominance_over_time(dominance_population)
        section(
            "Artist dominance over time",
            "Daily share of eligible chart slots. Choose artists below to compare; the global artist filter does not shrink the denominator. Collaboration slots are divided equally among credited artists.",
            "Share of voice",
        )
        if dominance.empty:
            empty_state("No artist chart slots are available for this date and filter selection.")
        else:
            artist_totals = dominance.groupby("artist")["credited_slots"].sum().sort_values(ascending=False)
            available_artists = artist_totals.index.tolist()
            defaults_from_global = sorted({
                name
                for credit in selected_artists
                for name in analysis.split_artist_credit(credit)
                if name in available_artists
            })
            default_artists = defaults_from_global or available_artists[:5]
            selection_key = "artist_dominance_selection"
            current_selection = st.session_state.get(selection_key, default_artists)
            valid_selection = [artist for artist in current_selection if artist in available_artists]
            if valid_selection != current_selection:
                st.session_state[selection_key] = valid_selection or default_artists
            compared_artists = st.multiselect(
                "Compare artists",
                available_artists,
                default=valid_selection or default_artists,
                key=selection_key,
                help="Choose multiple credited artists to compare their share of chart slots over time.",
            )
            if compared_artists:
                dates = sorted(dominance_population["date"].dropna().unique())
                share_history = pd.MultiIndex.from_product(
                    [dates, compared_artists], names=["date", "artist"]
                ).to_frame(index=False).merge(
                    dominance[["date", "artist", "share_pct"]],
                    on=["date", "artist"],
                    how="left",
                )
                share_history["share_pct"] = share_history["share_pct"].fillna(0)
                fig = px.line(
                    share_history,
                    x="date",
                    y="share_pct",
                    color="artist",
                    markers=False,
                    color_discrete_sequence=PALETTE,
                    labels={"date": "Date", "share_pct": "Share of eligible chart slots (%)", "artist": "Artist"},
                )
                fig.update_yaxes(rangemode="tozero", ticksuffix="%")
                chart(fig, 420)
                total_eligible_slots = dominance_population.groupby("date").size().sum()
                comparison_summary = (
                    dominance[dominance["artist"].isin(compared_artists)]
                    .groupby("artist", as_index=False)["credited_slots"].sum()
                )
                comparison_summary["average_share_pct"] = comparison_summary["credited_slots"] / total_eligible_slots * 100
                st.dataframe(
                    comparison_summary.rename(columns={"artist": "Artist", "credited_slots": "Weighted chart slots", "average_share_pct": "Average share (%)"}),
                    hide_index=True,
                    width="stretch",
                    column_config={"Weighted chart slots": st.column_config.NumberColumn(format="%.1f"), "Average share (%)": st.column_config.NumberColumn(format="%.2f%%")},
                )
            else:
                st.info("Select at least one artist to display the comparison.")

    elif view == "Popularity":
        section("Popularity score snapshot", "Explore the source-provided popularity score and its descriptive relationship with chart position.", "Popularity signal")
        if "popularity" not in filtered:
            empty_state("Popularity is not available in this dataset, so popularity analyses are skipped.")
        else:
            popularity_mean = filtered["popularity"].mean()
            popularity_median = filtered["popularity"].median()
            popularity_std = filtered["popularity"].std()
            popularity_corr = popularity_rank_summary(filtered)["popularity_rank_correlation"]
            p1, p2, p3, p4 = st.columns(4)
            p1.metric("Mean score", f"{popularity_mean:.1f} / 100")
            p2.metric("Median score", f"{popularity_median:.1f} / 100")
            p3.metric("Score standard deviation", f"{popularity_std:.1f}" if pd.notna(popularity_std) else "—")
            p4.metric("Score vs. rank correlation", f"{popularity_corr:.2f}" if pd.notna(popularity_corr) else "—", help="Descriptive association only. Correlation does not establish cause and effect.")
            p_left, p_right = st.columns(2)
            with p_left:
                section("Popularity score distribution", "Distribution across selected chart observations.")
                fig = px.histogram(filtered, x="popularity", nbins=20,
                                   labels={"popularity": "Popularity (0–100)", "count": "Observations"},
                                   color_discrete_sequence=[TEAL])
                chart(fig, 390)
            with p_right:
                section("Popularity versus rank", "Rank 1 is at the top of the vertical axis. Association is descriptive, not causal.")
                fig = px.scatter(filtered, x="popularity", y="position",
                                 color="album_type" if "album_type" in filtered else None,
                                 color_discrete_sequence=PALETTE, opacity=.48,
                                 hover_data=["song", "artist", "date"],
                                 labels={"popularity": "Popularity (0–100)", "position": "Chart position", "album_type": "Album type"})
                rank_axis(fig)
                chart(fig, 390)
            daily_popularity = filtered.groupby("date", as_index=False).agg(average_popularity=("popularity", "mean"))
            section("Popularity through time", "The source does not document when or how each popularity score was generated.")
            fig = px.line(daily_popularity, x="date", y="average_popularity",
                          labels={"date": "Date", "average_popularity": "Mean popularity (0–100)"},
                          color_discrete_sequence=[GOLD])
            fig.update_yaxes(range=[0, 100])
            chart(fig, 330)

            trend = daily_summary(filtered)
            if "popularity_trend_score" in trend:
                section("Seven-snapshot popularity trend", "Trailing average across up to seven observed snapshots; descriptive smoothing, not a forecast.")
                fig = px.line(trend, x="date", y="popularity_trend_score", labels={"date": "Date", "popularity_trend_score": "Trailing mean popularity"}, color_discrete_sequence=[TEAL])
                fig.update_yaxes(range=[0, 100])
                chart(fig, 300)
            section("Popularity by rank cohort", "Top 10 and Top 20 are cumulative cohorts; Top 50 is the full selected chart population.")
            cohort = popularity_by_rank_cohort(filtered)
            st.dataframe(cohort.rename(columns={"cohort": "Rank cohort", "observations": "Observations", "mean_popularity": "Mean popularity", "median_popularity": "Median popularity"}), hide_index=True, width="stretch", column_config={"Mean popularity": st.column_config.NumberColumn(format="%.1f"), "Median popularity": st.column_config.NumberColumn(format="%.1f")})
            tracks, stability_corr = popularity_stability_summary(filtered)
            section("Popularity stability vs. rank volatility", "Each point is a song–artist pair. Both volatility measures are sample standard deviations across observed dates.")
            if stability_corr is None or tracks.empty:
                empty_state("At least two tracks with repeated popularity and rank observations are needed for this comparison.")
            else:
                st.caption(f"Track-level correlation: {stability_corr:.2f}. Descriptive association only.")
                fig = px.scatter(tracks, x="popularity_volatility", y="rank_volatility", color="average_popularity" if "average_popularity" in tracks else None, color_continuous_scale=[TEAL, GOLD, CORAL], hover_data=["song", "artist", "days_on_chart"], labels={"popularity_volatility": "Popularity volatility", "rank_volatility": "Rank volatility", "average_popularity": "Mean popularity"})
                chart(fig, 380)

    elif view == "Attributes":
        section("Attribute comparisons", "Compare chart rank across explicit status, release format, track duration, and release size.", "Track metadata")
        tab_explicit, tab_release, tab_duration, tab_tracks = st.tabs(["Explicit status", "Album type", "Duration", "Release size"])
        with tab_explicit:
            if "is_explicit" not in filtered:
                empty_state("Explicit status is unavailable in this dataset.")
            else:
                fig = px.box(filtered, x="is_explicit", y="position", color="is_explicit", points=False,
                             color_discrete_map={False: TEAL, True: CORAL},
                             labels={"is_explicit": "Explicit", "position": "Chart position"})
                rank_axis(fig)
                chart(fig, 430)
                explicit_metrics = {"observations": ("position", "size"), "average_rank": ("position", "mean")}
                if "popularity" in filtered:
                    explicit_metrics["average_popularity"] = ("popularity", "mean")
                explicit_summary = filtered.groupby("is_explicit").agg(**explicit_metrics).reset_index()
                st.dataframe(explicit_summary, hide_index=True, width="stretch", column_config={"average_rank": st.column_config.NumberColumn("Average rank", format="%.1f"), "average_popularity": st.column_config.NumberColumn("Average popularity", format="%.1f")})
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
                counts = filtered["album_type"].value_counts().to_dict()
                st.caption("Filtered observations by release type: " + " · ".join(f"{kind}: {count:,}" for kind, count in counts.items()))
        with tab_duration:
            if "duration_ms" not in filtered:
                empty_state("Track duration is unavailable in this dataset.")
            else:
                duration = filtered.copy()
                if "duration_minutes" not in duration:
                    duration["duration_minutes"] = duration["duration_ms"] / 60000
                fig = px.scatter(duration, x="duration_minutes", y="position", color="is_explicit" if "is_explicit" in duration else None,
                                 color_discrete_sequence=[TEAL, CORAL], opacity=.45,
                                 labels={"duration_minutes": "Track duration (minutes)", "position": "Chart position", "is_explicit": "Explicit"},
                                 hover_data=["song", "artist"])
                rank_axis(fig)
                chart(fig, 480)
                st.caption(f"Duration versus rank correlation: {duration['duration_minutes'].corr(duration['position']):.2f}. Descriptive association only.")
                if "popularity" in duration:
                    section("Duration versus popularity", "Popularity is the source-provided score; its capture time is undocumented.")
                    fig = px.scatter(duration, x="duration_minutes", y="popularity", color="album_type" if "album_type" in duration else None, color_discrete_sequence=PALETTE, opacity=.45, hover_data=["song", "artist"], labels={"duration_minutes": "Track duration (minutes)", "popularity": "Popularity (0–100)", "album_type": "Album type"})
                    chart(fig, 380)
                    st.caption(f"Duration versus popularity correlation: {duration['duration_minutes'].corr(duration['popularity']):.2f}. Descriptive association only.")
        with tab_tracks:
            if "total_tracks" not in filtered:
                empty_state("Release track count is unavailable in this dataset.")
            else:
                metric_column = "popularity" if "popularity" in filtered else "position"
                fig = px.scatter(filtered, x="total_tracks", y=metric_column,
                                 color="album_type" if "album_type" in filtered else None, color_discrete_sequence=PALETTE,
                                 opacity=.45, hover_data=["song", "artist"],
                                 labels={"total_tracks": "Tracks on release", "popularity": "Popularity (0–100)", "position": "Chart position", "album_type": "Album type"})
                if "popularity" not in filtered:
                    rank_axis(fig)
                chart(fig, 480)
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
