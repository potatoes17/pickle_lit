
import streamlit as st
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
from scrape_from_ui import run_scrape_from_ui
from save_to_postgres import get_postgres_conn

st.set_page_config(page_title="📚 Browse & Update Books", layout="wide")
st.title("📚 Browse All Books")

@st.cache_data
def load_books_from_db(limit=100):
    conn = get_postgres_conn()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"SELECT * FROM books ORDER BY last_updated DESC LIMIT %s", (limit,))
        rows = cur.fetchall()
    conn.close()
    return pd.DataFrame(rows)

# Load books
if "browse_limit" not in st.session_state:
    st.session_state.browse_limit = 20

df = load_books_from_db(st.session_state.browse_limit)

if df.empty:
    st.warning("No book data found in the database.")
else:
    df["label"] = df["title"] + " by " + df["author"]
    selected = st.multiselect("Select books:", df["label"].tolist())

    st.dataframe(df)

    if st.button("⬇️ Load More"):
        st.session_state.browse_limit += 20
        st.rerun()

# Manual scrape UI
st.divider()
st.subheader("📘 Scrape New Book")
title_input = st.text_input("Enter book title to scrape")
if st.button("🔍 Scrape Book"):
    run_scrape_from_ui(title_input)
