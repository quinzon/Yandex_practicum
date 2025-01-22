import logging
from flask import Flask
from database import db
from routes import shortener_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    db.init_app(app)

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    with app.app_context():
        try:
            db.create_all()
            logger.info("Таблицы успешно созданы или уже существуют.")
        except Exception as e:
            logger.error(f"Ошибка при создании таблиц: {e}")

    app.register_blueprint(shortener_bp)

    return app
