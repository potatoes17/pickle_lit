import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
from audible_scraper import update_audible_info

# --- Google Sheet Setup ---
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

def load_data(ws):
    rows = ws.get_all_values()
    return pd.DataFrame(rows[1:], columns=rows[0]) if rows else pd.DataFrame()

def update_row(title, author, updated_fields, worksheet):
    all_records = worksheet.get_all_values()
    headers = all_records[0]
    data = all_records[1:]
    index_map = {(row[0], row[1]): idx+2 for idx, row in enumerate(data)}
    key = (title, author)

    if key in index_map:
        i = index_map[key]
        for col_name, value in updated_fields.items():
            if col_name in headers:
                col_letter = chr(65 + headers.index(col_name))
                worksheet.update(f"{col_letter}{i}", value)

# --- UI ---
st.set_page_config(page_title="📖 Book Detail View", layout="wide")
st.title("📖 Book Detail View")

title_param = st.query_params.get("title")
author_param = st.query_params.get("author")

if not title_param or not author_param:
    st.warning("No book specified.")
else:
    worksheet = get_worksheet()
    df = load_data(worksheet)
    book = df[(df["title"] == title_param) & (df["author"] == author_param)]

    if book.empty:
        st.error("Book not found.")
    else:
        row = book.iloc[0]
        st.header(row["title"])
        st.subheader(f"by {row['author']}")
        st.markdown(f"**Published:** {row['year_published']} by {row['publisher']}")
        st.markdown(f"**Series:** {row['series']} (#{row['num_in_series']})")
        st.markdown(f"**Spice Level:** {row['spice_level']}")
        st.markdown(f"**Rating:** {row['rating']}")
        st.markdown(f"**Tags:** {row['tags']}")
        st.markdown(f"**Description:** {row['description']}")
        st.markdown(f"**Narrator(s):** {row['audiobook_voices']}")
        st.markdown(f"**Audio Runtime:** {row['audiobook_time']}")
        if row["audiobook"].lower() == "yes":
            st.markdown(f"[🎧 Audible Link]({row.get('audible_link', '')})", unsafe_allow_html=True)

        if st.button("🔄 Check for Updates"):
            st.info("Scraping updates for this book...")
            updates = update_audible_info(pd.DataFrame([row]), max_days=0)
            if updates:
                updated = updates[0]
                updated_fields = {
                    "audiobook": updated["audiobook"],
                    "audiobook_voices": updated["audiobook_voices"],
                    "audiobook_time": updated["audiobook_time"],
                    "audio_last_updated": updated["audio_last_updated"],
                    "last_updated": datetime.now().strftime('%Y-%m-%d')
                }
                update_row(row["title"], row["author"], updated_fields, worksheet)
                st.success("✅ Book updated!")
            else:
                st.info("No new data found.")
