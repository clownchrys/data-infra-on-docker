"""
ModelHandler defines a custom model handler.
"""

from typing import *
import torch
import os
import json
import importlib

from ts.torch_handler.base_handler import BaseHandler
from ts.context import Context
from ts.utils.util import list_classes_from_module


# https://github.com/pytorch/serve/blob/master/ts/context.py
""" Example of ts.context.Context
{
    'model_name': 'iris_model',
    'manifest': {
        'createdOn': '27/04/2023 06:50:01',
        'runtime': 'python',
        'model': {
            'modelName': 'iris_model',
            'serializedFile': 'model.pt',
            'handler': 'handler.py',
            'modelVersion': '1.0',
            'requirementsFile': 'requirements.txt'
        },
        'archiverVersion': '0.7.1'
    },
    '_system_properties': {
        'model_dir': '/tmp/models/08fb704d35fc4eafbd51703fcb9e2d50',
        'gpu_id': None,
        'batch_size': 1,
        'server_name': 'MMS',
        'server_version': '0.7.1',
        'limit_max_image_pixels': True
    },
    'request_ids': {
        0: '4e269ce2-8558-4876-bef2-1da756faf495'
    },
    '_request_processor': [
        <ts.context.RequestProcessor object at 0x7f6bfa953250>
    ],
    '_metrics': <ts.metrics.metric_cache_yaml_impl.MetricsCacheYamlImpl object at 0x7f6c38f67490>,
    '_limit_max_image_pixels': True
}
"""


class ModelHandler(BaseHandler):
    """
    A custom model handler implementation.
    """

    def __init__(self):
        self._context = None
        self.initialized = False
        self.explain = False
        self.target = 0
        self.map_location = None

    # def initialize(self, context):
    #     """
    #     Initialize model. This will be called during model loading time
    #     :param context: Initial context contains model server system properties.
    #     :return:
    #     """
    #     self._context = context
    #     self.initialized = True
    #     #  load the model, refer 'custom handler class' above for details

    # def preprocess(self, data):
    #     """
    #     Transform raw input into model input data.
    #     :param batch: list of raw requests, should match batch size
    #     :return: list of preprocessed model input data
    #     """
    #     # Take the input data and make it inference ready
    #     preprocessed_data = data[0].get("data")
    #     if preprocessed_data is None:
    #         preprocessed_data = data[0].get("body")

    #     return preprocessed_data


    # def inference(self, model_input):
    #     """
    #     Internal inference methods
    #     :param model_input: transformed model input data
    #     :return: list of inference output in NDArray
    #     """
    #     # Do some inference call to engine here and return output
    #     model_output = self.model.forward(model_input)
    #     return model_output

    # def postprocess(self, inference_output):
    #     """
    #     Return inference result.
    #     :param inference_output: list of inference output
    #     :return: list of predict results
    #     """
    #     # Take output from network and post-process to desired format
    #     postprocess_output = inference_output
    #     return postprocess_output

    # def handle(self, data, context):
    #     """
    #     Invoke by TorchServe for prediction request.
    #     Do pre-processing of data, prediction using model and postprocessing of prediciton output
    #     :param data: Input data for prediction
    #     :param context: Initial context contains model server system properties.
    #     :return: prediction output
    #     """
    #     model_input = self.preprocess(data)
    #     model_output = self.inference(model_input)
    #     return self.postprocess(model_output)

    def initialize(self, context: Context):
        """
        Initialize model. This will be called during model loading time
        :param context: Initial context contains model server system properties.
        :return:
        """
        self._context = context
        self.initialized = True

        #  load the model
        self.manifest = context.manifest

        properties = context.system_properties
        model_dir = properties.get("model_dir")
        self.device = torch.device("cuda:" + str(properties.get("gpu_id")) if torch.cuda.is_available() else "cpu")

        # Read model serialize/pt file
        # from model import Model
        model_file = self.manifest["model"].get("modelFile", "")
        serialized_file = self.manifest['model']['serializedFile']
        model_pt_path = os.path.join(model_dir, serialized_file)
        if not os.path.isfile(model_pt_path):
            raise RuntimeError("Missing the model.pth file")


        try:
            with open("model_kwargs.json", "r") as f:
                model_kwargs  = json.load(f)
            self.model = self._load_model_with_state_dict(model_dir, model_kwargs)
            self.error = "none"
        except Exception as e:
            import traceback as tb
            tb.print_exc()
            self.error = str(e)


    def handle(self, data, context) -> List[object]:
        """
        Invoke by TorchServe for prediction request.
        Do pre-processing of data, prediction using model and postprocessing of prediciton output
        :param data: Input data for prediction. if None, [{'body': bytearray(b'')}]
        :param context: Initial context contains model server system properties.
        :return: prediction output
        """
        # model_input = self.preprocess(data)
        # model_output = self.inference(model_input)
        # return self.postprocess(model_output)
        return [ {"type": "test", "value": 1.0, "error": self.error, "data": str(data)} ]


    def _load_model_with_state_dict(self, model_dir: str, model_kwargs: dict):
        global Model
        import sys; sys.path.append(model_dir)
        from model import Model
        return Model(**model_kwargs)


    def _load_pickled_model(self, model_dir, model_file, model_pt_path, **model_kwargs):
        """
        Loads the pickle file from the given model path.

        Args:
            model_dir (str): Points to the location of the model artifacts.
            model_file (.py): the file which contains the model class.
            model_pt_path (str): points to the location of the model pickle file.

        Raises:
            RuntimeError: It raises this error when the model.py file is missing.
            ValueError: Raises value error when there is more than one class in the label,
                        since the mapping supports only one label per class.

        Returns:
            serialized model file: Returns the pickled pytorch model file
        """
        model_def_path = os.path.join(model_dir, model_file)
        if not os.path.isfile(model_def_path):
            raise RuntimeError("Missing the model.py file")

        module = importlib.import_module(model_file.split(".")[0])
        model_class_definitions = list_classes_from_module(module)
        if len(model_class_definitions) != 1:
            raise ValueError(
                "Expected only one class as model definition. {}".format(
                    model_class_definitions
                )
            )

        try:
            import torch_xla.core.xla_model as xm
            XLA_AVAILABLE = True
        except ImportError as e:
            XLA_AVAILABLE = False

        model_class = model_class_definitions[0]
        model = model_class(**model_kwargs)
        if model_pt_path:
            map_location = (
                None if (XLA_AVAILABLE and self.map_location is None) else self.device
            )
            state_dict = torch.load(model_pt_path, map_location=map_location)
            model.load_state_dict(state_dict)
        return model