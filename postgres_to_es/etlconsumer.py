from typing import List

from loguru import logger

from esindex import CINEMA_INDEX_BODY as esbody
from esindex import ES_INDEXES
from etlclasses import ESGenres, ESMovie, ESPerson, ETLFilmWork, ETLProducerTable
from etldecorator import coroutine, some_sleep
from etlelastic import ETLElastic
from etlpostgres import ETLPG
from etlredis import ETLRedis
from etlsettings import ETLSettings, postgres_table


class ETLConsumer:

    def __init__(self):
        cnf = ETLSettings()

        self.producer_table: ETLProducerTable = postgres_table

        self.index_name = cnf.elastic_index
        self.limit = cnf.etl_size_limit

        self.redis = ETLRedis()
        self.pgbase = ETLPG()
        self.es = ETLElastic()

    def worker(self, getfilmsidfromredis, getdatafromtable) -> ETLProducerTable:
        while self.redis.get_status('consumer') == 'run':
            getfilmsidfromredis.send(None)
            for table in self.producer_table:
                if table.isESindex:
                    getdatafromtable.send(table)
        
        if self.redis.get_status('consumer') == 'stop':
            logger.info('consumer stopped by stop signal')

    @coroutine
    def get_data_from_table(self, datatoes) -> dict:
        while True:
            data: ETLProducerTable = (yield)
            datas = {}
            idlists = self.redis.get_tableid_for_work(self.limit, data.table)
            datas['table'] = data
            if (len(idlists) > 0) and (data.table == 'djfilmgenre'):
                logger.info(f'Get {data.table} id to load to ES')
                datas['data'] = self.pgbase.get_genrebyid(tuple(idlists))
                datatoes.send(datas)

    @coroutine
    def put_data_to_ES(self):
        while True:
            datas = (yield)
            logger.info(f'Start loading to ES index from {datas["table"].table}')
            if datas['table'].table == 'djfilmgenre':
                esdata = [ESGenres(row.id, row.name, row.description) for row in datas['data']]
                if self.es.bulk_update(ES_INDEXES['GENRE_INDEX']['name'], esdata):
                    self.redis.del_work_queuename('djfilmgenre')
                    logger.info(f'Data succesfully loaded from  {datas["table"].table}, delet working queue')
                else:
                    some_sleep(min_sleep_time=1, max_sleep_time=10)

    @coroutine
    def get_filmsid_from_redis(self, putfilmtoes) -> List[ETLFilmWork]:
        while True:
            data = (yield)
            logger.info('Get film id to load to ES')
            idlists = self.redis.get_filmid_for_work(self.limit)
            films = self.pgbase.get_filmsbyid(tuple(idlists)) if len(idlists) > 0 else []
            putfilmtoes.send(films)

    @coroutine
    def put_films_to_ES(self):
        while True:
            films: List[ETLFilmWork] = (yield)
            logger.info('Start loading film data to elastic')
            esfilms = [
                ESMovie(
                    film.id, film.rating, film.imdb_tconst, film.type_name, film.genres,
                    film.title, film.description,
                    [name.split(' : ')[1] for name in film.directors] if film.directors else None,
                    [name.split(' : ')[1] for name in film.actors] if film.actors else None,
                    [name.split(' : ')[1] for name in film.writers] if film.writers else None,
                    [ESPerson(*name.split(' : ')) for name in film.directors] if film.directors else None,
                    [ESPerson(*name.split(' : ')) for name in film.actors] if film.actors else None,
                    [ESPerson(*name.split(' : ')) for name in film.writers] if film.writers else None
                ) for film in films]
            if self.es.bulk_update(self.index_name, esfilms):
                self.redis.del_work_queuename()
                logger.info('Film data succesfully loaded, delete working queue')
            else:
                some_sleep(min_sleep_time=1, max_sleep_time=10)

    def start(self):
        if self.redis.get_status('consumer') == 'run':
            logger.warning('ETL Consumer already started, please stop it before run!')
            return
        else:
            self.redis.set_status('consumer', 'run')
            self.es.create_index(self.index_name, esbody)
            self.es.create_index(ES_INDEXES['GENRE_INDEX']['name'], ES_INDEXES['GENRE_INDEX']['body_json'])
        
        # level 2
        putfilmtoes = self.put_films_to_ES()
        datatoes = self.put_data_to_ES()
        # level 1
        getfilmsidfromredis = self.get_filmsid_from_redis(putfilmtoes)
        getdatafromtable = self.get_data_from_table(datatoes)
        # level 0
        self.worker(getfilmsidfromredis, getdatafromtable)

    def stop(self):
        self.redis.set_status('consumer', 'stop')
        logger.info('consumer will be stopped')


if __name__ == '__main__':
    ETLConsumer().stop()
    ETLConsumer().start()
