import json

import backoff
import requests
from models import Movie


class ElasticSearchUploader:
    def __init__(self, url, index):
        self.url = url
        self.index = index

    @backoff.on_exception(backoff.expo, (requests.exceptions.ConnectionError,))
    def upload(self, movies: list[Movie]):
        data_list = list()
        for movie in movies:
            data_list.append(json.dumps({
                'index': {
                    '_index': self.index,
                    '_id': movie.id
                }}))
            data_list.append(movie.json())
        data = '\n'.join(data_list)
        data = data + '\n'
        requests.post(self.url + '_bulk', headers={'Content-Type': 'application/x-ndjson'}, data=data)
