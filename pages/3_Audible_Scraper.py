
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

def update_sheet(df, worksheet):
    all_records = worksheet.get_all_values()
    headers = all_records[0]
    data = all_records[1:]
    index_map = {(row[0], row[1]): idx+2 for idx, row in enumerate(data)}

    updated_rows = 0
    for _, row in df.iterrows():
        key = (row["title"], row["author"])
        if key in index_map:
            i = index_map[key]
            try:
                worksheet.update(f"O{i}", [str(row.get("audiobook", ""))])
                worksheet.update(f"P{i}", [str(row.get("audiobook_voices", ""))])
                worksheet.update(f"Q{i}", [str(row.get("audiobook_time", ""))])
                worksheet.update(f"U{i}", [str(row.get("audio_last_updated", ""))])
                worksheet.update(f"N{i}", [datetime.now().strftime('%Y-%m-%d')])
                updated_rows += 1
            except Exception as e:
                st.error(f"❌ Error updating row {i}: {e}")
    st.write(f"✅ {updated_rows} row(s) updated in the Google Sheet.")

# --- UI ---
st.set_page_config(page_title="🎧 Manual Audible Scraper", layout="wide")
st.title("🎧 Manual Audible Scraper")

worksheet = get_worksheet()
df = load_data(worksheet)

if df.empty:
    st.warning("No data found in sheet.")
else:
    st.markdown("Use this tool to check all books for audiobook info updates.")
    max_days = st.slider("Only check books not updated in the last (days):", 1, 90, 30)

    if st.button("🔄 Run Audible Update"):
        st.info("Checking books for audiobook updates...")
        updates = update_audible_info(df, max_days=max_days)

        if updates:
            updated_df = pd.DataFrame(updates)
            update_sheet(updated_df, worksheet)
            st.success(f"✅ Updated {len(updated_df)} books.")
            st.dataframe(updated_df)
        else:
            st.info("No books needed updating.")
