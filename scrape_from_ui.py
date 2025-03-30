
import streamlit as st
from scrape_book_metadata import scrape_book_metadata

def run_scrape_from_ui(title_input):
    if not title_input:
        st.warning("Please enter a book title.")
        return

    with st.spinner("🔍 Scraping book info..."):
        book = scrape_book_metadata(title_input)
        if book:
            st.success(f"✅ Book '{book['title']}' by {book['author']} added to the database.")
        else:
            st.error("❌ Book not found or failed to scrape.")
