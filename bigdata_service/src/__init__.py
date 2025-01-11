import sys
from http import HTTPStatus

from asgiref.wsgi import WsgiToAsgi
from flask import Flask, jsonify

from bigdata_service.src.config import Settings
from bigdata_service.src.kafka import kafka_producer
from bigdata_service.src.logging_config import logger
from bigdata_service.src.routes import events_bp
from bigdata_service.src.utils import ValidationError

sys.path.append('/opt/sentry')
from sentry.sentry_client import SentryClient


def create_app():

    sentry_client = SentryClient()
    app = Flask(__name__)
    app.config.from_object(Settings)

    app.producer = kafka_producer

    app.register_blueprint(events_bp)

    @app.errorhandler(HTTPStatus.INTERNAL_SERVER_ERROR)
    def handle_internal_server_error(_):
        logger.error('An internal error occurred', exc_info=True)
        return {'error': 'Internal Server Error',
                'message': 'Something went wrong'}, HTTPStatus.INTERNAL_SERVER_ERROR

    @app.errorhandler(ValidationError)
    def handle_validation_error(e):
        logger.error('Validation error: %s', str(e))
        return jsonify({'error': str(e)}), HTTPStatus.BAD_REQUEST

    return app


flask_app = create_app()
asgi_app = WsgiToAsgi(flask_app)
