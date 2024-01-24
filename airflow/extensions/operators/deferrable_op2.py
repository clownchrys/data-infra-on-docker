import os
import asyncio
import importlib
import logging
from datetime import timedelta
from functools import wraps, partial
from typing import *

from airflow.utils.context import Context
from airflow.utils.decorators import apply_defaults
from airflow.models.baseoperator import BaseOperator
from airflow.triggers.base import BaseTrigger, TriggerEvent

# extensions
from decorators import override


logger = logging.getLogger(__file__)


class TestObject:
    pass


class TestAsyncOperator(BaseOperator):

    @override
    @apply_defaults
    def __init__(self, **kwargs):
        super(TestAsyncOperator, self).__init__(**kwargs)


    @override
    def execute(self, context: Context, current_trial: int = 0 , **kwargs) -> NoReturn:
        logger.info("execute")

        current_trial += 1
        logger.info(f"trial: {current_trial}")

        # anything = lambda x: x
        anything = TestObject()

        trigger = Trigger(
            key=f"{context['dag'].dag_id}.{context['ti'].task_id} {context['run_id']}",
            obj=anything,
            status_check_interval=1
        )

        self.defer(
            trigger=trigger,
            method_name="execute_complete",
            kwargs={"obj": anything, "current_trial": current_trial},
            timeout=timedelta(seconds=600)
        )


    def execute_complete(self, obj: object, current_trial: int, context: Context, **kwargs) -> Any:
        logger.info("execute complete")
        logger.info(f"trial: {current_trial}")

        self.execute(context, current_trial=current_trial)


class Trigger(BaseTrigger):

    @override
    def __init__(self, key: str, obj: object, status_check_interval: int, **kwargs):
        super().__init__(**kwargs)

        self.key = key
        self.obj = obj
        self.status_check_interval = status_check_interval

        logger.info("init")
        logger.info(f"obj type: {type(self.obj)}")
        logger.info(f"obj print: {self.obj!r}")


    @override
    def serialize(self) -> Tuple[AnyStr, Dict]:
        classpath: str = f"{self.__class__.__module__}.{self.__class__.__qualname__}"
        kwargs: dict = {
            "key": self.key,
            "obj": self.obj,
            "status_check_interval": self.status_check_interval,
        }
        logger.info(f"trigger serializing... (classpath={classpath!r}, kwargs={kwargs})")
        logger.info(f"obj type: {type(self.obj)}")
        logger.info(f"obj print: {self.obj!r}")

        return classpath, kwargs


    @override
    async def run(self) -> AsyncGenerator[TriggerEvent, None]:
        logger.info("run")
        logger.info(f"obj type: {type(self.obj)}")
        logger.info(f"obj print: {self.obj!r}")

        i = 0
        while i < 10:
            await asyncio.sleep(self.status_check_interval)
            i += 1

        yield TriggerEvent(self.key)


    @override
    def cleanup(self) -> NoReturn:
        logger.info("cleanup")
        super().cleanup()
