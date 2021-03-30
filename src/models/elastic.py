from typing import List

from pydantic import Field

from core.orjson import BaseModelOrjson


class ESQuerySearchParameters(BaseModelOrjson):
    query: str = Field('')
    search_fields: List[str] =  Field(['title', 'description'], alias='fields')
    type: str = 'best_fields'


class ESQuerySearchType(BaseModelOrjson):
    multi_match: ESQuerySearchParameters = Field(ESQuerySearchParameters())


class ESQuery(BaseModelOrjson):
    query: ESQuerySearchType = Field(ESQuerySearchType())
