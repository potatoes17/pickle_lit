
import psycopg2
from psycopg2.extras import execute_batch
import streamlit as st

@st.cache_resource
def get_postgres_conn():
    return psycopg2.connect(st.secrets["postgres"]["url"])

def save_books_to_db(book_list):
    if not book_list:
        st.warning("No books to save.")
        return

    conn = get_postgres_conn()
    cursor = conn.cursor()

    query = """
    INSERT INTO books (
        title, author, isbn, isbn_13, series, num_in_series, year_published, page_count,
        spice_level, rating, subgenre, tags, description, kindle_unlimited, last_updated,
        audiobook, audiobook_voices, audiobook_time, graphic_audio, graphic_audio_voices,
        graph_audio_time, audio_last_updated
    )
    VALUES (
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
    )
    ON CONFLICT (title, author) DO UPDATE SET
        isbn = EXCLUDED.isbn,
        isbn_13 = EXCLUDED.isbn_13,
        series = EXCLUDED.series,
        num_in_series = EXCLUDED.num_in_series,
        year_published = EXCLUDED.year_published,
        page_count = EXCLUDED.page_count,
        spice_level = EXCLUDED.spice_level,
        rating = EXCLUDED.rating,
        subgenre = EXCLUDED.subgenre,
        tags = EXCLUDED.tags,
        description = EXCLUDED.description,
        kindle_unlimited = EXCLUDED.kindle_unlimited,
        last_updated = EXCLUDED.last_updated,
        audiobook = EXCLUDED.audiobook,
        audiobook_voices = EXCLUDED.audiobook_voices,
        audiobook_time = EXCLUDED.audiobook_time,
        graphic_audio = EXCLUDED.graphic_audio,
        graphic_audio_voices = EXCLUDED.graphic_audio_voices,
        graph_audio_time = EXCLUDED.graph_audio_time,
        audio_last_updated = EXCLUDED.audio_last_updated;
    """

    columns = [
        "title", "author", "isbn", "isbn_13", "series", "num_in_series", "year_published",
        "page_count", "spice_level", "rating", "subgenre", "tags", "description",
        "kindle_unlimited", "last_updated", "audiobook", "audiobook_voices", "audiobook_time",
        "graphic_audio", "graphic_audio_voices", "graph_audio_time", "audio_last_updated"
    ]

    values = [
        tuple(book.get(col, None) for col in columns)
        for book in book_list
    ]

    try:
        execute_batch(cursor, query, values)
        conn.commit()
        st.success(f"✅ {len(book_list)} book(s) saved to the database.")
    except Exception as e:
        st.error(f"❌ Database error: {e}")
    finally:
        cursor.close()
        conn.close()
