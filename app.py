
import streamlit as st
import pandas as pd
import gspread
from datetime import datetime
from google.oauth2.service_account import Credentials
import time

# Placeholder book metadata scraper
def scrape_book_metadata(title_query):
    # Simulate scraping logic here
    time.sleep(1.5)  # Simulate delay
    return {
        "title": title_query,
        "author": "Unknown",
        "isbn": "",
        "series": "",
        "num_in_series": "",
        "year_published": "2024",
        "publisher": "",
        "page_count": "",
        "spice_level": "",
        "rating": "",
        "subgenre": "",
        "tags": "",
        "description": "",
        "kindle_unlimited": "",
        "last_updated": datetime.now().strftime('%Y-%m-%d'),
        "audiobook": "",
        "audiobook_voices": "",
        "audiobook_time": "",
        "graphic_audio": "",
        "graphic_audio_voices": "",
        "graph_audio_time": "",
        "audio_last_updated": ""
    }

# Google Sheets setup
SCOPE = ["https://www.googleapis.com/auth/spreadsheets"]
SHEET_URL = "https://docs.google.com/spreadsheets/d/1eKNsNHFMw-Yh9sDYGAgWXAs4zO-otw06nl6OjqO-T20/edit"
WORKSHEET_NAME = "Sheet1"

@st.cache_resource
def get_worksheet():
    credentials = Credentials.from_service_account_info(
        st.secrets["GOOGLE_SERVICE_ACCOUNT_JSON"],
        scopes=SCOPE
    )
    gc = gspread.authorize(credentials)
    return gc.open_by_url(SHEET_URL).worksheet(WORKSHEET_NAME)

def load_sheet(ws):
    rows = ws.get_all_values()
    return pd.DataFrame(rows[1:], columns=rows[0]) if rows else pd.DataFrame()

def append_row(ws, book_dict):
    row = [book_dict.get(col, "") for col in ws.row_values(1)]
    ws.append_row(row)

# Streamlit UI
st.set_page_config(page_title="Pickle Lit", layout="centered")
st.title("📚 Pickle Lit: Romance Book Explorer")

worksheet = get_worksheet()
df = load_sheet(worksheet)

st.markdown("Search for a new book to add it to your database.")

title_input = st.text_input("Enter book title")
search_button = st.button("🔍 Search & Add New Books")

if search_button and title_input:
    if ((df["title"] == title_input).any()):
        st.info("This book is already in your sheet.")
    else:
        with st.spinner("Scraping book info..."):
            book_data = scrape_book_metadata(title_input)
            append_row(worksheet, book_data)
            st.success(f"✅ '{title_input}' added to your sheet!")
