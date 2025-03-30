
import streamlit as st
import pandas as pd
from search_logic import apply_filters
from scrape_manager import scrape_and_update
from save_to_postgres import get_postgres_conn
from psycopg2.extras import RealDictCursor

st.set_page_config(page_title="🔍 Advanced Search", layout="wide")
st.title("🔍 Advanced Search")

@st.cache_data
def load_all_books():
    conn = get_postgres_conn()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM books ORDER BY last_updated DESC LIMIT 1000")
        rows = cur.fetchall()
    conn.close()
    return pd.DataFrame(rows)

df = load_all_books()

if df.empty:
    st.warning("No books found in the database.")
else:
    # Sidebar filter UI
    with st.sidebar:
        title = st.text_input("Search by Title")
        author = st.text_input("Search by Author")
        year_range = st.slider("Year Published", 2005, 2025, (2005, 2025))
        spice_range = st.slider("Spice Level", 0.0, 5.0, (0.0, 5.0), step=0.5)
        run_scrape = st.checkbox("Run scrape on search")

    filtered = apply_filters(df, title, author, year_range, spice_range)
    st.subheader(f"Results: {len(filtered)} book(s) found")
    st.dataframe(filtered)

    if run_scrape and title:
        with st.spinner("Scraping..."):
            updated, meta = scrape_and_update(title)
            if meta["status"] == "new_scraped":
                st.success("✅ Book scraped and added!")
            elif meta["status"] == "fresh":
                st.info("🟢 Book is already up-to-date.")
            elif meta["status"] == "not_found":
                st.error("❌ Could not find this book.")
            st.session_state["trigger_rerun"] = True
            st.stop()

if st.session_state.get("trigger_rerun"):
    st.session_state["trigger_rerun"] = False
    st.experimental_rerun()
