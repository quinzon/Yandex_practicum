from dataclasses import dataclass

from werkzeug.datastructures import Headers


@dataclass
class Constants:
    AUTHORIZATION_HEADER = 'Authorization'
    BEARER_PREFIX = 'Bearer '
    STATUS_SUCCESS = 'success'


@dataclass
class ErrorMessages:
    ERROR_MISSING_AUTH = 'Missing or invalid Authorization header'
    ERROR_MISSING_ATTRIBUTES = 'Missing required fields'


class ValidationError(Exception):
    pass


def validate_request(json_data: dict) -> tuple:
    user_id = json_data.get('user_id')
    message = json_data.get('message')

    if not user_id or not message:
        raise ValidationError(ErrorMessages.ERROR_MISSING_ATTRIBUTES)

    return user_id, message
