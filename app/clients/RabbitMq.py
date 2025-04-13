import asyncio
from dataclasses import dataclass
from typing import Callable, Any, Awaitable, Coroutine

import aiormq
from aiormq.abc import DeliveredMessage

from app.schemes import Settings
from app.schemes.broker.messages import DeliveryDelMessage


CallbackMessageType = Callable[[DeliveryDelMessage], Awaitable[Any]]


@dataclass
class RabbitMqClient:
    settings: Settings

    @staticmethod
    async def on_message(func: CallbackMessageType) -> Callable[[DeliveredMessage], Coroutine]:
        async def wrapper(msg: DeliveredMessage):
            await func(DeliveryDelMessage.model_validate_json(json_data=msg.body))
            await msg.channel.basic_ack(delivery_tag=msg.delivery.delivery_tag)
            return None

        return wrapper

    async def get_broker_connection(self) -> aiormq.abc.AbstractConnection:
        return await aiormq.connect(url=str(self.settings.rabbitmq.AMQP_DSN))

    async def get_broker_chanel(self) -> aiormq.abc.AbstractChannel:
        connection = await self.get_broker_connection()
        return await connection.channel()

    async def declare_exchanger(self) -> aiormq.abc.Exchange.DeclareOk:
        channel = await self.get_broker_chanel()
        exchange = channel.exchange_declare(
            exchange=self.settings.rabbitmq.EXCHANGES.message_deleter.name,
            exchange_type=self.settings.rabbitmq.EXCHANGES.message_deleter.type
        )
        return await exchange

    async def declare_queue(self) -> aiormq.abc.Queue.DeclareOk:
        channel = await self.get_broker_chanel()
        return await channel.queue_declare(
            queue=self.settings.rabbitmq.QUEUES.message_deleter.name
        )

    async def bind_queue(self) -> aiormq.abc.Queue.BindOk:
        channel = await self.get_broker_chanel()
        return await channel.queue_bind(
            queue=(await self.declare_queue()).queue,
            exchange=self.settings.rabbitmq.EXCHANGES.message_deleter.name
        )

    async def consume(self, callback_func: Callable[[DeliveryDelMessage], Any]) -> None:
        queue = await self.declare_queue()
        channel = await self.get_broker_chanel()
        await self.declare_exchanger()
        await self.bind_queue()

        await channel.basic_consume(
            queue=queue.queue,
            consumer_callback=await self.on_message(callback_func)
        )

    async def polling_consume(self, callback_func: Callable[[DeliveryDelMessage], Any]) -> None:
        await self.consume(callback_func=callback_func)
        await asyncio.Future()
