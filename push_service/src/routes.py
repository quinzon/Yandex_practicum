from flask import Blueprint, request, jsonify

from push_service.src.utils import validate_request
from push_service.src.push_handler import push_sender

message_bp = Blueprint('message', __name__)


@message_bp.before_request
def before_request_validation():
    json_data = request.get_json(silent=True)
    user_id, message = validate_request(json_data)
    request.user_id = user_id
    request.message = message


@message_bp.route('/send_message', methods=['POST'])
async def handle_messages():
    user_id = request.user_id
    message = request.message
    print('---user-message---', user_id, message)

    await push_sender(user_id, message)
    return jsonify({'message': 'Ресурс успешно создан'}), 201
