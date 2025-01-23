import string
import random
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, redirect, url_for
from database import db
from models import ShortenedURL

shortener_bp = Blueprint("shortener", __name__, url_prefix="/api/v1/shortener")


def generate_short_id(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


@shortener_bp.route("/shorten", methods=["POST"])
def shorten_url():
    data = request.json
    original_url = data.get("url")
    expiration_minutes = data.get("expiration_minutes", 60)

    if not original_url:
        return jsonify({"error": "Missing required 'url' field"}), 400

    short_id = generate_short_id()
    while ShortenedURL.query.filter_by(short_id=short_id).first():
        short_id = generate_short_id()

    expiration_date = datetime.utcnow() + timedelta(minutes=expiration_minutes)

    # Создаем новую запись в базе данных
    new_url = ShortenedURL(
        short_id=short_id,
        original_url=original_url,
        expiration_date=expiration_date,
        redirect_url=original_url  # Мы добавляем redirect_url, если он нужен
    )

    db.session.add(new_url)
    db.session.commit()

    short_url = url_for('shortener.redirect_to_url', short_id=short_id, _external=True)
    short_url = short_url.replace("http://localhost", "http://localhost/api/v1/shortener")

    return jsonify({
        "short_url": short_url,
        "original_url": original_url,
        "expires_at": expiration_date.isoformat()
    }), 201


@shortener_bp.route("/<short_id>", methods=["GET"])
def redirect_to_url(short_id):
    url_entry = ShortenedURL.query.filter_by(short_id=short_id).first()

    if not url_entry or url_entry.is_expired():
        return jsonify({"error": "URL not found or expired"}), 404

    return redirect(url_entry.original_url, code=302)
