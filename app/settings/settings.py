from functools import lru_cache

from yaml import load, CSafeLoader
from app.schemes import Settings


@lru_cache()
def get_settings(config_file_name: str = "config") -> Settings:
    with open(f"{config_file_name}.yml") as file:
        data = load(stream=file, Loader=CSafeLoader)
    return Settings.model_validate(data)


settings = get_settings()
