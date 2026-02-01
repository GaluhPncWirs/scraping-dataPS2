import requests
import os
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
    "Referer": "https://thegamesdb.net/"
}

def slugify_filename(text):
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "_", text)
    return text.strip("_")

def download_images(image_url, save_dir, game_title, timeout=20):
    """
    Download image dan simpan dengan nama berdasarkan judul game
    """

    try:
        # Tentukan ekstensi dari URL
        ext = os.path.splitext(image_url.split("?")[0])[1].lower()
        if ext not in [".jpg", ".jpeg", ".png", ".webp"]:
            ext = ".jpg"  # fallback aman

        filename = f"{slugify_filename(game_title)}{ext}"
        save_path = os.path.join(save_dir, filename)

        # Skip jika file valid sudah ada
        if os.path.exists(save_path) and os.path.getsize(save_path) > 1024:
            return save_path

        os.makedirs(save_dir, exist_ok=True)

        r = requests.get(
            image_url,
            headers=HEADERS,
            stream=True,
            timeout=timeout
        )
        r.raise_for_status()

        content_type = r.headers.get("Content-Type", "").lower()
        if not content_type.startswith("image/"):
            print(f"⚠️ Skip non-image: {content_type}")
            return ""

        with open(save_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=16384):
                if chunk:
                    f.write(chunk)

        # # Validasi ukuran minimal
        # if os.path.getsize(save_path) < 1024:
        #     os.remove(save_path)
        #     print("⚠️ File terlalu kecil, dihapus")
        #     return ""

        return save_path

    except Exception as e:
        print(f"❌ Download gagal: {e}")
        if os.path.exists(save_path):
            os.remove(save_path)
        return ""
