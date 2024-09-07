#!/bin/sh

ELASTIC_HOST="${ELASTIC_HOST:-http://localhost}"
ELASTIC_PORT="${ELASTIC_PORT:-9200}"

until curl -s "$ELASTIC_HOST:$ELASTIC_PORT"; do
  echo "Waiting for Elasticsearch..."
  sleep 5
done


create_index_if_not_exists() {
  INDEX_NAME=$1
  INDEX_SETTINGS=$2

  if curl -s -o /dev/null -w "%{http_code}" "$ELASTIC_HOST:$ELASTIC_PORT/$INDEX_NAME" | grep "200"; then
    echo "Index '$INDEX_NAME' already exists."
  else
    echo "Index '$INDEX_NAME' does not exist. Creating..."
    curl -XPUT "$ELASTIC_HOST:$ELASTIC_PORT/$INDEX_NAME" -H 'Content-Type: application/json' -d"$INDEX_SETTINGS"
    echo "Index '$INDEX_NAME' created successfully"
  fi
}


MOVIES_INDEX_SETTINGS='{
  "settings": {
    "refresh_interval": "1s",
    "analysis": {
      "filter": {
        "english_stop": {
          "type": "stop",
          "stopwords": "_english_"
        },
        "english_stemmer": {
          "type": "stemmer",
          "language": "english"
        },
        "english_possessive_stemmer": {
          "type": "stemmer",
          "language": "possessive_english"
        },
        "russian_stop": {
          "type": "stop",
          "stopwords": "_russian_"
        },
        "russian_stemmer": {
          "type": "stemmer",
          "language": "russian"
        }
      },
      "analyzer": {
        "ru_en": {
          "tokenizer": "standard",
          "filter": [
            "lowercase",
            "english_stop",
            "english_stemmer",
            "english_possessive_stemmer",
            "russian_stop",
            "russian_stemmer"
          ]
        }
      }
    }
  },
  "mappings": {
    "dynamic": "strict",
    "properties": {
      "id": {
        "type": "keyword"
      },
      "imdb_rating": {
        "type": "float"
      },
      "genres": {
        "type": "keyword"
      },
      "title": {
        "type": "text",
        "analyzer": "ru_en",
        "fields": {
          "raw": {
            "type": "keyword"
          }
        }
      },
      "description": {
        "type": "text",
        "analyzer": "ru_en"
      },
      "directors_names": {
        "type": "text",
        "analyzer": "ru_en"
      },
      "actors_names": {
        "type": "text",
        "analyzer": "ru_en"
      },
      "writers_names": {
        "type": "text",
        "analyzer": "ru_en"
      },
      "directors": {
        "type": "nested",
        "dynamic": "strict",
        "properties": {
          "id": {
            "type": "keyword"
          },
          "name": {
            "type": "text",
            "analyzer": "ru_en"
          }
        }
      },
      "actors": {
        "type": "nested",
        "dynamic": "strict",
        "properties": {
          "id": {
            "type": "keyword"
          },
          "name": {
            "type": "text",
            "analyzer": "ru_en"
          }
        }
      },
      "writers": {
        "type": "nested",
        "dynamic": "strict",
        "properties": {
          "id": {
            "type": "keyword"
          },
          "name": {
            "type": "text",
            "analyzer": "ru_en"
          }
        }
      }
    }
  }
}'

create_index_if_not_exists "movies" "$MOVIES_INDEX_SETTINGS"
echo "All indexes created successfully."

python main.py