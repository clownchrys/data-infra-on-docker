import os
import inspect
import pathlib
from typing import *

import pendulum

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

from triggers.wait_trigger import WaitTrigger


def agg_callbacks(*callback_fn):
    def wrapper(context: Context):
        for f in callback_fn:
            if f is not None:
                f(context)
    return wrapper


def get_callback(key: str, kwargs: dict):
    valid_keys = [
        "on_success_callback",
        "on_failure_callback",
        "on_retry_callback",
        "on_execute_callback",
        "sla_miss_callback",
    ]
    assert key in valid_keys, f"Invalid key: {key!r}"
    return kwargs.get(key) or kwargs.get("default_args", {}).get(key)


class MyOperator(BaseOperator):
    def execute(self, context):
        try:
            # 실행 로직
            raise Exception("expected error")
            self.log.info("MyOperator is executed successfully.")
        except Exception as e:
            # 예외 처리 로직
            self.log.error("MyOperator is failed to execute.")
            raise e
        finally:
            self.teardown(context)

    def teardown(self, context):
        # 성공/실패 여부와 상관 없이 실행되는 코드
        self.log.info("MyOperator is teardowned.")


class TestOperator(BaseOperator):

    XCOM_JOB_NAME = "XCOM_JOB_NAME"
    XCOM_DEFERRED_START_DATE = "XCOM_DEFERRED_START_DATE"
    XCOM_DEFERRED_END_DATE = "XCOM_DEFERRED_END_DATE"

    @apply_defaults
    def __init__(self, is_exception: bool = False, is_deferred: bool = False, **kwargs):
        # kwargs["max_active_tis_per_dag"] = 1

        # self.callback injection
        kwargs["on_success_callback"] = agg_callbacks(self.operator_callback, get_callback("on_success_callback", kwargs))
        kwargs["on_failure_callback"] = agg_callbacks(self.operator_callback, get_callback("on_failure_callback", kwargs))
        kwargs["on_retry_callback"] = agg_callbacks(self.operator_callback, get_callback("on_retry_callback", kwargs))

        super().__init__(**kwargs)

        self.is_exception = is_exception
        self.is_deferred = is_deferred
        self.init_kwargs = kwargs

    def execute(self, context: Context):
        print("execute...")

        job_name = "test_job"
        start_date = pendulum.now("UTC")

        ti = context['ti']

        ti.xcom_push(key=self.XCOM_JOB_NAME, value=job_name)
        ti.xcom_push(key=self.XCOM_DEFERRED_START_DATE, value=start_date.to_datetime_string())

        if self.is_exception:
            raise Exception(f"expected exc: self.value({self.value})")

        if self.is_deferred:
            trigger = WaitTrigger(
                key=f"{context['dag'].dag_id}.{context['ti'].task_id} {context['run_id']}",
                seconds=120,
            )
            self.defer(
                trigger=trigger,
                method_name="execute_complete",
                kwargs={
                    "job_name": job_name,
                    "start_date": start_date,
                },
                timeout=timedelta(seconds=600)
            )
            print("deferred started!!!!!!!!!!!")

        return "execute"

    def execute_complete(self, job_name, start_date, **kwargs):
        event = kwargs.get("event")
        context = kwargs.get("context")
        print(f"execute_complete: event={event!r}, context={context!r}")

        end_date = pendulum.now("UTC")

        ti = context['ti']

        ti.xcom_push(key=self.XCOM_JOB_NAME, value=job_name)
        ti.xcom_push(key=self.XCOM_DEFERRED_START_DATE, value=start_date.to_datetime_string())
        ti.xcom_push(key=self.XCOM_DEFERRED_END_DATE, value=end_date.to_datetime_string())

        return "execute_complete"

    def operator_callback(self, context: Context):
        print(f"{inspect.currentframe().f_code.co_name!r} running...")

        ti = context["ti"]

        job_name = ti.xcom_pull(key=self.XCOM_JOB_NAME, task_ids=ti.task_id)
        start_date = pendulum.parse(ti.xcom_pull(key=self.XCOM_DEFERRED_START_DATE, task_ids=ti.task_id))
        end_date = pendulum.parse(ti.xcom_pull(key=self.XCOM_DEFERRED_END_DATE, task_ids=ti.task_id))

        self.log.info(f"ti.task.params: {ti.task.params}")
        self.log.warn(f"xcom.job_name: {job_name}")
        self.log.error(f"xcom.start_date: {start_date}")
        print("xcom.end_date: ", end_date)
        duration = (end_date - start_date).total_seconds()
        print("ti.duration: ", ti.duration)

        ti.start_date = start_date; ti.end_date = end_date; ti.duration = duration

        # @provide_session
        # def save_to_db(ti_or_dag_run, session: Optional[Session] = None):
        #     if session is None:
        #         raise Exception(f"session not provided: {session}")
        #     session.add(ti_or_dag_run)
        #     session.commit()
        #     ti_or_dag_run.refresh_from_db()
        # save_to_db(ti)

        with create_session() as sess:
            sess.add(ti)
        ti.refresh_from_db()


def callback_from_dag(context: Context):
    print(f"callback_from_dag running... (current_state: {context['ti'].current_state()})")
    print("context: ", context)


