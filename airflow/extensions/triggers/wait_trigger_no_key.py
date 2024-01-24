import asyncio
from typing import *

from airflow.triggers.base import BaseTrigger, TriggerEvent


class WaitTriggerNoKey(BaseTrigger):
    def __init__(self, seconds: int, **kwargs):
        super().__init__(**kwargs)

        self.seconds = seconds

    def serialize(self) -> Tuple[AnyStr, Dict]:
        classpath = f"{self.__class__.__module__}.{self.__class__.__qualname__}"
        kwargs = {
            "seconds": self.seconds,
        }
        print(f"trigger serializing... (classpath={classpath!r}, kwargs={kwargs})")
        return classpath, kwargs

    async def run(self) -> AsyncGenerator[TriggerEvent, None]:
        await asyncio.sleep(self.seconds)
        yield TriggerEvent(self.seconds)

    def cleanup(self) -> NoReturn:
        super().cleanup()
