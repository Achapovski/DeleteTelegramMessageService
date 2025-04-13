import json
from dataclasses import dataclass
from typing import Union, Any

import redis.asyncio as redis
from redis.asyncio.client import Pipeline

from app.schemes import Settings
from app.utils.predicates import is_json

RedisValueType = Union[str, int, dict, list, tuple]


@dataclass
class RedisClient:
    settings: Settings
    DB_NUMBER: int = None
    DECODE_RESPONSE: bool = True
    _pipeline: Pipeline | None = None

    def __post_init__(self):
        self.host: str = self.settings.redis.HOST
        self.port: int = self.settings.redis.PORT
        self.db: int = self.settings.redis.DB_DEFAULT_NUMBER if not self.DB_NUMBER else self.DB_NUMBER
        self._decode_response: bool = self.DECODE_RESPONSE

    @property
    def redis(self) -> redis.client.Redis:
        return redis.Redis(host=self.host, port=self.port, db=self.db, decode_responses=self._decode_response)

    async def set_value(self, key: str, value: RedisValueType) -> RedisValueType:
        data = json.dumps(value)
        await self.pipeline()
        await self.redis.set(name=key, value=data)
        data = await self.get_value(key=key)
        await self.pipeline_execute()
        return data

    async def get_value(self, key: str) -> Any:
        data = await self.redis.get(key)
        if is_json(data):
            return json.loads(s=data)
        return data

    async def get_all_values(self):
        data = {}
        for key in await self.get_keys():
            data[key] = await self.get_value(key=key)
        return data

    async def get_keys(self):
        return await self.redis.keys()

    async def del_value(self, key: str):
        return self.redis.delete(key)

    async def del_all_values(self):
        if not await self.get_all_values():
            # FIXME: Логгировать отсутствие значений
            print(__name__, "No values to delete")
            return
        return await self.redis.delete(*await self.get_all_values())

    async def pipeline(self):
        self._pipeline = await self.redis.pipeline()
        return self._pipeline

    async def pipeline_execute(self):
        return await self._pipeline.execute()
