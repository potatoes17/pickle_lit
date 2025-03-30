
import requests
from datetime import datetime

def scrape_book_metadata(title):
    try:
        response = requests.get(
            "https://www.googleapis.com/books/v1/volumes",
            params={"q": f'intitle:"{title}"', "maxResults": 1}
        )
        response.raise_for_status()
        data = response.json()

        if "items" not in data or not data["items"]:
            print("No items found for exact title match.")
            return None

        book = data["items"][0]["volumeInfo"]

        # Pull out desired metadata fields
        return {
            "title": book.get("title", ""),
            "author": ", ".join(book.get("authors", [])),
            "isbn": get_isbn(book),
            "series": "",  # No reliable series info in Google Books
            "num_in_series": "",
            "year_published": extract_year(book.get("publishedDate")),
            "publisher": book.get("publisher", ""),
            "page_count": str(book.get("pageCount", "")),
            "spice_level": "",
            "rating": str(book.get("averageRating", "")),
            "subgenre": "",
            "tags": "",
            "description": book.get("description", ""),
            "kindle_unlimited": "",
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "audiobook": "",
            "audiobook_voices": "",
            "audiobook_time": "",
            "graphic_audio": "",
            "graphic_audio_voices": "",
            "graph_audio_time": "",
            "audio_last_updated": ""
        }
    except Exception as e:
        print(f"Scrape failed: {e}")
        return None

def get_isbn(book):
    for identifier in book.get("industryIdentifiers", []):
        if identifier["type"] in ("ISBN_13", "ISBN_10"):
            return identifier["identifier"]
    return ""

def extract_year(published_date):
    if published_date:
        return published_date.split("-")[0]
    return ""
