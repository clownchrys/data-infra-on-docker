import os
import time
import pathlib
import importlib

import pendulum
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
from airflow.utils.dates import timedelta
from airflow.utils.weight_rule import WeightRule

from airflow import DAG
from airflow.operators.dummy import DummyOperator
from airflow.utils.dates import timedelta
from airflow.utils.weight_rule import WeightRule
from airflow.utils.context import Context
from airflow.utils.decorators import apply_defaults
from airflow.utils.db import provide_session, create_session
from airflow.utils.edgemodifier import Label
from airflow.utils.trigger_rule import TriggerRule
from airflow.utils.xcom import XCOM_RETURN_KEY
from airflow.models import BaseOperator

from airflow.triggers.temporal import TimeDeltaTrigger
from triggers.wait_trigger import WaitTrigger
from triggers.wait_trigger_no_key import WaitTriggerNoKey



default_args = {
    # base
    "owner": "admin",

    # email
    "email": ["admin@example.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    # "sla": timedelta(seconds=1),  # Service Level Agreement -> 작업에 소요되는 최대 시간에 대한 예상 (default: None)

    # task
    # "execution_timeout": timedelta(seconds=3),  # 태스크의 실행 타임아웃 시간  # (default: None)
    # "trigger_rule": "all_success",  # 하위 태스크의 트리거 규칙 (default: all_success -> 모든 상위 태스크가 성공한 경우)
    "depends_on_past": False,  # 태스크의 이전 인스턴스가 성공한 경우에만 트리거함  # (default: False)
    "retries": 3,  # 태스크가 실패하는 경우 추가로 다시 시작할 횟수 (No default)
    "retry_delay": timedelta(seconds=10),  # 재시작 대기시간 (default: 5 min)
    "retry_exponential_backoff": False,  # retry_delay 를 exponentially 하게 적용할지 (default: False)

    # callback
    # "on_success_callback": callback,
    # "on_failure_callback": callback,
    # "on_retry_callback": some_function,
    # "sla_miss_callback": some_function,

    # etc
    "provide_context": True,  # jinja 템플릿 변수 및 templates_dict 인수 전달 여부 (No default)
    "priority_weight": 1,  # Executor queue 에 등록될 우선 순위를 결정 (default: 1)
    "weight_rule": WeightRule.ABSOLUTE,  # weight 의 계산방법을 결정 (default: downstream)
    # "queue": "bash_queue",  # 태스크가 등록될 queue 의 이름을 지정 (default: default)
    # "pool": "backfill",  # 태스크가 등록될 pool 의 이름을 지정 (default: default_pool)
    "do_xcom_push": True,  # return 값을 xcom 으로 푸시함 (default: True)
}


dag = DAG(
    dag_id="raise_trigger_timeout",
    description="deferred operator error test",
    start_date=pendulum.yesterday(pendulum.timezone("Asia/Seoul")),  # DAG 의 시작 run id (started = run id + 1 interval)
    # end_date=pendulum.tomorrow(),  # DAG 의 마지막 run id
    concurrency=16,  # 동시 실행가능한 Task 인스턴스의 수 (default: 16)
    max_active_runs=1,  # 동시 실행가능한 DAG 인스턴스(DAG-Run)의 수 (default: 16)
    catchup=False,  # backfill 활성화 여부 (default: True -> 활성화)
    schedule_interval=None,  # DAG 실행 주기 (default: None)
    # schedule_interval="* * * * *",  # DAG 실행 주기 (default: None)
    # dagrun_timeout=timedelta(seconds=3),  # DAG 실행 타임아웃 시간 (default: None)
    default_args=default_args,  # 각 Task 에 적용할 기본 설정
    tags=pathlib.Path(__file__).parent.relative_to(os.environ["AIRFLOW_HOME"]).__str__().split("/")[1:],
)


class TestOperator(BaseOperator):

    @apply_defaults
    def __init__(self, wait: int, trigger_timeout: int, **kwargs):
        super(TestOperator, self).__init__(**kwargs)
        self.wait = wait
        self.trigger_timeout = trigger_timeout

    def execute(self, context: Context):
        unique_id = f"{context['dag'].dag_id}.{context['ti'].task_id} {context['run_id']}",
        self.log.info(f"execute on {unique_id!r}...")

        # trigger = TimeDeltaTrigger(delta=timedelta(seconds=self.wait))
        # trigger = WaitTriggerNoKey(seconds=self.wait)
        trigger = WaitTrigger(key="fixed_key", seconds=self.wait)

        trigger_timeout = None if (self.trigger_timeout is None) else timedelta(seconds=self.trigger_timeout)
        self.defer(trigger=trigger, method_name="execute_complete", kwargs={}, timeout=trigger_timeout)

    def execute_complete(self, **kwargs):
        pass


start = DummyOperator(task_id="start", dag=dag)
end = DummyOperator(task_id="end")
op1 = TestOperator(task_id="op1", wait=1, trigger_timeout=3)
op2 = TestOperator(task_id="op2", wait=2, trigger_timeout=3)
op3 = TestOperator(task_id="op3", wait=3, trigger_timeout=3)
op4 = TestOperator(task_id="op4", wait=4, trigger_timeout=3)
op5 = TestOperator(task_id="op5", wait=5, trigger_timeout=3)
op6 = TestOperator(task_id="op6", wait=6, trigger_timeout=3)
op7 = TestOperator(task_id="op7", wait=7, trigger_timeout=3)
op8 = TestOperator(task_id="op8", wait=8, trigger_timeout=3)
op9 = TestOperator(task_id="op9", wait=9, trigger_timeout=3)

start >> [op1, op2, op3, op4, op5] >> op6 >> op7 >> op8 >> op9 >> end
