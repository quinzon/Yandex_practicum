role = {
    'name': 'test_role'
}

already_exist_role = {
    'name': 'existing_role'
}

new_role = {
    'name': 'new_role'
}

roles = [
    {'name': 'test_role1'},
    {'name': 'test_role2'},
]

permission = {
    'name': 'test_permission',
    'http_method': 'post',
    'resource': 'test_resource'
}

new_permission = {
    'name': 'new_permission',
    'http_method': 'post',
    'resource': 'test_resource'
}

already_exist_permission = {
    'name': 'existing_permission',
    'http_method': 'post',
    'resource': 'test_resource'
}

permissions = [
    {
        'name': 'test_role_permission',
        'http_method': 'post',
        'resource': 'test_resource',
    },
    {
        'name': 'test_role_permission2',
        'http_method': 'get',
        'resource': 'test_resource2',
    },
]

already_exist_user = {
    'email': 'already_exist_user@example.com',
    'password': 'strongPassword123!',
    'first_name': 'John',
    'last_name': 'Doe'
}

already_exist_superuser = {
    'email': 'already_exist_superuser@example.com',
    'password': 'strongPassword123!',
    'first_name': 'John',
    'last_name': 'Doe',
}
