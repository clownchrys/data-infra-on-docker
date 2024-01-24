import asyncio
from typing import *

from airflow.triggers.base import BaseTrigger, TriggerEvent


class DummyTrigger(BaseTrigger):
    def __init__(self, key: str, **kwargs):
        super().__init__(**kwargs)

        self.key = key

    def serialize(self) -> Tuple[AnyStr, Dict]:
        classpath = f"{self.__class__.__module__}.{self.__class__.__qualname__}"
        kwargs = {
            "key": self.key,
        }
        print(f"trigger serializing... (classpath={classpath!r}, kwargs={kwargs})")
        return classpath, kwargs

    async def run(self) -> AsyncGenerator[TriggerEvent, None]:
        await asyncio.sleep(1)
        yield TriggerEvent(self.key)

    def cleanup(self) -> NoReturn:
        super().cleanup()
