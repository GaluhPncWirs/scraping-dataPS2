import requests
from bs4 import BeautifulSoup
import time
import random
import csv
import re
from genreKeywords import genre_keywords
from gamePopuler import POPULAR_PS2_GAMES

URL = "https://myrient.erista.me/files/Redump/Sony%20-%20PlayStation%202/"

# Konfigurasi untuk scraping yang ramah
DELAY_MIN = 1  # Delay minimum dalam detik
DELAY_MAX = 3  # Delay maximum dalam detik
REQUEST_TIMEOUT = 10  # Timeout untuk request
SKIP_KEYWORDS = ['(demo)', '(beta)', '(sample)', '(trial)', '(proto)']
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
MAX_DATA = len(POPULAR_PS2_GAMES)

# Headers untuk menghindari deteksi sebagai bot
headers = {
    'User-Agent': USER_AGENT,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
}

def get_base_name(filename):
    """Dapatkan nama dasar file tanpa region dan extension"""
    base = re.sub(r'\s*\([^)]*\)', '', filename)
    base = re.sub(r'\.[^.]+$', '', base)
    return base.strip()

def normalize_title(title):
    title = title.lower()
    title = re.sub(r"\(.*?\)", "", title)
    title = re.sub(r"[^a-z0-9\s]", "", title)
    title = re.sub(r"\s+", " ", title)
    return title.strip()


POPULAR_GAME_MAP = {
    normalize_title(item["title"]): item["rating"]
    for item in POPULAR_PS2_GAMES
}

def get_region(filename):
    """Ekstrak region dari nama file"""
    pattern = r'\(([^)]*(?:USA|Europe|Japan|Korea|Asia|World)[^)]*)\)'
    match = re.search(pattern, filename)
    return match.group(1) if match else None


def determine_genre(game_name):
    game_lowerCase =  game_name.lower()

    for genre, keywords in genre_keywords.items():
        for keyword in keywords :
            if keyword in game_lowerCase:
                return genre
    
    return "Action"

def clean_game_title(filename):
    name = filename.replace('.zip', '')
    name = re.sub(r'\([^)]*\)', '', name)
    name = re.sub(r'\[.*?\]', '', name)
    name = re.sub(r'(Disc \d+|v\d+\.\d+)', '', name, flags=re.IGNORECASE)
    name = ' '.join(name.split())
    return name.strip()

try:
    # Tambahkan delay sebelum request pertama
    time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))
    
    # Request dengan timeout dan headers
    response = requests.get(
        URL, 
        headers=headers, 
        timeout=REQUEST_TIMEOUT
    )
    response.raise_for_status()  # Raise error jika status bukan 200
    
    soup = BeautifulSoup(response.text, "html.parser")

    games_dict = {}

    for row in soup.find_all("tr"):
        cols = row.find_all("td")
        if len(cols) < 3:
            continue

        link = cols[0].find("a")
        if not link or not link.get("href"):
            continue

        file_name = link.text.strip()

        if re.match(r"^\d+", file_name):
            continue

        if any(keyword in file_name.lower() for keyword in SKIP_KEYWORDS):
            continue

        clean_title = clean_game_title(file_name)
        normalized = normalize_title(clean_title)

        # ⛔ FILTER: hanya game populer
        if normalized not in POPULAR_GAME_MAP:
            continue

        rating = POPULAR_GAME_MAP[normalized]

        base_name = get_base_name(file_name)
        region = get_region(file_name)

        item_data = {
            "fileName": file_name,
            "cleanTitle": clean_title,
            "url": URL + link.get("href"),
            "size": cols[1].text.strip(),
            "date": cols[2].text.strip(),
            "genre": determine_genre(clean_title),
            "rating": rating,
            "region": region
        }

        if base_name not in games_dict:
            games_dict[base_name] = item_data
        else:
            # prioritas region
            priority = {"USA": 4, "World": 3, "Europe": 2}
            cur = priority.get(region, 0)
            old = priority.get(games_dict[base_name]["region"], 0)

            if cur > old:
                games_dict[base_name] = item_data

     # Konversi ke list
    data = list(games_dict.values())
    
    # Batasi jika MAX_DATA ditentukan
    if MAX_DATA:
        data = data[:MAX_DATA]

    # Simpan ke CSV
    if data:
        csv_filename = 'hasil_scraping_gamePS2.csv'

        fieldnames = [
            "fileName",
            "cleanTitle",
            "url",
            "date",
            "size",
            "genre",
            "rating"
        ]
        
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(
                csvfile, 
                fieldnames=fieldnames, 
                quoting=csv.QUOTE_NONNUMERIC
            )
            
            writer.writeheader()
            
            for i, item in enumerate(data, 1):
                writer.writerow({
                    k: item[k] for k in fieldnames
                })

                if i % 50 == 0:
                    print(f"Diproses: {i} game")
        
        print(f"\n✓ Berhasil menyimpan {len(data)} game populer PS2")

        print("\nPreview data (5 baris pertama):")
        for item in data[:5]:
            game_name = clean_game_title(item['fileName'])
            print(f"{item['fileName']} → Genre: {determine_genre(game_name)}")
    else:
        print("Tidak ada data yang berhasil di-scrape")
    
except requests.exceptions.Timeout:
    print("Error: Request timeout. Server tidak merespons dalam waktu yang ditentukan.")
except requests.exceptions.ConnectionError:
    print("Error: Gagal terhubung ke server.")
except requests.exceptions.HTTPError as e:
    print(f"Error HTTP: {e}")
except Exception as e:
    print(f"Error tidak terduga: {e}")