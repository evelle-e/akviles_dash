import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

st.set_page_config(layout="wide", page_title="Akvilės Spotify", page_icon="🎵")

# ── Global styles ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
  .stApp { background-color: #121212; color: #FFFFFF; }
  [data-testid="stSidebar"] { background-color: #000000; }

  [data-testid="stMetric"] {
    background: #1A1A1A;
    border: 1px solid #282828;
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 8px;
  }
  [data-testid="stMetricLabel"] { color: #B3B3B3 !important; font-size: 0.78rem; }
  [data-testid="stMetricValue"] { color: #FFFFFF !important; font-size: 1.6rem; font-weight: 700; }

  .stTabs [data-baseweb="tab-list"] { background: #000000; gap: 4px; }
  .stTabs [data-baseweb="tab"] {
    background: transparent;
    color: #B3B3B3;
    border-radius: 20px;
    padding: 8px 20px;
    font-weight: 600;
    font-size: 0.85rem;
    letter-spacing: 0.05em;
  }
  .stTabs [aria-selected="true"] { background: #1DB954 !important; color: #000000 !important; }

  /* Year card styling */
  .year-card {
    background: #1A1A1A;
    border: 1px solid #282828;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
  }
  .year-card .year { color: #1DB954; font-size: 0.9rem; font-weight: 700; letter-spacing: 0.1em; }
  .year-card .track { color: #FFFFFF; font-size: 1rem; font-weight: 700; margin: 6px 0 2px; }
  .year-card .mins { color: #B3B3B3; font-size: 0.8rem; }

  h1, h2, h3 { color: #FFFFFF; }
  hr { border-color: #282828; }
  .block-container { padding-top: 2rem; }
</style>
""", unsafe_allow_html=True)

# ── Plotly shared theme ────────────────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="#181818",
    plot_bgcolor="#181818",
    font=dict(family="Helvetica, Arial, sans-serif", color="#B3B3B3", size=12),
    title_font=dict(color="#FFFFFF", size=15),
    xaxis=dict(gridcolor="#282828", zerolinecolor="#282828", tickfont=dict(color="#B3B3B3")),
    yaxis=dict(gridcolor="#282828", zerolinecolor="#282828", tickfont=dict(color="#B3B3B3")),
    margin=dict(t=50, b=40, l=10, r=10),
)
GREEN = "#1DB954"
GREY = "#535353"
GREEN_SCALE = [[0, "#181818"], [0.3, "#158a3e"], [1, "#1DB954"]]


def style(fig, **overrides):
    fig.update_layout(**{**PLOTLY_LAYOUT, **overrides})
    return fig


# ── Data ───────────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    files = [
        "Streaming_History_Audio_2023.csv",
        "Streaming_History_Audio_2024.csv",
        "Streaming_History_Audio_2024_1.csv",
        "Streaming_History_Audio_2025.csv",
        "Streaming_History_Audio_2025_1.csv",
        "Streaming_History_Audio_2026.csv",
    ]
    df = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
    df = df.drop(columns=[
        "platform", "ip_addr", "episode_name", "episode_show_name",
        "spotify_episode_uri", "audiobook_title", "audiobook_uri",
        "audiobook_chapter_uri", "audiobook_chapter_title",
        "offline", "offline_timestamp", "incognito_mode",
    ], errors="ignore")
    df["ms_played"] = df["ms_played"] / 1000
    df["ts"] = pd.to_datetime(df["ts"])
    df["year"] = df["ts"].dt.year
    df["month"] = df["ts"].dt.month
    df["weekday"] = df["ts"].dt.day_name()
    df["hour"] = df["ts"].dt.hour
    df["min_played"] = df["ms_played"] / 60
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    df["weekday"] = pd.Categorical(df["weekday"], categories=day_order, ordered=True)
    df = df.dropna(subset=["master_metadata_track_name"])
    return df


df_all = load_data()

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎵 Akvilės Spotify")
    st.markdown("<span style='color:#B3B3B3;font-size:0.8rem'>Streaming history · 2023–2026</span>",
                unsafe_allow_html=True)
    st.divider()

    years = sorted(df_all["year"].unique())
    year_options = ["All years"] + [str(y) for y in years]
    selected_year = st.selectbox("Filter by year", year_options, index=0)

    df = df_all if selected_year == "All years" else df_all[df_all["year"] == int(selected_year)].copy()
    df_vacation = df[(df["conn_country"] != "LT") & (df["conn_country"] != "US")].copy()

    st.divider()
    st.metric("Listening time", f"{df['min_played'].sum() / 60:,.0f} hrs")
    st.metric("Total streams", f"{len(df):,}")
    st.metric("Unique artists", f"{df['master_metadata_album_artist_name'].nunique():,}")
    st.metric("Unique tracks", f"{df['master_metadata_track_name'].nunique():,}")
    st.divider()
    st.markdown("<span style='color:#535353;font-size:0.75rem'>Built with Streamlit · Data from Spotify</span>",
                unsafe_allow_html=True)

# ── Page title ─────────────────────────────────────────────────────────────────
subtitle = "3 years of streaming data, visualised." if selected_year == "All years" else f"Showing data for {selected_year} only."
st.markdown(f"""
<h1 style='font-size:2.4rem; margin-bottom:0'>🎧 My Spotify Wrapped</h1>
<p style='color:#B3B3B3; margin-top:4px; margin-bottom:24px'>{subtitle}</p>
""", unsafe_allow_html=True)

tab_time, tab_top, tab_vacation, tab_skips, tab_records, tab_history = st.tabs([
    "📅  When Do I Listen?",
    "🏆  My Top Music",
    "✈️  Vacation Soundtrack",
    "⏭️  What I Skip",
    "🏅  Records & Milestones",
    "📆  This Day in History",
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — When Do I Listen?
# ══════════════════════════════════════════════════════════════════════════════
with tab_time:

    # Row 1: day-of-week + hour-of-day
    col1, col2 = st.columns(2, gap="large")
    with col1:
        df_day = df.groupby("weekday", observed=False)["min_played"].sum().reset_index()
        fig = px.bar(df_day, x="weekday", y="min_played",
                     labels={"weekday": "", "min_played": "Minutes"},
                     color_discrete_sequence=[GREEN])
        fig.update_traces(marker_line_width=0,
                          hovertemplate="<b>%{x}</b><br>%{y:,.0f} min<extra></extra>")
        style(fig, title="Which day do I listen most?")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        df_hourly = df.groupby("hour")["min_played"].sum().reset_index()
        fig = go.Figure(go.Scatter(
            x=df_hourly["hour"], y=df_hourly["min_played"],
            mode="lines", line=dict(color=GREEN, width=3),
            fill="tozeroy", fillcolor="rgba(29,185,84,0.12)",
            hovertemplate="<b>%{x}:00</b><br>%{y:,.0f} min<extra></extra>",
        ))
        fig.update_xaxes(tickvals=list(range(0, 24, 3)),
                         ticktext=[f"{h:02d}:00" for h in range(0, 24, 3)])
        style(fig, title="What time of day do I listen most?",
              xaxis_title="", yaxis_title="Minutes")
        st.plotly_chart(fig, use_container_width=True)

    # Calendar heatmap
    st.markdown("#### Every single day, for 3 years")
    st.caption("Each square is one day — darker green means more listening.")

    daily = (df.assign(date=df["ts"].dt.normalize())
               .groupby("date")["min_played"].sum()
               .reset_index())
    daily["year"] = daily["date"].dt.year
    daily["dayofweek"] = daily["date"].dt.dayofweek       # 0 = Monday
    daily["weekofyear"] = daily["date"].dt.dayofyear // 7  # 0–51

    years = sorted(daily["year"].unique())
    day_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    fig = make_subplots(rows=len(years), cols=1,
                        subplot_titles=[str(y) for y in years],
                        vertical_spacing=0.1)

    for i, year in enumerate(years, 1):
        yr = daily[daily["year"] == year]
        grid = pd.DataFrame(0.0, index=range(7), columns=range(53))
        for _, row in yr.iterrows():
            w = min(int(row["weekofyear"]), 52)
            grid.loc[int(row["dayofweek"]), w] = row["min_played"]

        hover = [[f"{day_labels[d]}, week {w+1}<br><b>{grid.loc[d, w]:.0f} min</b>"
                  for w in range(53)] for d in range(7)]

        fig.add_trace(
            go.Heatmap(
                z=grid.values,
                text=hover,
                hovertemplate="%{text}<extra></extra>",
                colorscale=GREEN_SCALE,
                showscale=(i == len(years)),
                xgap=3, ygap=3,
                coloraxis="coloraxis",
            ),
            row=i, col=1,
        )
        fig.update_yaxes(tickvals=list(range(7)), ticktext=day_labels,
                         tickfont=dict(color="#B3B3B3"), row=i, col=1)
        fig.update_xaxes(showticklabels=False, row=i, col=1)

    for ann in fig.layout.annotations:
        ann.font.color = "#FFFFFF"
        ann.font.size = 13

    fig.update_layout(
        height=420,
        paper_bgcolor="#181818",
        plot_bgcolor="#181818",
        margin=dict(t=30, b=10, l=60, r=20),
        coloraxis=dict(colorscale=GREEN_SCALE,
                       colorbar=dict(tickfont=dict(color="#B3B3B3"),
                                     title=dict(text="min", font=dict(color="#B3B3B3")))),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Month + Year row
    col1, col2 = st.columns(2, gap="large")
    with col1:
        month_names = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",
                       7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}
        df_month = df.groupby("month")["min_played"].sum().reset_index()
        df_month["month_name"] = df_month["month"].map(month_names)
        fig = px.bar(df_month, x="month_name", y="min_played",
                     labels={"month_name": "", "min_played": "Minutes"},
                     color_discrete_sequence=[GREEN],
                     category_orders={"month_name": list(month_names.values())})
        fig.update_traces(marker_line_width=0,
                          hovertemplate="<b>%{x}</b><br>%{y:,.0f} min<extra></extra>")
        style(fig, title="Which month do I listen most?")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        df_year = df.groupby("year")["min_played"].sum().reset_index()
        df_year["hours"] = df_year["min_played"] / 60
        fig = px.bar(df_year, x="year", y="hours",
                     labels={"year": "", "hours": "Hours"},
                     color_discrete_sequence=[GREEN],
                     text=df_year["hours"].apply(lambda h: f"{h:,.0f} hrs"))
        fig.update_traces(marker_line_width=0, textposition="outside",
                          textfont=dict(color="#FFFFFF"),
                          hovertemplate="<b>%{x}</b><br>%{y:,.0f} hrs<extra></extra>")
        fig.update_xaxes(type="category")
        style(fig, title="How much did I listen each year?", yaxis_title="Hours")
        st.caption("2023 starts in February · 2026 data goes up to May.")
        st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — My Top Music
# ══════════════════════════════════════════════════════════════════════════════
with tab_top:

    # Top N bar charts
    n = st.slider("Show top", min_value=5, max_value=25, value=10, step=5,
                  format="%d entries")
    col1, col2, col3 = st.columns(3, gap="large")

    def top_bar(data, y_col, title):
        fig = px.bar(data, x="Minutes", y=y_col, orientation="h",
                     color_discrete_sequence=[GREEN])
        fig.update_traces(marker_line_width=0,
                          hovertemplate=f"<b>%{{y}}</b><br>%{{x:,.0f}} min<extra></extra>")
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        style(fig, title=title, xaxis_title="Minutes", yaxis_title="")
        return fig

    with col1:
        d = (df.groupby("master_metadata_album_artist_name")["min_played"]
             .sum().sort_values(ascending=False).head(n).reset_index())
        d.columns = ["Artist", "Minutes"]
        st.plotly_chart(top_bar(d, "Artist", f"My top {n} artists"), use_container_width=True)

    with col2:
        d = (df.groupby("master_metadata_track_name")["min_played"]
             .sum().sort_values(ascending=False).head(n).reset_index())
        d.columns = ["Track", "Minutes"]
        st.plotly_chart(top_bar(d, "Track", f"My top {n} tracks"), use_container_width=True)

    with col3:
        d = (df.groupby("master_metadata_album_album_name")["min_played"]
             .sum().sort_values(ascending=False).head(n).reset_index())
        d.columns = ["Album", "Minutes"]
        st.plotly_chart(top_bar(d, "Album", f"My top {n} albums"), use_container_width=True)

    st.divider()

    # #1 Track each year + One-hit wonders
    col1, col2 = st.columns([3, 2], gap="large")

    with col1:
        st.markdown("#### My most-played track each year")
        top_per_year = (df.groupby(["year", "master_metadata_track_name"])["min_played"]
                        .sum().reset_index()
                        .sort_values("min_played", ascending=False)
                        .groupby("year").first()
                        .reset_index())

        cards_html = "<div style='display:flex; gap:12px; flex-wrap:wrap;'>"
        for _, row in top_per_year.iterrows():
            track = row["master_metadata_track_name"]
            # Truncate long names
            display = track if len(track) <= 28 else track[:26] + "…"
            cards_html += f"""
            <div class='year-card' style='flex:1; min-width:120px;'>
              <div class='year'>{int(row['year'])}</div>
              <div class='track'>{display}</div>
              <div class='mins'>{row['min_played']:,.0f} min</div>
            </div>"""
        cards_html += "</div>"
        st.markdown(cards_html, unsafe_allow_html=True)

    with col2:
        st.markdown("#### One-hit wonders")
        st.caption("Artists you only ever played once.")

        play_counts = (df.dropna(subset=["master_metadata_album_artist_name"])
                         .groupby("master_metadata_album_artist_name")["ts"]
                         .count())
        one_timers = play_counts[play_counts == 1]
        st.metric("Artists played exactly once", f"{len(one_timers):,}")

        # Show a few examples with the track they played
        sample = (df[df["master_metadata_album_artist_name"].isin(one_timers.index)]
                    [["master_metadata_album_artist_name", "master_metadata_track_name"]]
                    .drop_duplicates("master_metadata_album_artist_name")
                    .sample(min(8, len(one_timers)), random_state=42))
        sample.columns = ["Artist", "Track played"]
        st.dataframe(
            sample.reset_index(drop=True),
            hide_index=True,
            use_container_width=True,
            column_config={
                "Artist": st.column_config.TextColumn("Artist"),
                "Track played": st.column_config.TextColumn("Track played"),
            },
        )

    st.divider()

    # Discovery timeline
    st.markdown("#### New artists I discovered each month")
    st.caption("How many artists did you hear for the very first time that month?")

    first_heard = (df.dropna(subset=["master_metadata_album_artist_name"])
                     .groupby("master_metadata_album_artist_name")["ts"]
                     .min().reset_index())
    first_heard["year_month"] = first_heard["ts"].dt.to_period("M").astype(str)
    discoveries = (first_heard.groupby("year_month").size()
                              .reset_index(name="New artists")
                              .sort_values("year_month"))

    fig = px.bar(discoveries, x="year_month", y="New artists",
                 labels={"year_month": "", "New artists": "New artists"},
                 color_discrete_sequence=[GREEN])
    fig.update_traces(marker_line_width=0,
                      hovertemplate="<b>%{x}</b><br>%{y} new artists<extra></extra>")
    fig.update_xaxes(tickangle=-45)
    style(fig, title="")
    st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Vacation Soundtrack
# ══════════════════════════════════════════════════════════════════════════════
with tab_vacation:
    c1, c2, c3 = st.columns(3)
    c1.metric("Vacation streams", f"{len(df_vacation):,}")
    c2.metric("Listening time", f"{df_vacation['min_played'].sum():,.0f} min")
    c3.metric("Countries visited", f"{df_vacation['conn_country'].nunique()}")

    st.markdown("<br>", unsafe_allow_html=True)

    iso2_to_name = {"CY": "Cyprus", "ES": "Spain", "GB": "United Kingdom",
                    "GR": "Greece", "PL": "Poland"}

    # Country cards
    country_mins = df_vacation.groupby("conn_country")["min_played"].sum()
    country_top_track = (df_vacation.groupby(["conn_country", "master_metadata_track_name"])["min_played"]
                         .sum().reset_index()
                         .sort_values("min_played", ascending=False)
                         .groupby("conn_country")["master_metadata_track_name"].first())
    country_top_artist = (df_vacation.groupby(["conn_country", "master_metadata_album_artist_name"])["min_played"]
                          .sum().reset_index()
                          .sort_values("min_played", ascending=False)
                          .groupby("conn_country")["master_metadata_album_artist_name"].first())

    flag = {"CY": "🇨🇾", "ES": "🇪🇸", "GB": "🇬🇧", "GR": "🇬🇷", "PL": "🇵🇱"}

    cards_html = "<div style='display:flex; gap:12px; flex-wrap:wrap; margin-bottom:24px'>"
    for code in country_mins.sort_values(ascending=False).index:
        name  = iso2_to_name.get(code, code)
        mins  = country_mins[code]
        track = country_top_track.get(code, "—")
        artist = country_top_artist.get(code, "—")
        track_display = track if len(track) <= 24 else track[:22] + "…"
        cards_html += f"""
        <div style='flex:1; min-width:140px; background:#1A1A1A; border:1px solid #282828;
                    border-radius:12px; padding:20px 18px;'>
          <div style='font-size:2rem; line-height:1'>{flag.get(code,'🌍')}</div>
          <div style='color:#FFFFFF; font-size:1.1rem; font-weight:700;
                      margin:8px 0 2px'>{name}</div>
          <div style='color:#1DB954; font-size:1.4rem; font-weight:700;
                      margin-bottom:10px'>{mins:,.0f} <span style='font-size:0.8rem;
                      color:#B3B3B3; font-weight:400'>min</span></div>
          <div style='color:#B3B3B3; font-size:0.75rem; margin-bottom:2px'>TOP TRACK</div>
          <div style='color:#FFFFFF; font-size:0.85rem; font-weight:600'>{track_display}</div>
          <div style='color:#B3B3B3; font-size:0.8rem'>{artist}</div>
        </div>"""
    cards_html += "</div>"
    st.markdown(cards_html, unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        top_vac = (df_vacation.groupby("master_metadata_track_name")["min_played"]
                   .sum().sort_values(ascending=False).head(10).reset_index())
        top_vac.columns = ["Track", "Minutes"]
        fig = px.bar(top_vac, x="Minutes", y="Track", orientation="h",
                     color_discrete_sequence=[GREEN],
                     labels={"Track": "", "Minutes": "Minutes"})
        fig.update_traces(marker_line_width=0,
                          hovertemplate="<b>%{y}</b><br>%{x:,.0f} min<extra></extra>")
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        style(fig, title="My vacation soundtrack — top 10 tracks")
        st.plotly_chart(fig, use_container_width=True)

    # Top artist per country
    st.markdown("#### Who did I listen to in each country?")
    top_by_country = (df_vacation
                      .groupby(["conn_country", "master_metadata_album_artist_name"])["min_played"]
                      .sum().reset_index()
                      .sort_values("min_played", ascending=False)
                      .groupby("conn_country").first()
                      .reset_index())
    top_by_country["Country"] = top_by_country["conn_country"].map(iso2_to_name)
    top_by_country = top_by_country.rename(
        columns={"master_metadata_album_artist_name": "Top artist",
                 "min_played": "Minutes"}
    )[["Country", "Top artist", "Minutes"]].sort_values("Minutes", ascending=False)
    top_by_country["Minutes"] = top_by_country["Minutes"].apply(lambda m: f"{m:,.0f} min")

    st.dataframe(
        top_by_country.reset_index(drop=True),
        hide_index=True,
        use_container_width=True,
        column_config={
            "Country": st.column_config.TextColumn("Country"),
            "Top artist": st.column_config.TextColumn("Top artist"),
            "Minutes": st.column_config.TextColumn("Time"),
        },
    )



# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — What I Skip
# ══════════════════════════════════════════════════════════════════════════════
with tab_skips:
    skipped = int(df["skipped"].sum())
    completed = len(df) - skipped
    c1, c2, c3 = st.columns(3)
    c1.metric("Songs I finished", f"{completed:,}")
    c2.metric("Songs I skipped", f"{skipped:,}")
    c3.metric("Skip rate", f"{skipped / len(df) * 100:.1f}%")

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2, gap="large")

    with col1:
        fig = go.Figure(go.Pie(
            labels=["Finished", "Skipped"],
            values=[completed, skipped],
            hole=0.55,
            marker=dict(colors=[GREEN, GREY], line=dict(color="#121212", width=2)),
            hovertemplate="<b>%{label}</b><br>%{value:,} songs (%{percent})<extra></extra>",
            textfont=dict(color="#FFFFFF"),
        ))
        fig.add_annotation(
            text=f"<b>{skipped / len(df) * 100:.0f}%</b><br><span style='font-size:11px'>skipped</span>",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=20, color="#FFFFFF"),
        )
        style(fig, title="Do I actually listen to what I play?",
              showlegend=True, legend=dict(font=dict(color="#B3B3B3")))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        quick_skips = (df[df["ms_played"] < 10]
                       .groupby("master_metadata_track_name")["master_metadata_track_name"]
                       .count().sort_values(ascending=False).head(10)
                       .reset_index(name="count"))
        quick_skips.columns = ["Track", "Skips"]
        fig = px.bar(quick_skips, x="Skips", y="Track", orientation="h",
                     color_discrete_sequence=[GREY],
                     labels={"Track": "", "Skips": "Times skipped in under 10 seconds"})
        fig.update_traces(marker_line_width=0,
                          hovertemplate="<b>%{y}</b><br>%{x} quick skips<extra></extra>")
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        style(fig, title="Most skipped songs")
        st.plotly_chart(fig, use_container_width=True)



# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — Records & Milestones
# ══════════════════════════════════════════════════════════════════════════════
with tab_records:

    def milestone_card(emoji, label, value, sub=""):
        sub_html = f"<div style='color:#B3B3B3;font-size:0.78rem;margin-top:4px'>{sub}</div>" if sub else ""
        st.markdown(f"""
        <div style='background:#1A1A1A;border:1px solid #282828;border-radius:12px;
                    padding:20px 24px;margin-bottom:8px;'>
          <div style='color:#B3B3B3;font-size:0.78rem;margin-bottom:6px'>{emoji} {label}</div>
          <div style='color:#FFFFFF;font-size:1.3rem;font-weight:700;line-height:1.3'>{value}</div>
          {sub_html}
        </div>""", unsafe_allow_html=True)

    # ── Pre-compute milestones ─────────────────────────────────────────────────
    daily_mins = (df.assign(date=df["ts"].dt.normalize())
                    .groupby("date")["min_played"].sum())

    # Biggest listening day
    best_day = daily_mins.idxmax()
    best_day_mins = daily_mins.max()

    # Longest streak of consecutive days with listening
    all_dates = pd.Series(sorted(daily_mins.index))
    gaps = (all_dates.diff().dt.days != 1)
    streak_id = gaps.cumsum()
    streak_len = streak_id.value_counts().max()
    streak_start = all_dates[streak_id == streak_id.value_counts().idxmax()].iloc[0]
    streak_end   = all_dates[streak_id == streak_id.value_counts().idxmax()].iloc[-1]

    # First & last song
    first_row = df.loc[df["ts"].idxmin()]
    last_row  = df.loc[df["ts"].idxmax()]

    # Most played song in a single day
    best_track_day = (df.assign(date=df["ts"].dt.normalize())
                        .groupby(["date", "master_metadata_track_name"])["min_played"]
                        .sum().reset_index()
                        .sort_values("min_played", ascending=False)
                        .iloc[0])

    # Longest single listen (one row)
    longest_row = df.loc[df["min_played"].idxmax()]

    # Most active month (year + month)
    best_month_row = (df.groupby(["year", "month"])["min_played"].sum()
                        .reset_index().sort_values("min_played", ascending=False).iloc[0])
    month_names_full = {1:"January",2:"February",3:"March",4:"April",5:"May",6:"June",
                        7:"July",8:"August",9:"September",10:"October",11:"November",12:"December"}

    # Earliest & latest ever
    earliest = df.loc[df["hour"].eq(df["hour"].min()) & df["min_played"].gt(1), "ts"].min()
    latest   = df.loc[df["hour"].eq(df["hour"].max()) & df["min_played"].gt(1), "ts"].max()

    # ── Layout: 3 columns of cards ─────────────────────────────────────────────
    st.markdown("### Your personal Spotify records 🏅")
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3, gap="large")

    with col1:
        milestone_card("📆", "Biggest listening day ever",
                       best_day.strftime("%d %B %Y"),
                       f"{best_day_mins:,.0f} minutes")

        milestone_card("🔥", "Longest listening streak",
                       f"{streak_len} days in a row",
                       f"{streak_start.strftime('%d %b')} – {streak_end.strftime('%d %b %Y')}")

        milestone_card("🌅", "Most active month ever",
                       f"{month_names_full[int(best_month_row['month'])]} {int(best_month_row['year'])}",
                       f"{best_month_row['min_played']:,.0f} minutes")

    with col2:
        milestone_card("🎵", "Very first song ever played",
                       first_row["master_metadata_track_name"],
                       f"{first_row['master_metadata_album_artist_name']} · "
                       f"{first_row['ts'].strftime('%d %b %Y')}")

        milestone_card("🎶", "Most recent song played",
                       last_row["master_metadata_track_name"],
                       f"{last_row['master_metadata_album_artist_name']} · "
                       f"{last_row['ts'].strftime('%d %b %Y')}")

        milestone_card("⏱️", "Longest single listen",
                       longest_row["master_metadata_track_name"],
                       f"{longest_row['min_played']:,.1f} minutes · "
                       f"{longest_row['master_metadata_album_artist_name']}")

    with col3:
        milestone_card("🔁", "Most played track in one day",
                       best_track_day["master_metadata_track_name"],
                       f"{best_track_day['min_played']:,.0f} min on "
                       f"{pd.Timestamp(best_track_day['date']).strftime('%d %b %Y')}")

        milestone_card("🌙", "Latest night session",
                       latest.strftime("%H:%M on %d %b %Y"), "")

        milestone_card("🎸", "Total unique tracks heard",
                       f"{df['master_metadata_track_name'].nunique():,}",
                       f"across {df['master_metadata_album_album_name'].nunique():,} albums")

    # ── Fun summary bar ────────────────────────────────────────────────────────
    st.divider()
    total_hrs = df["min_played"].sum() / 60
    total_days = total_hrs / 24
    st.markdown(f"""
    <div style='background:linear-gradient(135deg,#1A1A1A,#0d2b18);border:1px solid #1DB954;
                border-radius:12px;padding:28px 32px;text-align:center;margin-top:8px'>
      <div style='color:#1DB954;font-size:0.85rem;font-weight:700;letter-spacing:0.1em;
                  margin-bottom:8px'>IN TOTAL</div>
      <div style='color:#FFFFFF;font-size:2rem;font-weight:700'>{total_hrs:,.0f} hours of music</div>
      <div style='color:#B3B3B3;margin-top:6px'>That's {total_days:.1f} full days — non-stop.</div>
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 — This Day in History
# ══════════════════════════════════════════════════════════════════════════════
with tab_history:
    st.markdown("### Pick a date and see what you were listening to 📆")

    min_date = df_all["ts"].dt.date.min()
    max_date = df_all["ts"].dt.date.max()

    chosen = st.date_input(
        "Choose a date",
        value=max_date,
        min_value=min_date,
        max_value=max_date,
        format="DD/MM/YYYY",
    )

    day_df = df_all[df_all["ts"].dt.date == chosen].copy()

    if day_df.empty:
        st.markdown("""
        <div style='background:#1A1A1A;border:1px solid #282828;border-radius:12px;
                    padding:40px;text-align:center;color:#B3B3B3'>
          😶 No listening recorded on this day.
        </div>""", unsafe_allow_html=True)
    else:
        # Summary metrics
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Songs played", f"{len(day_df):,}")
        c2.metric("Listening time", f"{day_df['min_played'].sum():,.0f} min")
        top_artist_day = day_df.groupby("master_metadata_album_artist_name")["min_played"].sum().idxmax()
        c3.metric("Top artist", top_artist_day)
        c4.metric("Songs finished", f"{(~day_df['skipped']).sum():,}")

        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2 = st.columns(2, gap="large")

        with col1:
            # Hour-by-hour listening
            hourly_day = day_df.groupby("hour")["min_played"].sum().reindex(range(24), fill_value=0).reset_index()
            hourly_day.columns = ["Hour", "Minutes"]
            fig = go.Figure(go.Bar(
                x=hourly_day["Hour"], y=hourly_day["Minutes"],
                marker_color=GREEN, marker_line_width=0,
                hovertemplate="<b>%{x}:00</b><br>%{y:.1f} min<extra></extra>",
            ))
            fig.update_xaxes(tickvals=list(range(0, 24, 3)),
                             ticktext=[f"{h:02d}:00" for h in range(0, 24, 3)])
            style(fig, title="When during the day?", xaxis_title="", yaxis_title="Minutes")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Top tracks of the day
            top_tracks_day = (day_df.groupby("master_metadata_track_name")["min_played"]
                              .sum().sort_values(ascending=False).head(10).reset_index())
            top_tracks_day.columns = ["Track", "Minutes"]
            fig = px.bar(top_tracks_day, x="Minutes", y="Track", orientation="h",
                         color_discrete_sequence=[GREEN],
                         labels={"Track": "", "Minutes": "Minutes"})
            fig.update_traces(marker_line_width=0,
                              hovertemplate="<b>%{y}</b><br>%{x:.1f} min<extra></extra>")
            fig.update_layout(yaxis={"categoryorder": "total ascending"})
            style(fig, title="Most played tracks this day")
            st.plotly_chart(fig, use_container_width=True)

        # Full track-by-track timeline
        st.markdown("#### Full playlist for this day")
        timeline = (day_df[["ts", "master_metadata_track_name",
                             "master_metadata_album_artist_name", "min_played", "skipped"]]
                    .sort_values("ts")
                    .copy())
        timeline["Time"] = timeline["ts"].dt.strftime("%H:%M")
        timeline["Duration"] = timeline["min_played"].apply(
            lambda m: f"{int(m)}:{int((m % 1) * 60):02d}"
        )
        timeline["Skipped"] = timeline["skipped"].map({True: "⏭", False: "✓"})
        timeline = timeline.rename(columns={
            "master_metadata_track_name": "Track",
            "master_metadata_album_artist_name": "Artist",
        })[["Time", "Track", "Artist", "Duration", "Skipped"]]

        st.dataframe(
            timeline.reset_index(drop=True),
            hide_index=True,
            use_container_width=True,
            height=min(400, 36 * len(timeline) + 38),
            column_config={
                "Time":     st.column_config.TextColumn("Time", width="small"),
                "Track":    st.column_config.TextColumn("Track"),
                "Artist":   st.column_config.TextColumn("Artist"),
                "Duration": st.column_config.TextColumn("Duration", width="small"),
                "Skipped":  st.column_config.TextColumn("", width="small"),
            },
        )
