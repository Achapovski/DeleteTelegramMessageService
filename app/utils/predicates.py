import json


def is_json(data: str) -> bool:
    try:
        json.loads(data)
        return True
    except (json.decoder.JSONDecodeError, TypeError):
        return False
