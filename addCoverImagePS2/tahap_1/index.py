import csv
import re
from urllib.parse import quote

def clean_game_title(filename):
    name = filename.replace('.zip', '')
    name = re.sub(r'\([^)]*\)', '', name)
    name = re.sub(r'\[.*?\]', '', name)
    name = re.sub(r'(Disc \d+|v\d+\.\d+)', '', name, flags=re.IGNORECASE)
    name = ' '.join(name.split())
    return name.strip()

def generate_thegamesdb_search_url(game_title):
    return f"https://thegamesdb.net/search.php?name={quote(game_title)}&platform=11"

def stage1_add_thegamesdb_search_url(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8', newline='') as outfile:

        reader = csv.DictReader(infile)

        fieldnames = list(reader.fieldnames) + [
            'cleanGameTitle',
            'coverSearchUrl_thegamesdb'
        ]

        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        total = 0
        for row in reader:
            clean_title = clean_game_title(row['fileName'])

            row['cleanGameTitle'] = clean_title
            row['coverSearchUrl_thegamesdb'] = generate_thegamesdb_search_url(clean_title)

            writer.writerow(row)
            total += 1

            if total % 100 == 0:
                print(f"Diproses: {total} game")

        print(f"\nStage 1 selesai — Total: {total} game")

# Jalankan tahap 1
input_file = '../data/hasil_scraping_gamePS2_test.csv'
output_file = '../data/tahap_1_gamePS2_search_urls.csv'

stage1_add_thegamesdb_search_url(input_file, output_file)
