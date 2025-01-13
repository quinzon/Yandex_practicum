import base64
import json
from dataclasses import dataclass

from werkzeug.datastructures import Headers


@dataclass
class Constants:
    AUTHORIZATION_HEADER = 'Authorization'
    BEARER_PREFIX = 'Bearer '
    STATUS_SUCCESS = 'success'


@dataclass
class RequiredFields:
    EVENT_TYPE = 'event_type'
    PAYLOAD = 'payload'


@dataclass
class ErrorMessages:
    ERROR_MISSING_AUTH = 'Missing or invalid Authorization header'
    ERROR_INVALID_PAYLOAD = 'Missing required fields'
    ERROR_PRODUCER = 'Failed to process event'


class ValidationError(Exception):
    pass


def get_token_payload(token: str) -> dict:
    try:
        payload_part = token.split('.')[1]
        payload_decoded = base64.urlsafe_b64decode(payload_part + '=' * (-len(payload_part) % 4))
        return json.loads(payload_decoded)
    except Exception as exc:
        raise ValidationError(ErrorMessages.ERROR_MISSING_AUTH) from exc


def validate_request(headers: Headers, json_data: dict) -> tuple:
    auth_header = headers.get(Constants.AUTHORIZATION_HEADER)
    if not auth_header or not auth_header.startswith(Constants.BEARER_PREFIX):
        raise ValidationError(ErrorMessages.ERROR_MISSING_AUTH)

    token = auth_header.split(Constants.BEARER_PREFIX)[1]
    token_payload = get_token_payload(token)
    user_id = token_payload.get('sub', 'unknown_user')

    if (not json_data or
            RequiredFields.EVENT_TYPE not in json_data or
            RequiredFields.PAYLOAD not in json_data):
        raise ValidationError(ErrorMessages.ERROR_INVALID_PAYLOAD)

    return user_id, json_data
