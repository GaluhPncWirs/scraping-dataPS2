import os
import csv
import time
import requests
from bs4 import BeautifulSoup
from downloadImages import download_images

COVER_DIR = "./covers_ps2"
os.makedirs(COVER_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def extract_thegamesdb_cover_image(game_page_url):
    r = requests.get(game_page_url, headers=HEADERS, timeout=15)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    covers = []

    for img in soup.select("img[src*='/images/thumb/boxart/front/']"):
        src = img.get("src")
        if not src:
            continue

        # Normalize URL
        if src.startswith("/"):
            src = "https://cdn.thegamesdb.net" + src

        covers.append(src)

    if not covers:
        return ""
    return covers[0]

def stage3_download_thegamesdb_covers(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8', newline='') as outfile:

        reader = csv.DictReader(infile)

        fieldnames = list(reader.fieldnames) + [
            'coverImageUrl',
            'coverImageLocalPath'
        ]

        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        total = 0
        downloaded = 0

        for row in reader:
            game_page = row.get('thegamesdbGamePage', '').strip()
            row['coverImageUrl'] = ''
            row['coverImageLocalPath'] = ''

            if not game_page:
                writer.writerow(row)
                continue

            try:
                print(f"🖼 Fetching cover: {row.get('cleanGameTitle', '')}")

                cover_url = extract_thegamesdb_cover_image(game_page)

                if cover_url:
                    game_id = game_page.split("id=")[-1]
                    ext = os.path.splitext(cover_url)[1]
                    filename = f"{game_id}{ext}"
                    save_path = os.path.join(COVER_DIR, filename)

                    success = download_images(cover_url, save_path)

                    if success:
                        row['coverImageUrl'] = cover_url
                        row['coverImageLocalPath'] = save_path
                        downloaded += 1

                time.sleep(2)

            except Exception as e:
                print(f"⚠️ Cover gagal: {e}")

            writer.writerow(row)
            total += 1

            if total % 50 == 0:
                print(f"Progress: {total} game")

        print("\n=== Stage 3 selesai ===")
        print(f"Total game      : {total}")
        print(f"Cover terunduh  : {downloaded}")

input_file = "../data/tahap_2_gamePS2_game_pages.csv"
output_file = "../data/tahap_3_thegamesdb_with_covers.csv"

stage3_download_thegamesdb_covers(input_file, output_file)
# extract_thegamesdb_cover_image("https://thegamesdb.net/search.php?name=0%20Story&platform=11,https://thegamesdb.net/game.php?id=97320")

