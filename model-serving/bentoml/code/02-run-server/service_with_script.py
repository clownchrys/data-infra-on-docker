from pydantic import BaseModel
from bentoml.io import (
    File,
    IODescriptor,
    Image,
    JSON,
    Multipart,
    NumpyNdarray,
    PandasDataFrame,
    PandasSeries,
    SSE, # v1.2.1
    Text,
)
import bentoml
import torch

# model = torch.jit.load("/tmp/model-artifacts/traced_model.pt")

model = bentoml.models.get("testmodel")
runner = model.to_runner()

service = bentoml.Service(
    name="TestModelService",
    runners=[runner],
    models=[model],
)

class RequestModel(BaseModel):
    pass

class ResponseModel(BaseModel):
    pass

@service.api(
    input=JSON(),
    output=JSON(),
    # output=NumpyNdarray(
    #     shape=(-1, 3),
    #     dtype=np.float32,
    #     enforce_dtype=True,
    #     enforce_shape=True
    # ),
    name="api_1",
    doc="123123123",
    route="/infer_sync"
)
def infer_sync(
    input_data: RequestModel,
    context: bentoml.Context
) -> ResponseModel:

    # get request metadata
    req_headers = context.request.headers
    print(req_headers)

    # On processing...

    # set response metadata
    context.response.status_code = 200
    context.response.cookies = [
        bentoml.Cookie(
            key="key",
            value="value",
            max_age=None,
            expires=None,
            path="/infer",
            domain=None,
            secure=True,
            httponly=True,
            samesite="None"
        )
    ]
    context.response.headers.append("X-Custom-Header", "value")

    return ResponseModel()


def test(input_data):
    runner.init_local()

    # input_data = torch.Tensor(input_data).float()
    # out = runner.run(input_data)

    print(input_data)
    print(runner)


"""
>> dir(service)
['__annotations__', '__attrs_attrs__', '__attrs_init__',
'__attrs_own_setattr__', '__class__', '__delattr__', '__dir__',
'__doc__', '__eq__', '__format__', '__ge__', '__getattribute__',
'__getstate__', '__gt__', '__hash__', '__init__',
'__init_subclass__', '__le__', '__lt__', '__module__',
'__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__',
'__setattr__', '__setstate__', '__sizeof__', '__slots__',
'__str__', '__subclasshook__', '__weakref__', '_caller_module',
'_import_str', '_working_dir', 'add_asgi_middleware',
'add_grpc_handlers', 'add_grpc_interceptor', 'api', 'apis',
'asgi_app', 'bento', 'context', 'deployment_hooks', 'doc',
'get_grpc_servicer', 'get_service_import_origin',
'grpc_handlers', 'grpc_servicer', 'interceptors',
'is_service_importable', 'middlewares', 'models',
'mount_apps', 'mount_asgi_app', 'mount_grpc_servicer',
'mount_servicers', 'mount_wsgi_app', 'name',
'on_asgi_app_shutdown', 'on_asgi_app_startup', 'on_deployment',
'on_grpc_server_shutdown', 'on_grpc_server_startup',
'on_shutdown', 'on_startup', 'openapi_spec',
'runners', 'shutdown_hooks', 'startup_hooks', 'tag']

>>> dir(runner)
['__abstractmethods__', '__annotations__', '__attrs_attrs__',
'__attrs_init__', '__call__', '__class__', '__delattr__',
'__dict__', '__dir__', '__doc__', '__eq__', '__format__',
'__ge__', '__getattribute__', '__gt__', '__hash__',
'__init__', '__init_subclass__', '__le__', '__lt__',
'__module__', '__ne__', '__new__', '__reduce__',
'__reduce_ex__', '__repr__', '__setattr__', '__sizeof__',
'__slots__', '__str__', '__subclasshook__', '__weakref__',
'_abc_impl', '_runner_handle', '_set_handle', 'async_run',
'destroy', 'embedded', 'init_client', 'init_local', 'models',
'name', 'resource_config', 'run', 'runnable_class',
'runnable_init_params', 'runner_handle_is_ready',
'runner_methods', 'scheduled_worker_count',
'scheduled_worker_env_map', 'scheduling_strategy',
'workers_per_resource']

>> dir(model)
['_Model__fs', '__abstractmethods__', '__annotations__',
'__attrs_attrs__', '__attrs_init__', '__attrs_own_setattr__',
'__class__', '__delattr__', '__dict__', '__dir__', '__doc__',
'__eq__', '__format__', '__ge__', '__getattribute__',
'__getstate__', '__gt__', '__hash__', '__init__',
'__init_subclass__', '__le__', '__lt__', '__module__',
'__ne__', '__new__', '__reduce__', '__reduce_ex__',
'__repr__', '__setattr__', '__setstate__', '__sizeof__',
'__slots__', '__str__', '__subclasshook__', '__weakref__',
'_abc_impl', '_compress', '_custom_objects', '_export_ext',
'_export_name', '_from_compressed', '_fs', '_info', '_model',
'_runnable', '_tag', '_write_custom_objects', '_write_info',
'create', 'creation_time', 'custom_objects',
'enter_cloudpickle_context', 'exit_cloudpickle_context',
'export', 'file_size', 'flush', 'from_fs', 'get_typename',
'guess_format', 'import_from', 'info', 'load_model', 'path',
'path_of', 'save', 'tag', 'to_runnable', 'to_runner',
'validate', 'with_options']
"""

if __name__ == "__main__":
    test({})