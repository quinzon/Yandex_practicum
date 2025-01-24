from http import HTTPStatus

from asgiref.wsgi import WsgiToAsgi
from flask import Flask, jsonify

from push_service.src.config import Settings
from push_service.src.logging_config import logger
from push_service.src.routes import message_bp
from push_service.src.utils import ValidationError
from push_service.src.storage import redis_storage


def create_app():
    app = Flask(__name__)
    app.config.from_object(Settings)

    app.register_blueprint(message_bp)

    @app.errorhandler(HTTPStatus.INTERNAL_SERVER_ERROR)
    def handle_internal_server_error(_):
        logger.error('An internal error occurred', exc_info=True)
        return {'error': 'Internal Server Error',
                'message': 'Something went wrong'}, HTTPStatus.INTERNAL_SERVER_ERROR

    @app.errorhandler(ValidationError)
    def handle_validation_error(e):
        logger.error('Validation error: %s', str(e))
        return jsonify({'error': str(e)}), HTTPStatus.BAD_REQUEST

    @app.teardown_appcontext
    async def shutdown_redis(exception=None):
        await redis_storage.redis.close()

    return app


flask_app = create_app()
asgi_app = WsgiToAsgi(flask_app)
