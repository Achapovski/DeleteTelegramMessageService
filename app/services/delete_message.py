import asyncio
from asyncio.tasks import Task
from dataclasses import dataclass

from app.clients import AiogramBotClient, RabbitMqClient
from app.clients.Redis import RedisClient
from app.schemes import Settings
from app.schemes.broker.messages import DeliveryDelMessage


@dataclass
class DeleteMessageService:
    settings: Settings
    broker: RabbitMqClient
    storage: RedisClient
    bot: AiogramBotClient

    __task: Task = None

    async def track_message(self):
        await self.broker.consume(self.remember_message)

    async def remember_message(self, msg: DeliveryDelMessage):
        await self.storage.pipeline()
        msgs: DeliveryDelMessage = await self.storage.get_value(key=str(msg.chat_id))

        valid_msgs = (await self.storage.set_value(key=str(msg.chat_id), value=msg.message_ids)) if not msgs else msgs

        data = DeliveryDelMessage(chat_id=str(msg.chat_id), message_ids=valid_msgs)
        data.message_ids += msg.message_ids if msgs else []
        await self.storage.set_value(key=str(msg.chat_id), value=data.message_ids)

        if not self.__task or self.__task.done():
            self.__task = asyncio.create_task(self.delete_msg(num=8))
        await self.storage.pipeline_execute()

    async def delete_msg(self, num):
        await asyncio.sleep(5)
        result = await self.storage.get_all_values()
        for id_, msgs in result.items():
            deleted_msgs = msgs[:-num]
            if deleted_msgs:
                await self.bot.delete_messages(data=DeliveryDelMessage(chat_id=id_, message_ids=deleted_msgs))
                values = await self.storage.get_value(key=id_)
                await self.storage.set_value(key=id_, value=values[len(deleted_msgs):])
