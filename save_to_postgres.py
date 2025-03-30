
import psycopg2
import streamlit as st
import pandas as pd

@st.cache_resource
def get_postgres_conn():
    return psycopg2.connect(st.secrets["postgres"]["url"])

def upsert_books(book_list):
    conn = get_postgres_conn()
    cur = conn.cursor()
    for book in book_list:
        keys = book.keys()
        values = [book[k] for k in keys]
        updates = [f"{k} = EXCLUDED.{k}" for k in keys if k not in ["isbn", "title", "author"]]
        sql = f"""
            INSERT INTO books ({','.join(keys)})
            VALUES ({','.join(['%s']*len(values))})
            ON CONFLICT (isbn) DO UPDATE SET {', '.join(updates)};
        """
        cur.execute(sql, values)
    conn.commit()
    cur.close()
    conn.close()
