from database import db
from datetime import datetime

class ShortenedURL(db.Model):
    """Модель сокращённых ссылок."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False)
    short_id = db.Column(db.String(10), unique=True, nullable=False)
    original_url = db.Column(db.String(2048), nullable=False)
    redirect_url = db.Column(db.String(2048), nullable=False)
    expiration_date = db.Column(db.DateTime, nullable=False)
    email_confirmed = db.Column(db.Boolean, default=False)

    def is_expired(self):
        """Проверка истечения срока действия ссылки."""
        return datetime.utcnow() > self.expiration_date

class UserVisit(db.Model):
    """Модель посещений сокращённых ссылок."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False)
    short_id = db.Column(db.String(10), nullable=False)
    visit_time = db.Column(db.DateTime, nullable=False)
