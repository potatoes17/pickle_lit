import streamlit as st
import psycopg2

st.set_page_config(page_title="DB Test", layout="wide")

try:
    conn = psycopg2.connect(st.secrets["postgres"]["url"])
    st.success("✅ Connected to Supabase PostgreSQL successfully.")
    conn.close()
except Exception as e:
    st.error(f"❌ Connection failed: {e}")
