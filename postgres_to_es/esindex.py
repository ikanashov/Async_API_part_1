import json

from etlsettings import config


ES_SETTINGS = {
  'index': {'number_of_shards': 1,'number_of_replicas': 0},
  'refresh_interval': '1s',
  'analysis': {
    'filter': {
      'english_stop': {'type': 'stop', 'stopwords': '_english_'},
      'english_stemmer': {'type': 'stemmer', 'language': 'english'},
      'english_possessive_stemmer': {'type': 'stemmer', 'language': 'possessive_english'},
      'russian_stop': {'type': 'stop', 'stopwords': '_russian_'},
      'russian_stemmer': {'type': 'stemmer', 'language': 'russian'}
    },
    'analyzer': {
      'ru_en': {
        'tokenizer': 'standard',
        'filter': [
          'lowercase',
          'english_stop','english_stemmer', 'english_possessive_stemmer',
          'russian_stop', 'russian_stemmer'
        ]
      }  
    }
  }
}

ES_PROPERTIES_CONFIG_text_ru_en = {
  'type': 'text',
  'analyzer': 'ru_en'
}

ES_PROPERTIES_CONFIG_raw_fields = {'fields': {'raw': {'type': 'keyword'}}}

ES_PROPERTIES_CONFIG_nested_person = {
  'type': 'nested',
  'dynamic': 'strict',
  'properties': {
    'id': {'type': 'keyword'},
    'name': ES_PROPERTIES_CONFIG_text_ru_en
  }
}

CINEMA_GENRE_INDEX_BODY = {
  'settings': ES_SETTINGS,
  'mappings': {
    'dynamic': 'strict',
    'properties': {
      'id': {'type': 'keyword'},
      'name': {'type': 'keyword'},
      'description': ES_PROPERTIES_CONFIG_text_ru_en
    }
  }
}

CINEMA_FILM_INDEX_BODY = {
  'settings': ES_SETTINGS,
  'mappings': {
    'dynamic': 'strict',
    'properties': {
      'id': {'type': 'keyword'},
      'imdb_rating': {'type': 'float'},
      'imdb_tconst': {'type': 'keyword'},
      'filmtype': {'type': 'keyword'},
      'genre': {'type': 'keyword'},
      'title': {**ES_PROPERTIES_CONFIG_text_ru_en, **ES_PROPERTIES_CONFIG_raw_fields},
      'description': ES_PROPERTIES_CONFIG_text_ru_en,
      'directors_names': ES_PROPERTIES_CONFIG_text_ru_en,
      'actors_names': ES_PROPERTIES_CONFIG_text_ru_en,
      'writers_names': ES_PROPERTIES_CONFIG_text_ru_en,
      'directors': ES_PROPERTIES_CONFIG_nested_person,
      'actors': ES_PROPERTIES_CONFIG_nested_person,
      'writers': ES_PROPERTIES_CONFIG_nested_person
    }
  }
}

ES_INDEXES = {
  'FILM_INDEX': {
    'name': config.elastic_film_index,
    'body_json': json.dumps(CINEMA_FILM_INDEX_BODY)
  },
  'GENRE_INDEX': {
    'name': config.elastic_genre_index,
    'body_json': json.dumps(CINEMA_GENRE_INDEX_BODY)
  }
}

CINEMA_INDEX_BODY = '''
{
  "settings": {
    "index": {
        "number_of_shards": 1,
        "number_of_replicas": 0
    },
    "refresh_interval": "1s",
    "analysis": {
      "filter": {
        "english_stop": {
          "type":       "stop",
          "stopwords":  "_english_"
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
          "type":       "stop",
          "stopwords":  "_russian_"
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
      "imdb_tconst": {
        "type": "keyword"
      },
      "filmtype": {
        "type": "keyword"
      },
      "genre": {
        "type": "keyword"
      },
      "title": {
        "type": "text",
        "analyzer": "ru_en",
        "fields": {
          "raw": {
            "type":  "keyword"
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
}
'''
