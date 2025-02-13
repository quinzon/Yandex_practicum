import uuid
from copy import deepcopy

import pytest

from ugc_service.tests.functional.testdata.bookmark_data import base_bookmark_data
from ugc_service.tests.functional.testdata.rating_data import base_rating_create_data
from ugc_service.tests.functional.testdata.review_data import \
    review_create_data as base_review_create_data


@pytest.fixture
def unique_rating_create_data():
    data = deepcopy(base_rating_create_data)
    data['user_id'] = f'user_{uuid.uuid4()}'
    data['film_id'] = f'film_{uuid.uuid4()}'
    return data


@pytest.fixture
def unique_review_create_data():
    data = deepcopy(base_review_create_data)
    data['film_id'] = str(uuid.uuid4())
    return data


@pytest.fixture
def unique_bookmark_data():
    data = deepcopy(base_bookmark_data)
    data['film_id'] = f'film_{uuid.uuid4()}'
    return data
