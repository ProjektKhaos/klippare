# cleanup.py
# Rensar gamla uppladdningar, resultat och ZIP-filer för Klippare. Klipparen är byggd av Hans Åberg och KlⒶsse Kod
# Senast uppdaterad: 2026-05-20 | av: KlⒶssⓔ & Ⓐberg

from datetime import datetime, timedelta
from pathlib import Path
import shutil

from config import JOB_MAX_AGE_HOURS, RESULT_DIR, UPLOAD_DIR, ZIP_DIR


def cleanup_old_jobs(max_age_hours=JOB_MAX_AGE_HOURS):
    """Ta bort jobbkataloger och zippar som är äldre än max_age_hours."""
    cutoff = datetime.now().timestamp() - timedelta(hours=max_age_hours).total_seconds()

    for directory in (UPLOAD_DIR, RESULT_DIR):
        Path(directory).mkdir(parents=True, exist_ok=True)
        for item in Path(directory).iterdir():
            if item.name == ".gitkeep":
                continue
            if item.stat().st_mtime < cutoff:
                if item.is_dir():
                    shutil.rmtree(item, ignore_errors=True)
                else:
                    item.unlink(missing_ok=True)

    ZIP_DIR.mkdir(parents=True, exist_ok=True)
    for item in ZIP_DIR.iterdir():
        if item.name == ".gitkeep":
            continue
        if item.stat().st_mtime < cutoff:
            item.unlink(missing_ok=True)


if __name__ == "__main__":
    cleanup_old_jobs()
