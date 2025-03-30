
import streamlit as st
import pandas as pd
from save_to_postgres import get_postgres_conn
from psycopg2.extras import RealDictCursor
from scrape_manager import scrape_and_update

st.set_page_config(page_title="📖 Browse All Books", layout="wide")
st.title("📖 Browse All Books")

@st.cache_data
def load_books(limit):
    conn = get_postgres_conn()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM books ORDER BY last_updated DESC LIMIT %s", (limit,))
        rows = cur.fetchall()
    return pd.DataFrame(rows)

if "browse_limit" not in st.session_state:
    st.session_state["browse_limit"] = 100

st.sidebar.slider("Max Books to Display", 10, 1000, st.session_state["browse_limit"], key="browse_limit")
df = load_books(st.session_state["browse_limit"])

if df.empty:
    st.warning("No book data found in the database.")
else:
    selected = st.multiselect("Select books to check for updates", df["title"])

    if st.button("Check for Updates") and selected:
        if len(selected) > 25:
            st.warning("⚠️ Too many entries selected. Please limit to 25 to avoid timeout or bans.")
        else:
            with st.spinner("Checking for updates..."):
                for title in selected:
                    scrape_and_update(title)
                st.session_state["trigger_rerun"] = True
                st.stop()

    st.dataframe(df)

# ✅ Safe rerun logic
if st.session_state.get("trigger_rerun", False):
    st.session_state["trigger_rerun"] = False
    st.experimental_rerun()
