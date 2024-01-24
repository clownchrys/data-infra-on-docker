import asyncio
from typing import *

from airflow.triggers.base import BaseTrigger, TriggerEvent


class WaitTrigger(BaseTrigger):
    def __init__(self, key: str, seconds: int, **kwargs):
        super().__init__(**kwargs)

        self.key = key
        self.seconds = seconds

    def serialize(self) -> Tuple[AnyStr, Dict]:
        classpath = f"{self.__class__.__module__}.{self.__class__.__qualname__}"
        kwargs = {
            "key": self.key,
            "seconds": self.seconds,
        }
        print(f"trigger serializing... (classpath={classpath!r}, kwargs={kwargs})")
        return classpath, kwargs

    async def run(self) -> AsyncGenerator[TriggerEvent, None]:
        await asyncio.sleep(self.seconds)
        yield TriggerEvent(self.key)

    def cleanup(self) -> NoReturn:
        super().cleanup()
