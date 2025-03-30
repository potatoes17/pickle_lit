
import requests
from datetime import datetime
import time

def scrape_book_metadata(title_query):
    time.sleep(1.5)  # Respectful delay
    url = f"https://www.googleapis.com/books/v1/volumes?q={title_query}"
    response = requests.get(url)
    
    if response.status_code != 200:
        return None

    data = response.json()
    items = data.get("items")
    if not items:
        return None

    volume = items[0]["volumeInfo"]

    title = volume.get("title", title_query)
    authors = ", ".join(volume.get("authors", []))
    publisher = volume.get("publisher", "")
    year = volume.get("publishedDate", "")[:4]
    description = volume.get("description", "")
    page_count = volume.get("pageCount", "")
    categories = volume.get("categories", [])
    subgenre = categories[0] if categories else ""
    isbn = ""

    for identifier in volume.get("industryIdentifiers", []):
        if identifier["type"] in ("ISBN_13", "ISBN_10"):
            isbn = identifier["identifier"]
            break

    return {
        "title": title,
        "author": authors,
        "isbn": isbn,
        "series": "",
        "num_in_series": "",
        "year_published": year,
        "publisher": publisher,
        "page_count": str(page_count),
        "spice_level": "",
        "rating": "",
        "subgenre": subgenre,
        "tags": subgenre,
        "description": description,
        "kindle_unlimited": "",
        "last_updated": datetime.now().strftime('%Y-%m-%d'),
        "audiobook": "",
        "audiobook_voices": "",
        "audiobook_time": "",
        "graphic_audio": "",
        "graphic_audio_voices": "",
        "graph_audio_time": "",
        "audio_last_updated": ""
    }
