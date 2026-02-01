import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def extract_thegamesdb_cover_image(game_page_url):
    try: 
        response = requests.get(game_page_url, headers=HEADERS, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        img = soup.select_one("img[src*='/images/thumb/boxart/front/']")
        if not img:
            return ""
        
        src = img.get("src", "").strip()
        if not src:
            return ""

        if src.startswith("/"):
            src = "https://cdn.thegamesdb.net" + src
        
        return src
    
    except Exception as e:
        print(f"⚠️ Gagal ambil cover: {e}")
        return ""