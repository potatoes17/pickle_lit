
import time
import streamlit as st
from scrape_book_metadata import scrape_book_metadata
from audible_scraper_with_timestamp import update_audible_info
from save_to_postgres import get_postgres_conn, upsert_books

def scrape_and_update(title, filters=None, max_age_days=30, skip_audible_if_many=True):
    """
    Shared scrape handler for homepage, advanced search, and browse page.

    Args:
        title (str): Book title to scrape.
        filters (dict): Optional filters to apply for deeper targeting.
        max_age_days (int): Age limit to consider a book stale.
        skip_audible_if_many (bool): Skip Audible scraping if too many results found.

    Returns:
        updated_df (pd.DataFrame): DataFrame of updates (if any)
        meta (dict): Metadata status for diagnostics
    """
    conn = get_postgres_conn()
    cur = conn.cursor()

    # Check if book exists
    cur.execute("SELECT * FROM books WHERE title ILIKE %s", (f"%{title}%",))
    matches = cur.fetchall()

    if matches:
        # If stale (based on max_age_days), update it
        last_updated = matches[0][-2]
        if last_updated:
            age_sec = (pd.Timestamp.now() - pd.to_datetime(last_updated)).total_seconds()
            age_days = age_sec / 86400
            if age_days < max_age_days:
                return None, {"status": "fresh", "skipped": True}
    else:
        # New entry — scrape and insert
        data = scrape_book_metadata(title)
        if data:
            upsert_books([data])
            if not skip_audible_if_many:
                update_audible_info([data])
            return data, {"status": "new_scraped"}
        else:
            return None, {"status": "not_found"}

    conn.close()
    return None, {"status": "no_action"}
