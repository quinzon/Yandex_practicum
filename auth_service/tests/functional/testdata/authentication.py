valid_user = {
    'email': 'test@example.com',
    'password': 'strongPassword123!',
    'first_name': 'John',
    'last_name': 'Doe'
}

valid_login = {
    'email': 'test@example.com',
    'password': 'strongPassword123!'
}

invalid_email_user = {
    'email': 'invalid_email',
    'password': 'strongPassword123!',
    'first_name': 'John',
    'last_name': 'Doe'
}

invalid_password_user = {
    'email': 'test@example.com',
    'password': '123',
    'first_name': 'John',
    'last_name': 'Doe'
}

non_existent_user_login = {
    'email': 'nonexistent@example.com',
    'password': 'strongPassword123!'
}

wrong_password_login = {
    'email': 'test@example.com',
    'password': 'wrongPassword!'
}

invalid_refresh_token = {
    'refresh_token': 'invalid_refresh_token'
}
