
import requests
from bs4 import BeautifulSoup
import re

def get_audiobook_info(title, author=None):
    """
    Scrapes Audible for audiobook info including narrator(s) and runtime.
    Returns a dictionary with audiobook metadata.
    """
    base_url = "https://www.audible.com/search"
    query = f"{title} {author}" if author else title
    params = {"keywords": query}
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(base_url, params=params, headers=headers, timeout=10)
        if response.status_code != 200:
            return {"audiobook": False}

        soup = BeautifulSoup(response.text, "html.parser")
        first_result = soup.find("li", class_="productListItem")

        if not first_result:
            return {"audiobook": False}

        # Extract link
        link_tag = first_result.find("a", class_="bc-link")
        audible_link = "https://www.audible.com" + link_tag["href"] if link_tag else None

        # Extract narrator(s)
        narrator_elem = first_result.find("li", class_="narratorLabel")
        narrators = []
        if narrator_elem:
            raw_text = narrator_elem.get_text(strip=True)
            narrators = [n.strip() for n in raw_text.replace("Narrated by:", "").split(",")]

        # Extract runtime
        runtime_elem = first_result.find("li", class_="runtimeLabel")
        runtime = runtime_elem.get_text(strip=True).replace("Length: ", "") if runtime_elem else None

        return {
            "audiobook": True,
            "audio_voices": narrators,
            "runtime": runtime,
            "audible_link": audible_link
        }

    except Exception as e:
        print(f"Error fetching audiobook info: {e}")
        return {"audiobook": False}
