import os
import pathlib
import time

import pendulum
from airflow import DAG
from airflow.decorators import task
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
from airflow.utils.dates import timedelta
from airflow.utils.weight_rule import WeightRule
from airflow.utils.trigger_rule import TriggerRule
from airflow.utils.context import Context


def on_failure(context: Context):
    print("[SYSTEM] on failure...")


def on_success(context: Context):
    print("[SYSTEM] on success...")


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
    "on_success_callback": on_success,
    "on_failure_callback": on_failure,
    # "on_retry_callback": some_function,
    # "sla_miss_callback": some_function,

    # etc
    "provide_context": True,  # jinja 템플릿 변수 및 templates_dict 인수 전달 여부 (No default)
    "priority_weight": 1,  # Executor queue 에 등록될 우선 순위를 결정 (default: 1)
    "weight_rule": WeightRule.ABSOLUTE,  # weight 의 계산방법을 결정 (default: downstream)
    # "queue": "bash_queue",  # 태스크가 등록될 queue 의 이름을 지정 (default: default)
    # "pool": "backfill",  # 태스크가 등록될 pool 의 이름을 지정 (default: default_pool)
    "do_xcom_push": False,  # return 값을 xcom 으로 푸시함 (default: True)
}


dag = DAG(
    dag_id=os.path.basename(__file__),
    start_date=pendulum.yesterday(pendulum.timezone("Asia/Seoul")),  # DAG 의 시작 run id (started = run id + 1 interval)
    # end_date=pendulum.tomorrow(),  # DAG 의 마지막 run id
    concurrency=16,  # 동시 실행가능한 Task 인스턴스의 수 (default: 16)
    max_active_runs=1,  # 동시 실행가능한 DAG 인스턴스(DAG-Run)의 수 (default: 16)
    catchup=False,  # backfill 활성화 여부 (default: True -> 활성화)
    schedule_interval=None,  # DAG 실행 주기 (default: None)
    # dagrun_timeout=timedelta(seconds=3),  # DAG 실행 타임아웃 시간 (default: None)
    default_args=default_args,  # 각 Task 에 적용할 기본 설정
    tags=pathlib.Path(__file__).parent.relative_to(os.environ["AIRFLOW_HOME"]).__str__().split("/")[1:],
)

from airflow.models import BaseOperator
from airflow.utils.state import State

class EndOperator(BaseOperator):
    def __init__(self, **kwargs):
        kwargs["trigger_rule"] = TriggerRule.ALL_DONE

        super().__init__(**kwargs)

    def execute(self, context):
        dag_run = context["dag_run"]
        tis = dag_run.get_task_instances()
        filtered_tis = list(filter(lambda ti: ti.state == State.FAILED, tis))

        if len(filtered_tis) > 0:
            dag_run.state = State.FAILED
        else:
            dag_run.state = State.FAILED

        print("[SYSTEM] end operator...")


@task(retries=0)
def success(task_id): pass

@task(retries=0)
def success123(task_id): pass

@task(retries=0)
def failure(task_id):
    raise Exception

start = DummyOperator(task_id="start", dag=dag)
#end = DummyOperator(task_id="end")

start >> success(task_id="1st") >> failure(task_id="2nd") >> success123(task_id="1st") >> EndOperator(task_id="end", trigger_rule=TriggerRule.ALL_SUCCESS)
