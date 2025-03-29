
import streamlit as st
import pandas as pd
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
    sheet = gc.open_by_url(SHEET_URL)
    return sheet.worksheet(WORKSHEET_NAME)

def load_data(worksheet):
    rows = worksheet.get_all_values()
    if not rows or len(rows) < 2:
        return pd.DataFrame()
    return pd.DataFrame(rows[1:], columns=rows[0])

def update_sheet(df, worksheet):
    all_records = worksheet.get_all_values()
    headers = all_records[0]
    data = all_records[1:]
    index_map = {(row[0], row[1]): idx+2 for idx, row in enumerate(data)}

    for _, row in df.iterrows():
        key = (row["title"], row["author"])
        if key in index_map:
            i = index_map[key]
            worksheet.update(f"O{i}", row["audiobook"])
            worksheet.update(f"P{i}", row["audiobook_voices"])
            worksheet.update(f"Q{i}", row["audiobook_time"])
            worksheet.update(f"U{i}", row["audio_last_updated"])

st.set_page_config(page_title="Pickle Lit", layout="wide")
st.title("🎧 Manual Audible Scrape")

worksheet = get_worksheet()
df = load_data(worksheet)

if df.empty:
    st.warning("Google Sheet is empty or not available.")
else:
    max_days = st.slider("Skip books updated within the past N days", 1, 90, 30)

    if st.button("🔄 Run Audible Scrape"):
        st.info("Looking for outdated or missing audiobook entries...")
        updates = update_audible_info(df, max_days=max_days)

        if updates:
            updated_df = pd.DataFrame(updates)
            st.success(f"✅ Audible info updated for {len(updated_df)} books.")
            st.dataframe(updated_df)
            update_sheet(updated_df, worksheet)
        else:
            st.warning("All books have recent Audible info.")
