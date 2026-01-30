import requests
import os

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
    "Referer": "https://thegamesdb.net/"
}

def download_images(url, save_path, timeout=20):
    try:
        # Skip jika file sudah ada
        if os.path.exists(save_path) and os.path.getsize(save_path) > 0:
            return True

        r = requests.get(
            url,
            headers=HEADERS,
            stream=True,
            timeout=timeout
        )
        r.raise_for_status()

        content_type = r.headers.get("Content-Type", "").lower()
        if not any(x in content_type for x in ["image/jpeg", "image/png", "image/webp"]):
            print(f"⚠️ Bukan image: {content_type}")
            return False

        # Pastikan folder ada
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        with open(save_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        # Validasi hasil
        if os.path.getsize(save_path) < 1024:
            print("⚠️ File terlalu kecil, kemungkinan error image")
            os.remove(save_path)
            return False

        return True

    except Exception as e:
        print(f"❌ Download gagal: {e}")
        if os.path.exists(save_path):
            os.remove(save_path)
        return False
