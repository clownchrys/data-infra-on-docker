import os
import asyncio
import importlib
import logging
from datetime import timedelta
from typing import *

from airflow.utils.context import Context
from airflow.utils.decorators import apply_defaults
from airflow.models.baseoperator import BaseOperator
from airflow.triggers.base import BaseTrigger, TriggerEvent

# extensions
from decorators import override


logger = logging.getLogger(__file__)


class TestAsyncOperator(BaseOperator):

    @override
    @apply_defaults
    def __init__(self, *args, **kwargs):
        super(TestAsyncOperator, self).__init__(*args, **kwargs)


    @override
    def execute(self, context: Context) -> Any:
        logger.info("execute")

        trigger = TestAsyncOperatorTrigger(
            key=f"{context['dag'].dag_id}.{context['ti'].task_id} {context['run_id']}",
            status_check_interval=1
        )

        self.defer(
            trigger=trigger,
            method_name="execute_complete",
            kwargs={},
            # timeout=timedelta(seconds=600),
        )

        return "execute"  # xcom


    # def execute_complete(self, context: Context, event: str) -> Any:
    def execute_complete(self, **kwargs) -> NoReturn:
        """
        :param kwargs:
        . user-defined kwargs
        . context: airflow.utils.context.Context
        . (conditional) event: str (if no kwargs has been assigned)
        :return:
        """
        logger.info("execute complete")
        logger.info(f"{kwargs!r}")



class TestAsyncOperatorTrigger(BaseTrigger):

    @override
    def __init__(self, key: str, status_check_interval: int, **kwargs):
        super().__init__(**kwargs)

        self.key = key
        self.status_check_interval = status_check_interval


    @override
    def serialize(self) -> Tuple[AnyStr, Dict]:
        classpath: str = f"{self.__class__.__module__}.{self.__class__.__qualname__}"
        kwargs: dict = {
            "key": self.key,
            "status_check_interval": self.status_check_interval,
        }
        logger.info(f"trigger serializing... (classpath={classpath!r}, kwargs={kwargs})")
        return classpath, kwargs


    @override
    async def run(self) -> AsyncGenerator[TriggerEvent, None]:
        logger.info("run")

        await asyncio.sleep(5)
        # await asyncio.sleep(60)

        # i = 0
        # while i < 10:
        #     await asyncio.sleep(self.status_check_interval)
        #     i += 1

        yield TriggerEvent(self.key)


    @override
    def cleanup(self) -> NoReturn:
        logger.info("cleanup")
        super().cleanup()
