import requests
from bs4 import BeautifulSoup

GENIUS_TOKEN = "ВАШ_ТОКЕН_ОТСЮДА"

def search_song(query):
    """Ищет песню и возвращает исполнителя и ссылку на текст"""
    headers = {"Authorization": f"Bearer {GENIUS_TOKEN}"}
    search_url = f"https://api.genius.com/search?q={query}"
    response = requests.get(search_url, headers=headers)
    data = response.json()

    if data["response"]["hits"]:
        song = data["response"]["hits"][0]["result"]
        return {
            "title": song["title"],
            "artist": song["primary_artist"]["name"],
            "url": song["url"]
        }
    return None


def get_lyrics_from_url(url):
    """Парсит текст с Genius"""
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    lyrics_divs = soup.select("div[data-lyrics-container='true']")
    return "\n".join(div.get_text(separator="\n") for div in lyrics_divs)
