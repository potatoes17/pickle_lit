
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import RealDictCursor
from audible_scraper import update_audible_info
from save_to_postgres import get_postgres_conn, save_books_to_db

st.set_page_config(page_title="🎧 Audible Scraper", layout="wide")
st.title("🎧 Manual Audible Scraper")

@st.cache_data
def load_books_needing_audio_update(max_days=30):
    conn = get_postgres_conn()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT * FROM books
            WHERE audio_last_updated IS NULL
               OR audio_last_updated < %s
            ORDER BY audio_last_updated NULLS FIRST
            LIMIT 100
        """, (datetime.now().date() - timedelta(days=max_days),))
        rows = cur.fetchall()
    conn.close()
    return pd.DataFrame(rows)

max_days = st.slider("Only check books not updated in the last (days):", 1, 90, 30)

if st.button("🔄 Run Audible Update"):
    df = load_books_needing_audio_update(max_days)
    if df.empty:
        st.info("No books need updates based on that date filter.")
    else:
        st.info(f"Checking {len(df)} books for audiobook info...")
        updates = update_audible_info(df, max_days=max_days)
        if updates:
            save_books_to_db(updates)
            st.success(f"✅ Updated {len(updates)} books with audio info.")
            st.dataframe(pd.DataFrame(updates))
        else:
            st.info("No updates needed.")
