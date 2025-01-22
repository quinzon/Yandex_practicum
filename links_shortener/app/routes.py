import string
import random
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, redirect, abort, render_template
from database import db
from models import ShortenedURL, UserVisit

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
        expiration_date=expiration_date,
        email_confirmed=False
    )

    db.session.add(new_url)
    db.session.commit()

    return jsonify({"short_url": f"http://localhost:8001/{short_id}"}), 201

@shortener_bp.route("/<short_id>", methods=["GET"])
def redirect_to_url(short_id):
    url_entry = ShortenedURL.query.filter_by(short_id=short_id).first()

    if not url_entry:
        return abort(404)

    if url_entry.is_expired():
        return abort(404)

    if not url_entry.email_confirmed:
        return jsonify({"error": "Email confirmation required"}), 403

    visit = UserVisit(user_id=url_entry.user_id, short_id=short_id, visit_time=datetime.utcnow())
    db.session.add(visit)
    db.session.commit()

    return redirect(url_entry.redirect_url)

@shortener_bp.route("/confirm_email/<short_id>", methods=["POST"])
def confirm_email(short_id):
    url_entry = ShortenedURL.query.filter_by(short_id=short_id).first()

    if not url_entry:
        return jsonify({"error": "Invalid short ID"}), 404

    url_entry.email_confirmed = True
    db.session.commit()

    return jsonify({"message": "Email confirmed successfully"}), 200

@shortener_bp.route("/visits/<short_id>", methods=["GET"])
def get_visit_count(short_id):
    visits = UserVisit.query.filter_by(short_id=short_id).count()
    return jsonify({"short_id": short_id, "visit_count": visits}), 200
