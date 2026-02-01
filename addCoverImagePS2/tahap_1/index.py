import csv
from urllib.parse import quote

def generate_thegamesdb_search_url(game_title):
    return f"https://thegamesdb.net/search.php?name={quote(game_title)}&platform=11"

def stage1_add_thegamesdb_search_url(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)

        if not reader.fieldnames:
            print("CSV kosong atau header tidak ditemukan")
            return

        # Fieldnames baru (gunakan tuple → lebih ringan)
        fieldnames = (*reader.fieldnames,
                      'coverSearchUrl_thegamesdb')

        with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()

            total = 0
            for row in reader:
                file_name = row.get('cleanTitle')
                if not file_name:
                    continue

                # Hindari mutasi row langsung (lebih aman)
                writer.writerow({
                    **row,
                    'coverSearchUrl_thegamesdb':
                        generate_thegamesdb_search_url(file_name)
                })

                total += 1
                if total % 100 == 0:
                    print(f"Diproses: {total} game")

    print(f"\nStage 1 selesai — Total: {total} game")


# Jalankan tahap 1
input_file = '../data/hasil_scraping_gamePS2.csv'
output_file = '../data/tahap_1_gamePS2_search_urls.csv'

stage1_add_thegamesdb_search_url(input_file, output_file)
