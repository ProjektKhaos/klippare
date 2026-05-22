# app.py
# Flask-webbapp för Klippare – laddar upp bildark och beskär dem med OpenCV. Klipparen är byggd av Hans Åberg och KlⒶsse Kod
# Senast uppdaterad: 2026-05-20 | av: KlⒶssⓔ & Ⓐberg

from datetime import datetime
from pathlib import Path
import json
import uuid
import zipfile

from flask import Flask, abort, jsonify, redirect, render_template, request, send_file, url_for
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.utils import secure_filename

from cleanup import cleanup_old_jobs
from config import (
    ALLOWED_EXTENSIONS,
    BASE_DIR,
    DEFAULT_PRESET_KEY,
    DOMAIN,
    MAX_CONTENT_LENGTH,
    PRESETS,
    RESULT_DIR,
    UPLOAD_DIR,
    ZIP_DIR,
)
from cropper import crop_icons_from_sheet


app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH


def allowed_file(filename):
    """Kontrollera filändelsen innan filen sparas på servern."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def read_int_form_value(name, default, minimum=0, maximum=100000):
    """Läs heltal från formuläret och håll dem inom rimliga gränser."""
    try:
        value = int(request.form.get(name, default))
    except (TypeError, ValueError):
        value = default
    return max(minimum, min(maximum, value))


def read_settings():
    """Samla OpenCV-värden från POST och fyll på med standardpreset vid behov."""
    defaults = PRESETS[DEFAULT_PRESET_KEY]
    background_color = request.form.get("background_color", "white")
    if background_color not in {"white", "light_gray", "black"}:
        background_color = "white"

    return {
        "padding": read_int_form_value("padding", defaults["padding"], 0, 500),
        "min_area": read_int_form_value("min_area", defaults["min_area"], 1, 10_000_000),
        "threshold_value": read_int_form_value("threshold_value", defaults["threshold_value"], 0, 255),
        "morph_close_kernel_w": read_int_form_value(
            "morph_close_kernel_w", defaults["morph_close_kernel_w"], 1, 501
        ),
        "morph_close_kernel_h": read_int_form_value(
            "morph_close_kernel_h", defaults["morph_close_kernel_h"], 1, 501
        ),
        "dilate_kernel_w": read_int_form_value("dilate_kernel_w", defaults["dilate_kernel_w"], 1, 501),
        "dilate_kernel_h": read_int_form_value("dilate_kernel_h", defaults["dilate_kernel_h"], 1, 501),
        "make_square": request.form.get("make_square") == "on",
        "background_color": background_color,
    }


def create_job_name():
    """Ge varje körning ett läsbart namn med datum och kort UUID."""
    stamp = datetime.now().strftime("%Y-%m-%d-%H_%M")
    short_id = uuid.uuid4().hex[:8]
    return f"klippare-{stamp}-{short_id}"


def create_zip(job_name, result_dir, filenames):
    """Packa alla beskurna PNG-filer i en ZIP som kan laddas ner."""
    ZIP_DIR.mkdir(parents=True, exist_ok=True)
    zip_path = ZIP_DIR / f"{job_name}.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for filename in filenames:
            archive.write(result_dir / filename, arcname=filename)
    return zip_path


def save_metadata(result_dir, metadata):
    """Spara metadata så resultatsidan kan återskapas via /result/<job_id>."""
    (result_dir / "metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")


def load_metadata(job_id):
    """Läs metadata utan att exponera godtyckliga sökvägar."""
    metadata_path = RESULT_DIR / secure_filename(job_id) / "metadata.json"
    if not metadata_path.exists():
        abort(404)
    return json.loads(metadata_path.read_text(encoding="utf-8"))


@app.errorhandler(RequestEntityTooLarge)
def too_large(_error):
    return render_template("index.html", presets=PRESETS, error="Uppladdningen är för stor. Max är 80 MB."), 413


@app.route("/")
def index():
    cleanup_old_jobs()
    return render_template("index.html", presets=PRESETS, error=None)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/process", methods=["POST"])
def process():
    cleanup_old_jobs()
    files = [file for file in request.files.getlist("files") if file and file.filename]
    if not files:
        return render_template("index.html", presets=PRESETS, error="Ingen fil uppladdad."), 400

    invalid_files = [file.filename for file in files if not allowed_file(file.filename)]
    if invalid_files:
        return (
            render_template(
                "index.html",
                presets=PRESETS,
                error=f"Filtypen stöds inte: {', '.join(invalid_files)}.",
            ),
            400,
        )

    settings = read_settings()
    job_name = create_job_name()
    upload_dir = UPLOAD_DIR / job_name
    result_dir = RESULT_DIR / job_name
    upload_dir.mkdir(parents=True, exist_ok=False)
    result_dir.mkdir(parents=True, exist_ok=False)

    uploaded_names = []
    result_files = []
    errors = []

    for file in files:
        safe_name = secure_filename(file.filename)
        upload_path = upload_dir / safe_name
        file.save(upload_path)
        uploaded_names.append(safe_name)

        try:
            new_files = crop_icons_from_sheet(upload_path, result_dir, job_name, len(result_files) + 1, settings)
            result_files.extend(new_files)
        except ValueError as error:
            errors.append(str(error))

    if not result_files:
        return (
            render_template(
                "index.html",
                presets=PRESETS,
                error="Inga objekt hittades. Testa ett annat preset eller sänk MIN_AREA.",
            ),
            400,
        )

    zip_path = create_zip(job_name, result_dir, result_files)
    metadata = {
        "job_id": job_name,
        "uploaded_count": len(uploaded_names),
        "uploaded_names": uploaded_names,
        "result_count": len(result_files),
        "result_files": result_files,
        "settings": settings,
        "zip_name": zip_path.name,
        "errors": errors,
    }
    save_metadata(result_dir, metadata)
    return redirect(url_for("result", job_id=job_name))


@app.route("/result/<job_id>")
def result(job_id):
    metadata = load_metadata(job_id)
    return render_template("result.html", metadata=metadata)


@app.route("/files/<job_id>/<filename>")
def result_file(job_id, filename):
    safe_job_id = secure_filename(job_id)
    safe_filename = secure_filename(filename)
    file_path = RESULT_DIR / safe_job_id / safe_filename
    if not file_path.exists() or file_path.suffix.lower() != ".png":
        abort(404)
    return send_file(file_path, mimetype="image/png")


@app.route("/image/<filename>")
def image_asset(filename):
    """Servera fasta designbilder från projektets image-katalog."""
    safe_filename = secure_filename(filename)
    image_path = BASE_DIR / "image" / safe_filename
    if not image_path.exists() or image_path.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
        abort(404)
    return send_file(image_path)


@app.route("/download/<job_id>")
def download(job_id):
    safe_job_id = secure_filename(job_id)
    zip_path = ZIP_DIR / f"{safe_job_id}.zip"
    if not zip_path.exists():
        abort(404)
    return send_file(zip_path, as_attachment=True, download_name=zip_path.name)


@app.route("/download/header-logo")
def download_header_logo():
    image_path = BASE_DIR / "image" / "klippare_logga_banner.png"
    if not image_path.exists():
        abort(404)
    return send_file(image_path, as_attachment=True, download_name="klippare_logga_banner.png")


@app.route("/health")
def health():
    return jsonify({"status": "ok", "app": "klippare", "domain": DOMAIN})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
