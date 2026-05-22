# config.py
# Central konfiguration för Klippare. Klipparen är byggd av Hans Åberg och KlⒶsse Kod
# Senast uppdaterad: 2026-05-20 | av: KlⒶssⓔ & Ⓐberg

from pathlib import Path
import os


# Flask stoppar uppladdningen om summan av filerna/formuläret går över gränsen.
MAX_CONTENT_LENGTH = 80 * 1024 * 1024

# Endast bildformat som OpenCV normalt kan läsa släpps igenom.
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

# Alla sökvägar räknas från projektkatalogen så appen inte beror på var den startas.
BASE_DIR = Path(__file__).resolve().parent
STORAGE_DIR = BASE_DIR / "storage"
UPLOAD_DIR = STORAGE_DIR / "uploads"
RESULT_DIR = STORAGE_DIR / "results"
ZIP_DIR = STORAGE_DIR / "zips"

# cleanup.py rensar jobb som är äldre än detta antal timmar.
JOB_MAX_AGE_HOURS = 24

# Publik driftinformation används i health-route och dokumentation.
APP_NAME = "klippare"
DOMAIN = os.environ.get("KLIPPARE_DOMAIN", "example.com")

# Presets fyller formuläret och används även som säkra defaults i backend.
PRESETS = {
    "standard_amyralen": {
        "label": "Standard Ark",
        "padding": 20,
        "min_area": 4000,
        "threshold_value": 245,
        "morph_close_kernel_w": 25,
        "morph_close_kernel_h": 25,
        "dilate_kernel_w": 18,
        "dilate_kernel_h": 18,
    },
    "small_trash": {
        "label": "Om småskräp blir egna bilder",
        "padding": 20,
        "min_area": 8000,
        "threshold_value": 235,
        "morph_close_kernel_w": 25,
        "morph_close_kernel_h": 25,
        "dilate_kernel_w": 18,
        "dilate_kernel_h": 18,
    },
    "icons_cut_or_split": {
        "label": "Om ikoner kapas eller delas upp",
        "padding": 35,
        "min_area": 3000,
        "threshold_value": 245,
        "morph_close_kernel_w": 35,
        "morph_close_kernel_h": 35,
        "dilate_kernel_w": 25,
        "dilate_kernel_h": 25,
    },
    "icons_merge": {
        "label": "Om flera ikoner slås ihop",
        "padding": 15,
        "min_area": 4000,
        "threshold_value": 245,
        "morph_close_kernel_w": 15,
        "morph_close_kernel_h": 15,
        "dilate_kernel_w": 10,
        "dilate_kernel_h": 10,
    },
}

DEFAULT_PRESET_KEY = "standard_amyralen"
