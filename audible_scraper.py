
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_audiobook_info(title, author=None):
    base_url = "https://www.audible.com/search"
    query = f"{title} {author}" if author else title
    params = {"keywords": query}
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(base_url, params=params, headers=headers, timeout=10)
        if response.status_code != 200:
            return {"audiobook": False}

        soup = BeautifulSoup(response.text, "html.parser")
        first_result = soup.find("li", class_="productListItem")

        if not first_result:
            return {"audiobook": False}

        link_tag = first_result.find("a", class_="bc-link")
        audible_link = "https://www.audible.com" + link_tag["href"] if link_tag else None

        narrator_elem = first_result.find("li", class_="narratorLabel")
        narrators = []
        if narrator_elem:
            raw_text = narrator_elem.get_text(strip=True)
            narrators = [n.strip() for n in raw_text.replace("Narrated by:", "").split(",")]

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

def update_audible_info(existing_df, max_days=30):
    now_str = datetime.now().strftime('%Y-%m-%d')
    updated_books = []

    for _, row in existing_df.iterrows():
        title = row["title"]
        author = row["author"]
        last_audio_update = row.get("audio_last_updated", "")
        update_needed = True

        if last_audio_update:
            try:
                last_dt = datetime.strptime(last_audio_update, "%Y-%m-%d")
                if (datetime.now() - last_dt).days < max_days:
                    update_needed = False
            except:
                pass

        if update_needed:
            audio_data = get_audiobook_info(title, author)
            updated_books.append({
                "title": title,
                "author": author,
                "audiobook": "Yes" if audio_data["audiobook"] else "No",
                "audiobook_voices": ", ".join(audio_data.get("audio_voices", [])),
                "audiobook_time": audio_data.get("runtime", ""),
                "audio_last_updated": now_str
            })

    return updated_books
