
import streamlit as st
import pandas as pd

# Load your CSV
@st.cache_data
def load_data():
    return pd.read_csv("openlibrary_romance_books.csv")

df = load_data()

st.title("📚 Romance Book Explorer")
st.markdown("Filter and explore romance novels with subgenres, tags, and spice levels.")

# Sidebar filters
with st.sidebar:
    st.header("🔍 Filters")
    title_filter = st.text_input("Search by Title")
    author_filter = st.text_input("Search by Author")
    year_range = st.slider("Year Published", 2005, 2025, (2005, 2025))
    subgenres = df["Subgenre"].dropna().unique().tolist()
    subgenre_filter = st.multiselect("Subgenre", subgenres)
    spice_levels = df["Spice Level"].dropna().unique().tolist()
    spice_filter = st.multiselect("Spice Level", spice_levels)

# Apply filters
filtered_df = df[
    df["Year Published"].between(*year_range) &
    df["Title"].str.contains(title_filter, case=False, na=False) &
    df["Author"].str.contains(author_filter, case=False, na=False)
]

if subgenre_filter:
    filtered_df = filtered_df[filtered_df["Subgenre"].isin(subgenre_filter)]

if spice_filter:
    filtered_df = filtered_df[filtered_df["Spice Level"].isin(spice_filter)]

st.markdown(f"### 📖 {len(filtered_df)} books found")
st.dataframe(filtered_df.reset_index(drop=True))
