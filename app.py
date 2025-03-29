
import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import requests
import time
from collections import Counter

# --- Google Sheets Setup ---
SCOPE = ["https://www.googleapis.com/auth/spreadsheets"]
SHEET_NAME = "pickle_lit_books"
WORKSHEET_NAME = "Sheet1"

@st.cache_resource
def get_gsheet():
    credentials = Credentials.from_service_account_info(
        st.secrets["GOOGLE_SERVICE_ACCOUNT_JSON"],
        scopes=SCOPE
    )
    gc = gspread.authorize(credentials)
    sh = gc.open(SHEET_NAME)
    worksheet = sh.worksheet(WORKSHEET_NAME)
    return worksheet

# --- Scraper ---
def get_edition_data(work_key):
    editions_url = f"https://openlibrary.org{work_key}/editions.json?limit=10"
    isbns = set()
    page_counts = []
    publishers = []
    try:
        r = requests.get(editions_url)
        if r.status_code != 200:
            return isbns, None, None
        editions = r.json().get("entries", [])
        for edition in editions:
            isbns.update(edition.get("isbn_10", []))
            isbns.update(edition.get("isbn_13", []))
            if 'number_of_pages' in edition:
                page_counts.append(edition['number_of_pages'])
            if 'publishers' in edition:
                publishers.extend(edition['publishers'])
    except:
        pass
    most_common_pages = Counter(page_counts).most_common(1)
    most_common_publisher = list(set(publishers))
    return (
        isbns,
        most_common_pages[0][0] if most_common_pages else None,
        ", ".join(most_common_publisher)
    )

def scrape_books():
    books = []
    for page in range(1, 3):
        url = f"https://openlibrary.org/subjects/romance.json?limit=50&offset={(page - 1) * 50}"
        response = requests.get(url)
        if response.status_code != 200:
            break
        data = response.json()
        works = data.get("works", [])

        for work in works:
            year = work.get("first_publish_year")
            if not year or not (2005 <= year <= 2025):
                continue
            title = work.get("title")
            author = work["authors"][0]["name"] if work.get("authors") else None
            tags = ", ".join(work.get("subject", [])) if work.get("subject") else ""
            work_key = work.get("key")
            isbns, page_count, publisher = get_edition_data(work_key)
            books.append([
                title, author, year, "Romance", tags, page_count,
                publisher, ", ".join(isbns), ""
            ])
            time.sleep(0.5)
        time.sleep(1)
    return books

# --- UI ---
st.title("📚 Pickle Lit: Romance Book Explorer")

if st.button("🔄 Scrape and Append New Books"):
    st.info("Scraping books from Open Library...")
    book_data = scrape_books()
    worksheet = get_gsheet()
    existing = worksheet.get_all_values()
    headers = [
        "Title", "Author", "Year Published", "Subgenre", "Tags",
        "Page Count", "Publisher", "ISBNs", "Spice Level"
    ]

    if existing:
        existing_df = pd.DataFrame(existing[1:], columns=existing[0])
        existing_titles = set(zip(existing_df["Title"], existing_df["Author"]))
    else:
        worksheet.append_row(headers)
        existing_titles = set()

    new_books = [row for row in book_data if (row[0], row[1]) not in existing_titles]

    if new_books:
        worksheet.append_rows(new_books)
        st.success(f"✅ {len(new_books)} new books appended to Google Sheets!")
    else:
        st.warning("No new books found to append.")

# Load from sheet
worksheet = get_gsheet()
rows = worksheet.get_all_values()
if rows:
    df = pd.DataFrame(rows[1:], columns=rows[0])

    # --- Filters ---
    with st.sidebar:
        st.header("🔍 Filters")
        title_filter = st.text_input("Search by Title")
        author_filter = st.text_input("Search by Author")
        year_range = st.slider("Year Published", 2005, 2025, (2005, 2025))
        subgenres = df["Subgenre"].dropna().unique().tolist()
        subgenre_filter = st.multiselect("Subgenre", subgenres)
        spice_levels = df["Spice Level"].dropna().unique().tolist()
        spice_filter = st.multiselect("Spice Level", spice_levels)

    df_filtered = df[
        df["Year Published"].astype(int).between(*year_range) &
        df["Title"].str.contains(title_filter, case=False, na=False) &
        df["Author"].str.contains(author_filter, case=False, na=False)
    ]

    if subgenre_filter:
        df_filtered = df_filtered[df_filtered["Subgenre"].isin(subgenre_filter)]

    if spice_filter:
        df_filtered = df_filtered[df_filtered["Spice Level"].isin(spice_filter)]

    st.markdown(f"### 📖 {len(df_filtered)} books found")
    st.dataframe(df_filtered.reset_index(drop=True))
else:
    st.warning("No data found in Google Sheet. Click the scrape button above to begin.")
 
