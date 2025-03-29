import streamlit as st
import pandas as pd
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
    return gc.open_by_url(SHEET_URL).worksheet(WORKSHEET_NAME)

def load_data(ws):
    rows = ws.get_all_values()
    return pd.DataFrame(rows[1:], columns=rows[0]) if rows else pd.DataFrame()

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
    spice_level = st.sidebar.slider("Spice Level (0–5)", 0.0, 5.0, (0.0, 5.0), 0.5)

    subgenres = df["subgenre"].dropna().unique().tolist()
    tags = df["tags"].dropna().unique().tolist()

    selected_subgenres = st.sidebar.multiselect("Subgenres", subgenres)
    selected_tags = st.sidebar.multiselect("Tags", tags)

    filtered_df = df[
        df["year_published"].astype(str).str.isnumeric() &
        df["spice_level"].astype(str).str.replace(",", ".").str.replace(" ", "").str.replace("–", "-").str.extract(r"(\d+\.?\d*)")[0].astype(float).between(*spice_level) &
        df["year_published"].astype(int).between(*year_range)
    ]

    if title_filter:
        filtered_df = filtered_df[filtered_df["title"].str.contains(title_filter, case=False)]

    if author_filter:
        filtered_df = filtered_df[filtered_df["author"].str.contains(author_filter, case=False)]

    if selected_subgenres:
        filtered_df = filtered_df[filtered_df["subgenre"].isin(selected_subgenres)]

    if selected_tags:
        filtered_df = filtered_df[filtered_df["tags"].str.contains('|'.join(selected_tags), case=False)]

    st.write(f"### Results: {len(filtered_df)} book(s) found")
    st.dataframe(filtered_df.reset_index(drop=True))
