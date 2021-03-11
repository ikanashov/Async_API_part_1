import orjson

# Используем pydantic для упрощения работы при перегонке данных из json в объекты
from pydantic import BaseModel

def _orjson_dumps(val, *, default):
    return orjson.dumps(val, default=default).decode()

class Film(BaseModel):
    id: str
    title: str
    description: str

    class Config:
        # Заменяем стандартную работу с json на более быструю, 
        # Здесь возникает ошибка надо разобраться пока починил вот так https://github.com/samuelcolvin/pydantic/issues/1150
        #  File "pydantic/main.py", line 506, in pydantic.main.BaseModel.json
        # TypeError: Expected unicode, got bytes
        json_loads = orjson.loads
        json_dumps = _orjson_dumps