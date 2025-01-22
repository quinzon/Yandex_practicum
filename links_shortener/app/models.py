from database import db
from datetime import datetime, timedelta

class ShortenedURL(db.Model):
    __tablename__ = "shortened_urls"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(128), nullable=False)
    short_id = db.Column(db.String(10), unique=True, nullable=False)
    original_url = db.Column(db.String(2048), nullable=False)
    redirect_url = db.Column(db.String(2048), nullable=False)
    expiration_date = db.Column(db.DateTime, nullable=False)

    def is_expired(self):
        return datetime.utcnow() > self.expiration_date
