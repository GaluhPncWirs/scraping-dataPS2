import os
import csv
import time
from downloadImages import download_images
from extractCoverImage import extract_thegamesdb_cover_image

COVER_DIR = "./covers_ps2"
DELAY_SECONDS = 3

def stage3_download_thegamesdb_covers(input_file, output_file):
    os.makedirs(COVER_DIR, exist_ok=True)

    with open(input_file, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)

        if not reader.fieldnames:
            print("CSV kosong atau header tidak valid")
            return

        fieldnames = (*reader.fieldnames,
                      'coverImageUrl',
                      'coverImageLocalPath')

        with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()

            total = 0
            downloaded = 0

            # Cache untuk menghindari extract & download berulang
            cover_cache = {}

            for row in reader:
                game_page = (row.get('thegamesdbGamePage') or '').strip()
                clean_title = row.get('cleanTitle') or row.get('cleanGameTitle', '')

                cover_url = ''
                local_path = ''

                if game_page:
                    try:
                        if game_page in cover_cache:
                            cover_url, local_path = cover_cache[game_page]
                        else:
                            print(f"🖼 Fetching cover: {clean_title}")

                            cover_url = extract_thegamesdb_cover_image(game_page)

                            if cover_url:
                                local_path = download_images(cover_url, COVER_DIR, row["cleanTitle"])

                                if local_path:
                                    row["coverImageUrl"] = cover_url
                                    row["coverImageLocalPath"] = local_path
                                    downloaded += 1
                                    time.sleep(DELAY_SECONDS)

                            cover_cache[game_page] = (cover_url, local_path)

                    except Exception as e:
                        print(f"⚠️ Cover gagal [{clean_title}]: {e}")

                writer.writerow({
                    **row,
                    'coverImageUrl': cover_url,
                    'coverImageLocalPath': local_path
                })

                total += 1
                if total % 50 == 0:
                    print(f"Progress: {total} game")

    print("\n=== Stage 3 selesai ===")
    print(f"Total game     : {total}")
    print(f"Cover tersedia : {downloaded}")
    print(f"Unique covers  : {len(cover_cache)}")

input_file = "../data/tahap_2_gamePS2_game_pages.csv"
output_file = "../data/tahap_3_thegamesdb_with_covers.csv"

stage3_download_thegamesdb_covers(input_file, output_file)
