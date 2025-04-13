import asyncio
from dataclasses import dataclass

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError

from app.schemes.broker.messages import DeliveryDelMessage


@dataclass
class AiogramBotClient:
    bot: Bot

    async def delete_messages(self, data: DeliveryDelMessage) -> bool:
        try:
            await self.bot.delete_messages(chat_id=data.chat_id, message_ids=data.message_ids)
        except TelegramAPIError as err:
            # FIXME: Логирование ошибок
            print(__name__, f"Error: {err.message}")
        else:
            return True
        finally:
            await self.bot.session.close()
        return False
