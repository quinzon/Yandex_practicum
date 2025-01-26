import logging
from flask import Flask
from flask_migrate import Migrate
from sqlalchemy.exc import SQLAlchemyError
from database import db
from routes import shortener_bp
from config import settings


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = settings.SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = settings.SQLALCHEMY_TRACK_MODIFICATIONS

    db.init_app(app)
    migrate = Migrate(app, db)

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    with app.app_context():
        try:
            logger.info("Приложение успешно инициализировано.")
        except SQLAlchemyError as db_error:
            logger.error(f"Ошибка при работе с базой данных: {db_error}")
        except Exception as e:
            logger.error(f"Непредвиденная ошибка: {e}")

    app.register_blueprint(shortener_bp)

    return app
