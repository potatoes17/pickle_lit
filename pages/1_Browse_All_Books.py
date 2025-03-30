
import streamlit as st
import pandas as pd
from datetime import datetime
from audible_scraper import update_audible_info
import gspread
from google.oauth2.service_account import Credentials

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
    return pd.DataFrame(rows[1:], columns=rows[0]) if rows else pd.DataFrame()

def update_sheet(df, worksheet):
    all_records = worksheet.get_all_values()
    headers = all_records[0]
    data = all_records[1:]
    index_map = {(row[0], row[1]): idx+2 for idx, row in enumerate(data)}

    for _, row in df.iterrows():
        key = (row["title"], row["author"])
        if key in index_map:
            i = index_map[key]
            try:
                worksheet.update(f"O{i}", str(row.get("audiobook", "")))
                worksheet.update(f"P{i}", str(row.get("audiobook_voices", "")))
                worksheet.update(f"Q{i}", str(row.get("audiobook_time", "")))
                worksheet.update(f"U{i}", str(row.get("audio_last_updated", "")))
                worksheet.update(f"N{i}", datetime.now().strftime('%Y-%m-%d'))
            except Exception as e:
                st.error(f"Error updating row {i}: {e}")

# --- Main Page ---
st.set_page_config(page_title="📚 Browse & Update Books", layout="wide")
st.title("📚 Browse & Update Books")

worksheet = get_worksheet()
df = load_data(worksheet)

if "browse_limit" not in st.session_state:
    st.session_state.browse_limit = 20

if df.empty:
    st.warning("No book data available.")
else:
    df["label"] = df["title"] + " by " + df["author"]
    shown_df = df.head(st.session_state.browse_limit)

    selected = st.multiselect("Select books to check for updates:", options=shown_df["label"].tolist())

    if selected:
        if len(selected) > 20:
            st.error("⚠️ Too many entries selected. Please limit to 20.")
        elif st.button("🔄 Check Selected for Updates"):
            selected_df = shown_df[shown_df["label"].isin(selected)]
            st.info(f"Running updates on {len(selected_df)} books...")
            updates = update_audible_info(selected_df, max_days=0)

            if updates:
                updated_df = pd.DataFrame(updates)
                update_sheet(updated_df, worksheet)
                st.success(f"✅ Updated {len(updated_df)} books.")
                st.dataframe(updated_df)
            else:
                st.info("All selected books are already up-to-date.")
    else:
        st.dataframe(shown_df)

    if st.button("⬇️ Load More Books"):
        st.session_state.browse_limit += 20
        st.experimental_rerun()
