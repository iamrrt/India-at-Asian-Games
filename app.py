import sqlite3
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="India Asian Games StatsHub", page_icon="🏅", layout="wide"
)


@st.cache_resource
def get_connection():
    return sqlite3.connect("asian_games.db", check_same_thread=False)


conn = get_connection()

# App Header
st.title("🏅 India at the Asian Games (1951–2022)")
st.caption(
    "Cricinfo-style search engine & historical database for Indian medalists"
)

# Cricinfo-style Top Stat Cards
total_medals = pd.read_sql("SELECT COUNT(*) FROM medals", conn).iloc[0, 0]
golds = pd.read_sql(
    "SELECT COUNT(*) FROM medals WHERE medal = 'Gold'", conn
).iloc[0, 0]
silvers = pd.read_sql(
    "SELECT COUNT(*) FROM medals WHERE medal = 'Silver'", conn
).iloc[0, 0]
bronzes = pd.read_sql(
    "SELECT COUNT(*) FROM medals WHERE medal = 'Bronze'", conn
).iloc[0, 0]

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Total Medals", total_medals)
kpi2.metric("🥇 Gold", golds)
kpi3.metric("🥈 Silver", silvers)
kpi4.metric("🥉 Bronze", bronzes)

st.divider()

# Sidebar Filters & Search
st.sidebar.header("🔍 Search Filters")
free_text = st.sidebar.text_input(
    "Search Athlete, Sport, or Event",
    placeholder="e.g. Milkha Singh, Shooting, 400m",
)

sports_list = ["All"] + pd.read_sql(
    "SELECT DISTINCT sport FROM medals ORDER BY sport", conn
)["sport"].tolist()
selected_sport = st.sidebar.selectbox("Sport", sports_list)

editions_list = ["All"] + sorted(
    pd.read_sql("SELECT DISTINCT edition FROM medals", conn)[
        "edition"
    ].tolist(),
    reverse=True,
)
selected_edition = st.sidebar.selectbox("Edition (Year)", editions_list)

selected_medal = st.sidebar.radio(
    "Medal Type", ["All", "Gold", "Silver", "Bronze"], horizontal=True
)

# Dynamic SQL Query Generation
query = "SELECT edition AS Edition, medal AS Medal, sport AS Sport, event AS Event, athlete_name AS Athlete FROM medals WHERE 1=1"
params = []

if free_text.strip():
    query += " AND (athlete_name LIKE ? OR event LIKE ? OR sport LIKE ?)"
    pattern = f"%{free_text.strip()}%"
    params.extend([pattern, pattern, pattern])

if selected_sport != "All":
    query += " AND sport = ?"
    params.append(selected_sport)

if selected_edition != "All":
    query += " AND edition = ?"
    params.append(selected_edition)

if selected_medal != "All":
    query += " AND medal = ?"
    params.append(selected_medal)

query += " ORDER BY edition DESC, medal ASC"
results = pd.read_sql(query, conn, params=params)

# Cricinfo-style Athlete Profile Card
if free_text.strip():
    athlete_match = pd.read_sql(
        "SELECT * FROM medals WHERE athlete_name LIKE ? LIMIT 1",
        conn,
        params=[f"%{free_text.strip()}%"],
    )
    if not athlete_match.empty:
        matched_name = athlete_match.iloc[0]["athlete_name"]
        athlete_records = pd.read_sql(
            "SELECT * FROM medals WHERE athlete_name = ?",
            conn,
            params=[matched_name],
        )

        with st.expander(
            f"👤 Career Summary: {matched_name}", expanded=True
        ):
            c1, c2, c3 = st.columns(3)
            c1.write(f"**Primary Sport:** {athlete_records['sport'].iloc[0]}")
            c2.write(
                f"**Editions:** {', '.join(map(str, sorted(athlete_records['edition'].unique())))}"
            )
            c3.write(
                f"**Medals:** 🥇 {len(athlete_records[athlete_records['medal']=='Gold'])} | "
                f"🥈 {len(athlete_records[athlete_records['medal']=='Silver'])} | "
                f"🥉 {len(athlete_records[athlete_records['medal']=='Bronze'])}"
            )

# Results Table
st.subheader(f"Results ({len(results)} records found)")
st.dataframe(
    results,
    use_container_width=True,
    hide_index=True,
    column_config={"Edition": st.column_config.NumberColumn(format="%d")},
)