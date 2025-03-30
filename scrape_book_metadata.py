
import requests
from datetime import datetime
from save_to_postgres import upsert_books

def extract_year(date_str):
    if date_str and len(date_str) >= 4:
        try:
            return int(date_str[:4])
        except:
            return None
    return None

def scrape_book_metadata(title):
    try:
        response = requests.get(
            "https://www.googleapis.com/books/v1/volumes",
            params={"q": f'intitle:"{title}"', "maxResults": 1}
        )
        response.raise_for_status()
        data = response.json()

        if "items" not in data or not data["items"]:
            print("No results found for title:", title)
            return None

        book = data["items"][0]["volumeInfo"]
        identifiers = book.get("industryIdentifiers", [])

        isbn = ""
        isbn_13 = ""
        for ident in identifiers:
            if ident["type"] == "ISBN_13":
                isbn_13 = ident["identifier"]
            elif ident["type"] == "ISBN_10":
                isbn = ident["identifier"]

        book_entry = {
            "title": book.get("title", ""),
            "author": ", ".join(book.get("authors", [])),
            "isbn": isbn,
            "isbn_13": isbn_13,
            "series": "",
            "num_in_series": "",
            "year_published": extract_year(book.get("publishedDate")),
            "page_count": book.get("pageCount", None),
            "spice_level": None,
            "rating": book.get("averageRating", None),
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

        return book_entry

    except Exception as e:
        print(f"Scrape failed for '{title}':", e)
        return None
