from __future__ import annotations
import os, uuid
from pathlib import Path
from flask import Flask, render_template, request, jsonify, url_for, send_from_directory
from werkzeug.utils import secure_filename
from parking_analyzer import ParkingAnalyzer

ROOT = Path(__file__).resolve().parent
UPLOAD_DIR = ROOT / "static" / "uploads"
RESULT_DIR = ROOT / "static" / "results"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
RESULT_DIR.mkdir(parents=True, exist_ok=True)
ALLOWED = {"png", "jpg", "jpeg", "webp", "bmp"}

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 15 * 1024 * 1024
analyzer = ParkingAnalyzer()

@app.get("/")
def index():
    return render_template("index.html")

@app.post("/process")
def process():
    uploaded = request.files.get("image")
    if not uploaded or not uploaded.filename:
        return jsonify(error="Выберите фотографию парковки."), 400
    ext = uploaded.filename.rsplit(".", 1)[-1].lower() if "." in uploaded.filename else ""
    if ext not in ALLOWED:
        return jsonify(error="Поддерживаются JPG, JPEG, PNG и WEBP."), 400
    token = uuid.uuid4().hex[:12]
    safe = secure_filename(uploaded.filename) or "parking.jpg"
    input_path = UPLOAD_DIR / f"{token}_{safe}"
    uploaded.save(input_path)
    try:
        result = analyzer.analyze(input_path)
        output_name = f"{token}_result.jpg"
        result["image"].save(RESULT_DIR / output_name, quality=92)
        return jsonify(
            result_url=url_for("result_file", filename=output_name),
            occupied=result["occupied"],
            processing_ms=result["processing_ms"],
        )
    except Exception as exc:
        app.logger.exception("Analysis error")
        return jsonify(error=f"Не удалось выполнить анализ: {exc}"), 500
    finally:
        input_path.unlink(missing_ok=True)

@app.get("/results/<path:filename>")
def result_file(filename):
    return send_from_directory(RESULT_DIR, filename)

@app.get("/health")
def health():
    return jsonify(status="ok", model=analyzer.model_status)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=False)
