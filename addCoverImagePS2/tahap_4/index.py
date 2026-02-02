import cloudinary
import cloudinary.api
import csv
import csv
import re
from dotenv import load_dotenv
import os

load_dotenv()

# Nama file CSV output
CSV_OUTPUT = "dataGamePS2_done.csv"

cloudinary.config(
    cloud_name=os.getenv("CLOUD_NAME"),
    api_key=os.getenv("API_KEY"),
    api_secret=os.getenv("API_SECRET"),
    secure=True
)

INPUT_CSV = "../data/tahap_3_thegamesdb_with_covers.csv"
OUTPUT_CSV = "../data/dataGamePS2_done.csv"

def fetch_all_images():
    resources = []
    next_cursor = None

    while True:
        result = cloudinary.api.resources(
            type="upload",
            resource_type="image",
            max_results=500,
            next_cursor=next_cursor
        )

        resources.extend(result["resources"])
        next_cursor = result.get("next_cursor")

        if not next_cursor:
            break

    return resources


images = fetch_all_images()

# Buat mapping: filename → secure_url
cloudinary_map = {}

for img in images:
    filename = img["public_id"].split("/")[-1].lower()
    cloudinary_map[filename] = img["secure_url"]

def slugify_filename(text):
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "_", text)
    return text.strip("_")

with open(INPUT_CSV, newline="", encoding="utf-8") as infile:
    reader = csv.DictReader(infile)
    fieldnames = reader.fieldnames + ["url_image"]

    rows = []

    for row in reader:
        slug = slugify_filename(row["cleanTitle"])

        matched_url = ""

        for filename, url in cloudinary_map.items():
            if slug in filename:
                matched_url = url
                break

        row["url_image"] = matched_url
        rows.append(row)


with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as outfile:
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)


print("✅ CSV berhasil ditambahkan url_image dari Cloudinary")
