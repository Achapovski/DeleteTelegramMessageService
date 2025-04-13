from typing import Union

from pydantic import BaseModel

class DeliveryDelMessage(BaseModel):
    chat_id: int | str
    message_ids: Union[list[int], tuple[int]]
