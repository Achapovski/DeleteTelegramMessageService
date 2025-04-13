from typing import Literal

from pydantic import BaseModel, Field, SecretStr, AmqpDsn


class Bot(BaseModel):
    TOKEN: str


class Redis(BaseModel):
    HOST: str
    PORT: int = Field(ge=1000, le=16394)
    DB_DEFAULT_NUMBER: int = Field(ge=0, le=15)


class RabbitMQ(BaseModel):
    HOST: str
    PORT: int = Field(ge=1000, le=16394)
    LOGIN: str
    PASSWORD: SecretStr
    AMQP_DSN: AmqpDsn
    EXCHANGES: "RabbitExchanges"
    QUEUES: "RabbitQueues"


class Settings(BaseModel):
    bot: Bot
    redis: Redis
    rabbitmq: RabbitMQ


class BasicQueue(BaseModel):
    name: str


class BasicExchange(BaseModel):
    name: str
    type: Literal["direct", "topic", "fanout"]


class RabbitExchanges(BaseModel):
    message_deleter: BasicExchange


class RabbitQueues(BaseModel):
    message_deleter: BasicQueue
