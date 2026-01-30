import csv
import time
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

DELAY_SECONDS = 2

def extract_thegamesdb_game_ids(search_url):
    r = requests.get(search_url, headers=HEADERS, timeout=15)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    ids = []
    for a in soup.select("a[href^='./game.php?id=']"):
        href = a.get("href")
        game_id = href.split("id=")[-1]
        if game_id.isdigit():
            ids.append(game_id)

    return list(set(ids))  # deduplicate

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
            return ""

        for game_id in game_ids:
            print(f"   🔍 Checking ID {game_id}")

            if is_ps2_game(game_id):
                print(f"   ✅ PS2 FOUND: {game_id}")
                return f"https://thegamesdb.net/game.php?id={game_id}"

            time.sleep(2)

    except Exception as e:
        print(f"⚠️ Resolve gagal: {e}")

    return ""


def stage2_resolve_thegamesdb_game_page(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8', newline='') as outfile:

        reader = csv.DictReader(infile)

        fieldnames = list(reader.fieldnames) + ['thegamesdbGamePage']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        total = 0
        success = 0

        for row in reader:
            search_url = row.get('coverSearchUrl_thegamesdb', '')

            if search_url:
                print(f"🔎 Resolving: {row.get('cleanGameTitle', '')}")
                game_page = resolve_thegamesdb_ps2_game_page(search_url)
                row['thegamesdbGamePage'] = game_page

                if game_page:
                    success += 1
            else:
                row['thegamesdbGamePage'] = ''

            writer.writerow(row)
            total += 1

            if total % 50 == 0:
                print(f"Progress: {total} game")

            time.sleep(DELAY_SECONDS)

        print("\n=== Stage 2 selesai ===")
        print(f"Total game     : {total}")
        print(f"Berhasil resolve: {success}")

# Jalankan tahap 2
input_file = '../data/tahap_1_gamePS2_search_urls.csv'
output_file = '../data/tahap_2_gamePS2_game_pages.csv'

stage2_resolve_thegamesdb_game_page(input_file, output_file)
# resolve_thegamesdb_ps2_game_page("https://thegamesdb.net/search.php?name=007%20-%20From%20Russia%20with%20Love&platform=11")