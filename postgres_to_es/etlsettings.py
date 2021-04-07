from pydantic import BaseSettings

from etlclasses import ETLProducerTable


class ETLSettings(BaseSettings):
    postgres_db: str = 'postgres'
    postgres_host: str = 'localhost'
    postgres_port: int = 5432
    postgres_user: str = 'postgres'
    postgres_password: str = ''
    postgres_schema: str = 'public'
    redis_prefix: str = ''
    redis_host: str = 'localhost'
    redis_port: int = 6379
    redis_password: str = ''
    elastic_host: str = 'localhost'
    elastic_port: int = 9200
    elastic_scheme: str = 'http'
    elastic_user: str = 'elastic'
    elastic_password: str = ''
    elastic_index: str = 'movies'
    elastic_film_index: str = 'movies'
    elastic_genre_index: str = 'genres'
    elastic_person_index: str = 'persons'
    etl_size_limit: int = 10

    class Config:
        env_file = '../.env'


config = ETLSettings()

postgres_table = [
    ETLProducerTable(table='djfilmwork', isrelation=False),
    ETLProducerTable(
        table='djfilmperson', field='film_work_id', ptable='djfilmworkperson', pfield='person_id', isESindex=True
    ),
    ETLProducerTable(
        table='djfilmgenre', field='film_work_id', ptable='djfilmworkgenre', pfield='genre_id', isESindex=True
    ),
    ETLProducerTable(table='djfilmtype', field='id', ptable='djfilmwork', pfield='type_id'),
]
