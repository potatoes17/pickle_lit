
import streamlit as st
import pandas as pd
from save_to_postgres import get_postgres_conn
from psycopg2.extras import RealDictCursor
from audible_scraper_with_timestamp import update_audible_info

st.set_page_config(page_title="🎧 Manual Audible Scrape", layout="wide")
st.title("🎧 Manual Audible Scrape")

@st.cache_data
def load_books_needing_audio_update(max_days):
    conn = get_postgres_conn()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"""
            SELECT * FROM books
            WHERE audio_last_updated IS NULL OR audio_last_updated < CURRENT_DATE - INTERVAL '%s days'
            ORDER BY audio_last_updated NULLS FIRST
            LIMIT 100
        """, (max_days,))
        rows = cur.fetchall()
    return pd.DataFrame(rows)

max_days = st.slider("Show books not updated in the last X days", 1, 180, 30)

df = load_books_needing_audio_update(max_days)

if df.empty:
    st.info("✅ All books have recent audiobook data.")
else:
    selected = st.multiselect("Select books to update audiobook info", df["title"])

    if st.button("🔄 Run Audible Scrape") and selected:
        with st.spinner("Scraping audiobook data..."):
            update_audible_info(df[df["title"].isin(selected)].to_dict(orient="records"))
            st.session_state["trigger_rerun"] = True
            st.stop()

    st.dataframe(df)

# ✅ Safe rerun logic
if st.session_state.get("trigger_rerun", False):
    st.session_state["trigger_rerun"] = False
    st.experimental_rerun()
