# https://github.com/triton-inference-server/python_backend#quick-start
# pip install transformers[torch] ctranslate2 sacremoses sentencepiece
from transformers import AutoModelForSeq2SeqLM
import numpy as np
import torch
import triton_python_backend_utils as pb_utils


def build_input(requests: list):
    batch_sizes = [np.shape(pb_utils.get_input_tensor_by_name(request, "INPUT_IDS").as_numpy()) for request in requests]
    max_len = np.max([bs[1] for bs in batch_sizes])
    input_ids = torch.tensor(np.concatenate([np.pad(
            pb_utils.get_input_tensor_by_name(request, "INPUT_IDS").as_numpy(),
            ((0, 0), (0, max_len - batch_size[1])),
            ) for batch_size, request in zip(batch_sizes, requests)], axis=0,)
    ).to("cuda")
    attention_mask = torch.tensor(
        (
            np.arange(max_len).repeat(len(requests)).reshape(max_len, len(requests))
            < [bs[1] for bs in batch_sizes]
        ).T
    ).to("cuda")
    return batch_sizes, input_ids, attention_mask


class TritonPythonModel:
    def initialize(self, args):
        self.model = AutoModelForSeq2SeqLM.from_pretrained("facebook/nllb-200-distilled-600M").to("cuda")

    def execute(self, requests: list):
        batch_sizes, input_ids, attention_mask = build_input(requests)
        responses = []
        translated_tokens = self.model.generate(input_ids=input_ids, 
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