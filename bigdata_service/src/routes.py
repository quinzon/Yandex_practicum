from http import HTTPStatus

from flask import Blueprint, request, jsonify

from bigdata_service.src.event_handler import process_event
from bigdata_service.src.utils import validate_request

events_bp = Blueprint('events', __name__)


@events_bp.before_request
def before_request_validation():
    headers = request.headers
    json_data = request.get_json(silent=True)
    request.user_id, request.event_data = validate_request(headers, json_data)


@events_bp.route('/events', methods=['POST'])
async def handle_events():
    event_type = request.event_data['event_type']
    payload = request.event_data['payload']
    user_id = request.user_id

    result = await process_event(event_type, user_id, payload)
    return jsonify(result), HTTPStatus.OK
