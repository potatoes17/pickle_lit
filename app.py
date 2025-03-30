
import streamlit as st
from scrape_manager import scrape_and_update
from save_to_postgres import get_postgres_conn
from psycopg2.extras import RealDictCursor
import pandas as pd

st.set_page_config(page_title="📚 Pickle Lit: Romance Book Explorer", layout="wide")
st.title("📚 Pickle Lit: Romance Book Explorer")

def load_books(limit=50):
    conn = get_postgres_conn()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM books ORDER BY last_updated DESC LIMIT %s", (limit,))
        rows = cur.fetchall()
    return pd.DataFrame(rows)

title = st.text_input("Search for a book title")

if st.button("Search and Scrape"):
    if title:
        with st.spinner("Scraping and updating..."):
            updated, meta = scrape_and_update(title)
            if meta["status"] == "new_scraped":
                st.success("✅ Book scraped and added!")
            elif meta["status"] == "fresh":
                st.info("🟢 Book is already up-to-date.")
            elif meta["status"] == "not_found":
                st.error("❌ Could not find this book.")
            st.session_state["trigger_rerun"] = True
            st.stop()

df = load_books()
st.write("Recent Books:")
st.dataframe(df)

# ✅ Safe rerun logic
if st.session_state.get("trigger_rerun", False):
    st.session_state["trigger_rerun"] = False
    st.experimental_rerun()
