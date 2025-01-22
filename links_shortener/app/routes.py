import string
import random
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, redirect, abort
from database import db
from models import ShortenedURL

shortener_bp = Blueprint("shortener", __name__)

def generate_short_id(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

@shortener_bp.route("/shorten", methods=["POST"])
def shorten_url():
    data = request.json
    user_id = data.get("user_id")
    original_url = data.get("url")
    redirect_url = data.get("redirect_url")
    expiration_minutes = data.get("expiration_minutes", 60)

    if not user_id or not original_url or not redirect_url:
        return jsonify({"error": "Missing required fields"}), 400

    short_id = generate_short_id()
    while ShortenedURL.query.filter_by(short_id=short_id).first():
        short_id = generate_short_id()

    expiration_date = datetime.utcnow() + timedelta(minutes=expiration_minutes)

    new_url = ShortenedURL(
        user_id=user_id,
        short_id=short_id,
        original_url=original_url,
        redirect_url=redirect_url,
        expiration_date=expiration_date
    )

    db.session.add(new_url)
    db.session.commit()

    return jsonify({"short_url": f"http://localhost:8001/{short_id}"}), 201

@shortener_bp.route("/<short_id>", methods=["GET"])
def redirect_to_url(short_id):
    url_entry = ShortenedURL.query.filter_by(short_id=short_id).first()

    if not url_entry or url_entry.is_expired():
        abort(404)

    return redirect(url_entry.redirect_url)