"""
■ Environment-level 설정
airflow.cfg 의 설정값을 통해서 동시성 제어

parallelism : Worker에서 동시에 실행 가능한 타스크 인스턴수의 수 제어. “maximum active tasks anywhere.”
max_active_tasks_per_dag (dag_concurrency) : DAG 당 동시에 스케쥴링되는 Task의 수. 하나의 DAG이 slot을 독점하는 것을 방지.
max_active_runs_per_dag : DAG당 한 순간에 실행 가능한 DAG Run의 개수. Backfilling (catchup=True) 상황과 관련.

■ DAG-level 제어
concurrency : 모든 DAG Runs 에서의 최대 타스크 인스턴스의 수. DAG parameter에 지정. default는 max_active_tasks_per_dag 사용.
max_active_tasks 하나의 DAG Run에서의 최대 타스크 인스턴스 수. Default는 max_active_tasks_per_dag 사용.
max_active_runs DAG Runs의 수 제한. Default는 max_active_runs_per_dag. backfill 상황에서 고려.

■ Task-level 제어
pool : This setting defines the amount of pools available for a task. Pools are a way to limit the number of concurrent instances of an arbitrary group of tasks.
max_active_tis_per_dag(task_concurrency) : concurrency limit for the same task across multiple DAG runs
"""


default_args = {
    # base
    "owner": "admin",

    # email
    "email": ["admin@example.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    # "sla": timedelta(seconds=1),  # Service Level Agreement -> 작업에 소요되는 최대 시간에 대한 예상 (default: None)

    # task
    "execution_timeout": timedelta(seconds=600),  # 태스크의 실행 타임아웃 시간  # (default: None)
    "trigger_rule": TriggerRule.ALL_SUCCESS,  # 하위 태스크의 트리거 규칙 (default: all_success -> 모든 상위 태스크가 성공한 경우)
    "depends_on_past": False,  # 이전 ti가 실패한 경우, ti가 생성되지 않고 대기 (default: False)
    "wait_for_downstream": False,  # 이전 dag_run의 ti가 하나라도 실패하면, dag_run이 생성되지 않고 대기 (default: False)
    "retries": 1,  # 태스크가 실패하는 경우 추가로 다시 시작할 횟수 (No default)
    "retry_delay": timedelta(seconds=3),  # 재시작 대기시간 (default: 5 min)
    "retry_exponential_backoff": False,  # retry_delay 를 exponentially 하게 적용할지 (default: False)
    "max_active_tis_per_dag": 1,  # (task_concurrency) 모든 dag_run 에서 동일한 태스크에 대해 생성할 수 있는 최대 ti 개수 (default: None)

    # callback
    "on_success_callback": callback_from_dag,
    "on_failure_callback": callback_from_dag,
    "on_retry_callback": callback_from_dag,
    "sla_miss_callback": callback_from_dag,

    # etc
    "provide_context": True,  # jinja 템플릿 변수 및 templates_dict 인수 전달 여부 (No default)
    "priority_weight": 1,  # Executor queue 에 등록될 우선 순위를 결정 (default: 1)
    "weight_rule": WeightRule.ABSOLUTE,  # weight 의 계산방법을 결정 (default: downstream)
    # "queue": "bash_queue",  # 태스크가 등록될 queue 의 이름을 지정 (default: default)
    # "pool": "backfill",  # 태스크가 등록될 pool 의 이름을 지정 (default: default_pool)
    "do_xcom_push": False,  # return 값을 xcom 으로 푸시함 (default: True)
}

with DAG(
    dag_id=os.path.basename(__file__),
    description="callback running test",
    start_date=pendulum.yesterday(pendulum.timezone("Asia/Seoul")),  # DAG 의 시작 run id (started = run id + 1 interval)
    end_date=pendulum.tomorrow(),  # DAG 의 마지막 run id

    concurrency=16,  # 모든 dag_run 에서의 최대 ti 개수 (default: 16)
    max_active_tasks=16,  # 하나의 dag_run 에서의 최대 ti 개수
    max_active_runs=1,  # 동시 실행가능한 DAG 인스턴스(dag_run)의 수 (default: 16)

    catchup=False,  # backfill 활성화 여부 (default: True -> 활성화)
    schedule_interval=None,  # DAG 실행 주기 (default: None)
    dagrun_timeout=timedelta(seconds=600),  # DAG 실행 타임 아웃 시간 (default: None)
    default_args=default_args,  # 각 Task 에 적용할 기본 설정
    tags=pathlib.Path(__file__).parent.relative_to(os.environ["AIRFLOW_HOME"]).__str__().split("/")[1:],
) as dag:

    start = DummyOperator(task_id="start")
    end = DummyOperator(task_id="end", trigger_rule=TriggerRule.ONE_SUCCESS)

    op_success = TestOperator(task_id="success", is_exception=False)
    op_dummy = TestOperator(task_id="dummy", is_exception=True, trigger_rule=TriggerRule.DUMMY)
    op_failure = TestOperator(task_id="failure", is_exception=True)
    op_deferred = TestOperator(task_id="deferred", is_exception=False, is_deferred=True)
    op_teardown = MyOperator(task_id="teardown")

    start >> Label("on success") >> op_success
    start >> Label("on failure") >> op_failure
    start >> Label("`TriggerRule.DUMMY` not working") >> op_dummy
    start >> Label("on deferred") >> op_deferred
    start >> Label("teardown") >> op_teardown

    [op_success, op_failure, op_dummy, op_deferred, op_teardown] >> end
