import requests
from bs4 import BeautifulSoup
import time
import random
import csv
import re

URL = "https://myrient.erista.me/files/Redump/Sony%20-%20PlayStation%202/"

# Konfigurasi untuk scraping yang ramah
DELAY_MIN = 1  # Delay minimum dalam detik
DELAY_MAX = 3  # Delay maximum dalam detik
REQUEST_TIMEOUT = 10  # Timeout untuk request
SKIP_ITEMS = ['Parent directory/', '..', '.', '../']
SKIP_KEYWORDS = ['(demo)', '(beta)', '(sample)', '(trial)', '(proto)']
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
MAX_DATA = 500

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

def get_region(filename):
    """Ekstrak region dari nama file"""
    pattern = r'\(([^)]*(?:USA|Europe|Japan|Korea|Asia|World)[^)]*)\)'
    match = re.search(pattern, filename)
    return match.group(1) if match else None


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
        if len(cols) >= 3:
            link = cols[0].find("a")
            if link and link.get("href"):
                file_name = link.text.strip()

                if file_name in SKIP_ITEMS or file_name.endswith("/"):
                    continue

                if any(keyword in file_name.lower() for keyword in SKIP_KEYWORDS):
                    continue

                base_name = get_base_name(file_name)
                region = get_region(file_name)

                item_data = {
                    "fileName": file_name,
                    "url": URL + link.get("href"),
                    "date": cols[1].text.strip(),
                    "size": cols[2].text.strip(),
                    "region": region
                }

                # Jika game belum ada, tambahkan
                if base_name not in games_dict:
                    games_dict[base_name] = item_data
                else:
                    # Prioritas region
                    priority = {
                        'USA': 4,
                        'World': 3,
                        'Europe': 2
                    }
                    
                    current_priority = 0
                    existing_priority = 0
                
                    if region:
                            for key in priority:
                                if key in region:
                                    current_priority = priority[key]
                                    break
                        
                    existing_region = games_dict[base_name]["region"]
                    if existing_region:
                        for key in priority:
                            if key in existing_region:
                                existing_priority = priority[key]
                                break
                    
                    # Replace jika prioritas lebih tinggi
                    if current_priority > existing_priority:
                        games_dict[base_name] = item_data

     # Konversi ke list
    data = list(games_dict.values())
    
    # Batasi jika MAX_DATA ditentukan
    if MAX_DATA:
        data = data[:MAX_DATA]

    # Simpan ke CSV
    if data:
        csv_filename = 'hasil_scraping_gamePS2.csv'
        
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['fileName', 'url', 'date', 'size']
            writer = csv.DictWriter(
                csvfile, 
                fieldnames=fieldnames, 
                quoting=csv.QUOTE_NONNUMERIC
            )
            
            writer.writeheader()
            # Hapus kolom 'region' sebelum menulis
            for item in data:
                writer.writerow({k: v for k, v in item.items() if k != 'region'})
        
        print(f"✓ Berhasil menyimpan {len(data)} data ke '{csv_filename}'")
        print("  (Prioritas: USA > World > Europe > lainnya)")
        
        print("\nPreview data (5 baris pertama):")
        for item in data[:5]:
            print(f"{item['fileName']} - Region: {item['region']}")
    else:
        print("Tidak ada data yang berhasil di-scrape")

    # if data :
    #     csv_fileName = "hasil_scraping_gamePS2.csv"

    #     with open(csv_fileName, "w", newline="", encoding="utf-8") as csvfile:
    #         fieldName = ["fileName", "url", "date", "size"]
    #         writer = csv.DictWriter(csvfile, fieldnames=fieldName, quoting=csv.QUOTE_NONNUMERIC)

    #         writer.writeheader()
    #         writer.writerows(data)
        
    #     print(f"✓ Berhasil menyimpan {len(data)} data ke '{csv_fileName}'")
    #     print(f"  (Dibatasi maksimal {MAX_DATA} data)")
    
    #     print("\nPreview data (5 baris pertama):")
    #     for item in data[:5]:
    #         print(item)
    # else:
    #     print("Tidak ada data yang berhasil di-scrape")
    
except requests.exceptions.Timeout:
    print("Error: Request timeout. Server tidak merespons dalam waktu yang ditentukan.")
except requests.exceptions.ConnectionError:
    print("Error: Gagal terhubung ke server.")
except requests.exceptions.HTTPError as e:
    print(f"Error HTTP: {e}")
except Exception as e:
    print(f"Error tidak terduga: {e}")