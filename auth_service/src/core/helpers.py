import secrets
import string

from starlette.requests import Request


def generate_password(length: int = 8) -> str:
    alphabet = string.ascii_letters + string.digits + string.punctuation
    while True:
        password = ''.join(secrets.choice(alphabet) for _ in range(length))

        if (any(c.isalpha() for c in password) and any(c.isdigit() for c in password) and
                any(c in string.punctuation for c in password)):
            return password


def get_login_info(request: Request) -> tuple:
    user_agent = request.headers.get('user-agent', 'Unknown')
    client_address = request.headers.get('host')
    return user_agent, client_address
