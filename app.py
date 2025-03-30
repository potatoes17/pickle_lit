
import streamlit as st
import pandas as pd
import gspread
from datetime import datetime
from google.oauth2.service_account import Credentials
from scrape_book_metadata import scrape_book_metadata

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
    try:
        ws.append_row(row)
        st.success("✅ New book successfully added to the sheet.")
    except Exception as e:
        st.error(f"❌ Failed to append row to sheet: {e}")

# Streamlit UI
st.set_page_config(page_title="Pickle Lit", layout="centered")
st.title("📚 Pickle Lit: Romance Book Explorer")

worksheet = get_worksheet()
df = load_sheet(worksheet)

st.markdown("Search for a new book to add it to your database.")

title_input = st.text_input("Enter book title")
search_button = st.button("🔍 Search & Add New Book")

if search_button and title_input:
    if ((df["title"] == title_input).any()):
        st.info("This book is already in your sheet.")
    else:
        with st.spinner("Scraping book info..."):
            book_data = scrape_book_metadata(title_input)
            if book_data:
                st.write("Scraped data preview:")
                st.dataframe(pd.DataFrame([book_data]))
                append_row(worksheet, book_data)
            else:
                st.error("❌ Could not find this book using Google Books API.")
