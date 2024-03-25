# https://github.com/triton-inference-server/python_backend#quick-start
# pip install transformers[torch] ctranslate2 sacremoses sentencepiece
from transformers import AutoModelForSeq2SeqLM
import numpy as np
import torch
import triton_python_backend_utils as pb_utils
import json


def build_input(requests: list, device: str):
    batch_sizes = [np.shape(pb_utils.get_input_tensor_by_name(request, "INPUT_IDS").as_numpy()) for request in requests]
    max_len = np.max([bs[1] for bs in batch_sizes])

    each_ids = [
        np.pad(
            pb_utils.get_input_tensor_by_name(request, "INPUT_IDS").as_numpy(),
            ((0, 0), (0, max_len - batch_size[1])),
        ) for batch_size, request in zip(batch_sizes, requests)
    ]
    input_ids = torch.tensor(np.concatenate(each_ids, axis=0)).to(device)

    attention_mask = torch.tensor(
        (
            np.arange(max_len).repeat(len(requests)).reshape(max_len, len(requests))
            < [bs[1] for bs in batch_sizes]
        ).T
    ).to(device)

    return batch_sizes, input_ids, attention_mask


class TritonPythonModel:
    def initialize(self, kwargs):
        self.model_config: dict = json.loads(kwargs["model_config"]) # json string of config.pbtxt (auto-configured or not)
        self.model_instance_kind: str = kwargs["model_instance_kind"] # CPU | GPU
        self.model_instance_name: str = kwargs["model_instance_name"] # <model_name>_<group_id>_<instance_id>
        self.model_instance_device_id: int = int(kwargs["model_instance_device_id"]) # 0
        self.model_repository: str = kwargs["model_repository"] # /data/models/<model_name>/
        self.model_version: int = kwargs["model_version"] # 1
        self.model_name: str = kwargs["model_name"] # <model_name>
        pb_utils.Logger.log_info(f"model_config <value={self.model_config}>")
        pb_utils.Logger.log_info(f"pb_utils <attrs={dir(pb_utils)}>")

        self.model = AutoModelForSeq2SeqLM.from_pretrained("facebook/nllb-200-distilled-600M", device_map="auto")
        pb_utils.Logger.log_info(f"model_initialized <device={self.model.device}>")

    def execute(self, requests: list):
        batch_sizes, input_ids, attention_mask = build_input(requests, self.model.device)
        responses = []
        translated_tokens = self.model.generate(
            input_ids=input_ids, 
            attention_mask=attention_mask,
            forced_bos_token_id=256042 # German Language token
        ).to("cpu")

        start = 0
        for batch_shape in batch_sizes:
            out_tensor = pb_utils.Tensor(
                "OUTPUT_IDS", translated_tokens[start : start + batch_shape[0], :].numpy().astype(np.int32)
            )
            start += batch_shape[0]
            responses.append(pb_utils.InferenceResponse(output_tensors=[out_tensor]))

        return responses
