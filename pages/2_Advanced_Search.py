
import streamlit as st
import pandas as pd
import gspread
import time
from datetime import datetime
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

    st.write(f"✅ {updated_rows} row(s) successfully updated in the Google Sheet.")

# --- Safe Rerun Trigger ---
if st.session_state.get("search_reload"):
    st.session_state.search_reload = False
    st.stop()

# --- UI ---
st.set_page_config(page_title="🔍 Advanced Search", layout="wide")
st.title("🔍 Advanced Search")

worksheet = get_worksheet()
df = load_data(worksheet)

if df.empty:
    st.warning("No book data available.")
else:
    st.sidebar.header("📑 Filters")

    title_filter = st.sidebar.text_input("Search by Title")
    author_filter = st.sidebar.text_input("Search by Author")
    year_range = st.sidebar.slider("Year Published", 2005, 2025, (2005, 2025))
    spice_range = st.sidebar.slider("Spice Level", 0.0, 5.0, (0.0, 5.0), 0.5)

    subgenres = df["subgenre"].dropna().unique().tolist()
    tags = df["tags"].dropna().unique().tolist()

    selected_subgenres = st.sidebar.multiselect("Subgenres", subgenres)
    selected_tags = st.sidebar.multiselect("Tags", tags)

    # --- Apply Filters ---
    filtered_df = df.copy()
    filtered_df = filtered_df[filtered_df["year_published"].astype(str).str.isnumeric()]
    filtered_df = filtered_df[filtered_df["year_published"].astype(int).between(*year_range)]
    filtered_df = filtered_df[filtered_df["spice_level"].astype(str).str.extract(r"(\d+\.?\d*)")[0].astype(float).between(*spice_range)]

    if title_filter:
        filtered_df = filtered_df[filtered_df["title"].str.contains(title_filter, case=False)]

    if author_filter:
        filtered_df = filtered_df[filtered_df["author"].str.contains(author_filter, case=False)]

    if selected_subgenres:
        filtered_df = filtered_df[filtered_df["subgenre"].isin(selected_subgenres)]

    if selected_tags:
        filtered_df = filtered_df[filtered_df["tags"].str.contains("|".join(selected_tags), case=False)]

    st.write(f"### Results: {len(filtered_df)} book(s) found")

    if "search_limit" not in st.session_state:
        st.session_state.search_limit = 20

    show_df = filtered_df.head(st.session_state.search_limit)
    st.dataframe(show_df.reset_index(drop=True))

    if st.button("⬇️ Load More Results"):
        st.session_state.search_limit += 20
        st.session_state.search_reload = True
        st.experimental_rerun()

    if st.button("🔄 Scrape Updates for Filtered Books"):
        if len(show_df) > 20:
            st.error("⚠️ Too many entries to scrape safely. Please narrow your search (limit: 20).")
        else:
            st.info("Scraping audiobook info for selected books...")
            time.sleep(1.5)
            updates = update_audible_info(show_df, max_days=0)
            time.sleep(1.5)

            if updates:
                updated_df = pd.DataFrame(updates)
                st.success(f"✅ {len(updated_df)} updated books scraped.")
                update_sheet(updated_df, worksheet)
            else:
                st.info("No updates were needed.")
