import csv
import time
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}
REQUEST_TIMEOUT = 15
DELAY_SECONDS = 2

def extract_thegamesdb_game_ids(search_url):
    response = requests.get(search_url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    ids = []
    for a in soup.select("a[href^='./game.php?id=']"):
        href = a.get("href")
        game_id = href.split("id=")[-1]
        if game_id.isdigit():
            ids.append(game_id)

    return list(set(ids))  # deduplicate

def extract_thegamesdb_description(game_page_url):
    try:
        response = requests.get(game_page_url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # TheGamesDB description biasanya di p ini
        desc_p = soup.find("p", class_="game-overview")

        if not desc_p:
            return None

        description = desc_p.get_text(separator=" ", strip=True)
        return description

    except Exception as e:
        print(f"⚠️ Gagal ambil deskripsi: {e}")
        return None


def is_ps2_game(game_id):
    url = f"https://thegamesdb.net/game.php?id={game_id}"

    r = requests.get(url, headers=HEADERS, timeout=15)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    for a in soup.select("a[href^='/platform.php']"):
        href = a.get("href", "")
        if "id=11" in href:
            return True

    return False


def resolve_thegamesdb_ps2_game_page(search_url):
    try:
        game_ids = extract_thegamesdb_game_ids(search_url)

        if not game_ids:
            print("   ⚠️ No game IDs found")
            return None

        for game_id in game_ids:
            print(f"   🔍 Checking ID {game_id}")

            if not is_ps2_game(game_id):
                time.sleep(2)
                continue

            print(f"   ✅ PS2 FOUND: {game_id}")
            game_page_url = f"https://thegamesdb.net/game.php?id={game_id}"

            # === FETCH GAME PAGE SEKALI ===
            response = requests.get(
                game_page_url,
                headers=HEADERS,
                timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # === AMBIL DESKRIPSI ===
            desc_p = soup.find("p", class_="game-overview")
            description = (
                desc_p.get_text(separator=" ", strip=True)
                if desc_p else None
            )

            return {
                "gamePage": game_page_url,
                "description": description
            }

    except Exception as e:
        print(f"⚠️ Resolve gagal: {e}")

    return None



def stage2_resolve_thegamesdb_game_page(input_file, output_file):
    with open(input_file, "r", encoding='utf-8') as infile:
        reader = csv.DictReader(infile)

        if not reader.fieldnames:
            print("CSV kosong atau header tidak valid")
            return
        
        fieldnames = (*reader.fieldnames, 'thegamesdbGamePage', 'thegamesdbDescription')

        with open(output_file, "w", encoding="utf-8", newline="") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()

            total = 0
            success = 0

            # cache: search_url → (game_page, description)
            resolve_cache = {}

            for row in reader:
                search_url = row.get('coverSearchUrl_thegamesdb')
                clean_title = row.get('cleanTitle') or row.get('cleanGameTitle', '')

                game_page = ''
                description = ''

                if search_url:
                    if search_url in resolve_cache:
                        game_page, description = resolve_cache[search_url]
                    else:
                        print(f"🔎 Resolving: {clean_title}")
                        result = resolve_thegamesdb_ps2_game_page(search_url)

                        if result:
                            game_page = result.get('gamePage', '')
                            description = result.get('description', '')

                            success += 1

                        resolve_cache[search_url] = (game_page, description)
                        time.sleep(DELAY_SECONDS)

                writer.writerow({
                    **row,
                    'thegamesdbGamePage': game_page,
                    'thegamesdbDescription': description
                })

                total += 1
                if total % 50 == 0:
                    print(f"Progress: {total} game")


    print("\n=== Stage 2 selesai ===")
    print(f"Total game      : {total}")
    print(f"Berhasil resolve: {success}")
    print(f"Cache hit       : {len(resolve_cache)} unique search URL")

# Jalankan tahap 2
input_file = '../data/tahap_1_gamePS2_search_urls.csv'
output_file = '../data/tahap_2_gamePS2_game_pages.csv'

stage2_resolve_thegamesdb_game_page(input_file, output_file)