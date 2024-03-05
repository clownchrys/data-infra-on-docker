from bentoml.io import JSON
import bentoml
import torch

# load plain model (more memory used)
# model = torch.jit.load("/tmp/model-artifacts/traced_model.pt")

# load bento wrapped runner (less memory used)
model = bentoml.models.get("testmodel")
runner = model.to_runner()

@bentoml.service(
    workers=6, # bento serve --api-workers 옵션 먹히지 않음
    resource={
        # https://docs.bentoml.org/en/latest/guides/configurations.html#configuration-fields
        "cpu": "200m",
        "memory": "512Mi",
        "gpu": "0",
        # "gpu_type": "nvidia-tesla-a100",
    },
    traffic={
        "timeout": 10,
    }
)
class Service:
    def __init__(self):
        self.request_id = 0

    # 동기식 로직의 경우 BentoML은 실행을 처리하기 위해 최적 크기의 작업자 풀을 생성합니다.
    # 동기 API는 간단하며 대부분의 모델 제공 시나리오에 적합합니다.
    @bentoml.api
    def infer_sync(self) -> dict:
        print(model)
        return {}

    # 성능과 처리량을 최대화하려는 시나리오의 경우 동기 API로는 충분하지 않을 수 있습니다.
    # 비동기 API는 처리 로직이 IO 바인딩이고 비동기 모델 실행이 지원되는 경우에 이상적입니다.
    @bentoml.api(
        name="api_2",
        route="/infer_async",
        # batchable=False,
        # batch_dim=0,
        # max_batch_size=100,
        # max_latency_ms=60000,
    )
    async def infer_async(self):
        raise NotImplementedError
