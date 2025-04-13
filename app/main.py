import asyncio

from aiogram import Bot

from app.clients.Redis import RedisClient
from app.settings.settings import settings
from app.clients import RabbitMqClient, AiogramBotClient
from app.services.delete_message import DeleteMessageService


async def main():
    redis = RedisClient(settings=settings)
    bot = Bot(token=settings.bot.TOKEN)

    dms = DeleteMessageService(
        settings=settings,
        bot=AiogramBotClient(bot=bot),
        broker=RabbitMqClient(settings=settings),
        storage=redis
    )
    print("Delete message Service work")
    await redis.del_all_values()
    await dms.track_message()
    await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
