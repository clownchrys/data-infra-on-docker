import os
import asyncio
import time
import logging
from datetime import timedelta
from typing import *

from airflow.utils.decorators import apply_defaults
from airflow.utils.context import Context
from airflow.models.baseoperator import BaseOperator
from airflow.triggers.base import BaseTrigger, TriggerEvent

import boto3
from botocore.config import Config as BotoConfig

import sagemaker
from sagemaker.estimator import Estimator
from sagemaker.pytorch import PyTorch
from sagemaker.tensorflow import TensorFlow

# extensions
from decorators import override
# from config import Config as cfg


logger = logging.getLogger(__file__)
sagemaker_client = boto3.client(
    "sagemaker",
    config=BotoConfig(connect_timeout=5, read_timeout=60, retries={"max_attempts": 20, "mode": "standard"})
)


# test dummy class
class cfg:
    @staticmethod
    def get_sagemaker_info():
        return {
            "role": "",
            "subnet": "",
            "security_group": ""
        }

    @staticmethod
    def s3_bucket(*args, **kwargs):
        return "s3_bucket"


class AsyncTrainingJobOperator(BaseOperator):
    template_fields: Sequence[str] = (
        "estimator_cls",
        "base_job_name",
        "source_dir",
        "entry_point",
        "instance_types",
        "instance_count",
        "dependencies",
        "environment",
        "tags",
        "image_uri",
        "trigger_timeout",
        "trigger_polling_interval",
        "retry_wait_interval",
        "retry_single_instance_tries",
    )

    ESTIMATOR_TYPE = {
        "estimator": {"class": Estimator},
        "pytorch": {"class": PyTorch, "framework_version": "1.10", "py_version": "py38"},
        "tensorflow": {"class": TensorFlow, "framework_version": "2.6.2", "py_version": "py38"},
    }

    REPOSITORY_ROOT = "/home/airflow/sagemaker/mlrepository"
    ARTIFACT_ROOT = f"{cfg.s3_bucket('workspace')}/sagemaker/artifact"
    SM_CONFIG = cfg.get_sagemaker_info()

    @override
    @apply_defaults
    def __init__(
        self,

        # estimator parameter
        estimator_cls: Union["estimator", "pytorch", "tensorflow"],  # use Literal instead of Union, in python3.8+
        base_job_name: str,
        source_dir: str,
        entry_point: str,
        instance_types: List[str],
        instance_count: int = 1,
        dependencies: List[str] = [],
        environment: Dict[str, str] = {},
        tags: List[Dict[Union["Key", "Value"], str]] = [],  # use Literal instead of Union, in python3.8+
        image_uri: str = "",

        # trigger parameter
        trigger_timeout: int = 86400,
        trigger_polling_interval: int = 600,

        # retry parameter
        retry_wait_interval: int = 180,
        retry_single_instance_tries: int = 3,

        # airflow parameter
        **kwargs
    ):
        super().__init__(**kwargs)

        # validate parameters
        assert estimator_cls.lower() in self.ESTIMATOR_TYPE.keys()
        assert trigger_timeout > 0
        assert trigger_polling_interval > 0
        assert retry_wait_interval > 0
        assert retry_single_instance_tries > 0

        # estimator parameters
        self.estimator_cls = estimator_cls
        self.base_job_name = base_job_name
        self.source_dir = source_dir
        self.entry_point = entry_point
        self.instance_types = instance_types
        self.instance_count = instance_count
        self.dependencies = dependencies
        self.environment = environment
        self.tags = tags
        self.image_uri = image_uri

        # trigger parameters
        self.trigger_timeout = trigger_timeout
        self.trigger_polling_interval = trigger_polling_interval

        # retry parameters
        self.retry_wait_interval = retry_wait_interval
        self.retry_single_instance_tries = retry_single_instance_tries

        # other parameters
        self.retry_max_tries = retry_single_instance_tries * len(instance_types)


    @override
    def execute(self, context: Context, current_tries: int = 0, **kwargs) -> NoReturn:
        estimator = self.build_estimator(current_tries)
        estimator.fit(wait=False)

        job_name = estimator._current_job_name

        trigger = TrainingJobTrigger(
            key=f"{context['dag'].dag_id}.{context['ti'].task_id} {context['run_id']}",
            job_name=job_name,
            status_check_interval=self.trigger_polling_interval,
        )
        self.defer(
            trigger=trigger,
            method_name="execute_complete",
            kwargs={"job_name": job_name, "current_tries": current_tries + 1},
            timeout=timedelta(seconds=self.trigger_timeout)
        )

        return job_name


    def execute_complete(self, job_name: str, current_tries: int, context: Context, **kwargs) -> Any:
        description = sagemaker_client.describe_training_job(TrainingJobName=job_name)
        job_status = description["TrainingJobStatus"] # Enum: Completed, Failed, Stopping, Stopped, (InProgress)
        failure_reason = description.get("FailureReason", job_status)

        """
        status 따라서 success or fail 처리
        """

        is_retry = (
            job_status == "Failed"
            and failure_reason.startswith("CapacityError")
        )

        if job_status == "Completed":
            return

        elif is_retry and (current_tries < self.retry_max_tries):
            time.sleep(self.retry_wait_interval)
            self.execute(context, current_tries=current_tries)

        elif is_retry:
            raise Exception(f"Retry({current_tries}) Exceeded: {failure_reason}")

        else:
            raise Exception(f"Training Job Failed: {failure_reason}")


    def build_estimator(self, current_tries: int):
        kwargs = {
            "base_job_name": self.base_job_name,
            "source_dir": os.path.join(self.REPOSITORY_ROOT, self.source_dir),
            "entry_point": self.entry_point,
            "instance_type": self.instance_types[current_tries // self.retry_single_instance_tries],
            "instance_count": self.instance_count,
            "dependencies": [os.path.join(self.REPOSITORY_ROOT, dep_dir) for dep_dir in self.dependencies],
            "environment": self.environment,
            "tags": self.tags,
            "role": self.SM_CONFIG["role"],
            "subnets": [self.SM_CONFIG["subnet"]],
            "security_group_ids": [self.SM_CONFIG["security_group"]],
            "output_path": self.ARTIFACT_ROOT,
            "code_location": self.ARTIFACT_ROOT,
            "sagemaker_session": sagemaker.Session(sagemaker_client=sagemaker_client),
        }
        estimator_info = self.ESTIMATOR_TYPE[self.estimator_cls.lower()]

        if self.estimator_cls.lower() == "estimator":
            kwargs["image_uri"] = self.image_uri
        else:
            kwargs["framework_version"] = estimator_info["framework_version"]
            kwargs["py_version"] = estimator_info["py_version"]

        return estimator_info["class"](**kwargs)


class TrainingJobTrigger(BaseTrigger):

    STATUS_JOB_DONE = (
        "Completed",
        "Failed",
        "Stopping",
        "Stopped",
    )

    @override
    def __init__(self, key: str, job_name: str, status_check_interval: int, **kwargs):
        super().__init__(**kwargs)

        self.key = key
        self.job_name = job_name
        self.status_check_interval = status_check_interval


    @override
    def serialize(self) -> Tuple[str, dict]:
        classpath: str = f"{self.__class__.__module__}.{self.__class__.__qualname__}" # "extensions.operators.training_job.TrainingJobTrigger"
        kwargs: dict = {
            "key": self.key,
            "job_name": self.job_name,
            "status_check_interval": self.status_check_interval,
        }
        logger.info(f"trigger serializing... (classpath={classpath!r}, kwargs={kwargs})")
        return classpath, kwargs


    @override
    async def run(self) -> AsyncGenerator[TriggerEvent, None]:
        while (
            sagemaker_client.describe_training_job(TrainingJobName=self.job_name)["TrainingJobStatus"]
            not in self.STATUS_JOB_DONE
        ):
            await asyncio.sleep(self.status_check_interval)

        yield TriggerEvent(self.key)


if __name__ == "__main__":
    # this ain't working, just usage sample
    task_training_job = AsyncTrainingJobOperator(
        task_id="training_job",
        estimator_cls="tensorflow",
        base_job_name="deferrable-operator-test",
        source_dir="dummy",
        entry_point="entrypoint.py",
        instance_types=["ml.g4dn.8xlarge", "ml.p2.8xlarge", "ml.p3.8xlarge"],
        instance_count=1,
        dependencies=["common"],
        environment={"ENV": "staging"},
        tags=[{"Key": "dag", "Value": "test_dag"}],
        trigger_timeout=1800,
        trigger_polling_interval=60,
        retry_wait_interval=60,
        retry_single_instance_tries=3,
    )
