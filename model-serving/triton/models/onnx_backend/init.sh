#!/bin/bash

ROOT_DIR=$(realpath $(dirname $0))

python - << EOF
import torch
import argparse
import os

class Model(torch.nn.Module):
    def __init__(self, n_users, n_items, embedding_size):
        super(Model, self).__init__()
        self.user_embedding = torch.nn.Embedding(n_users, embedding_size)
        self.item_embedding = torch.nn.Embedding(n_items, embedding_size)

    def forward(self, user_indices, item_indices):
        user_vectors = self.user_embedding(user_indices)
        item_vectors = self.item_embedding(item_indices)
        score_pred = (user_vectors * item_vectors).sum(dim=-1)
        return score_pred

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model-store",
        default=${ROOT_DIR}/1,
        type=str
    )
    args = parser.parse_args()

    os.makedirs(args.model_store, exist_ok=True)

    model_kwargs = {
        "n_users": 1_998_070,
        "n_items": 2_229_701,
        "embedding_size": 64
    }
    model = Model(**model_kwargs)

    torch.onnx.export(
        model = model,
        args = (torch.IntTensor([0]), torch.IntTensor([0])),
        f = os.path.join(args.model_store, "model.onnx"),
        input_names = ["INPUT_01", "INPUT_02"],
        output_names = ["OUTPUT_01"],
        verbose = True,
    )

if __name__ == "__main__":
    main()
EOF


tee ${ROOT_DIR} << EOF
name: "onnx_backend"
platform: "onnxruntime_onnx"
backend: "onnxruntime"
runtime: ""

version_policy: {
    latest: {
        num_versions: 1
    }
}

input: [
    {
        name: "INPUT_01",
        data_type: TYPE_INT32,
        format: FORMAT_NONE,
        dims: [ 1 ],
        is_shape_tensor: false,
        allow_ragged_batch: false,
        optional: false
    },
    {
        name: "INPUT_02",
        data_type: TYPE_INT32,
        format: FORMAT_NONE,
        dims: [ 1 ],
        is_shape_tensor: false,
        allow_ragged_batch: false,
        optional: false
    }
]
output: [
    {
        name: "OUTPUT_01",
        data_type: TYPE_FP32,
        dims: [ 1 ],
        label_filename: "",
        is_shape_tensor: false
    }
]

max_batch_size: 0
batch_input: []
batch_output: []

optimization: {
    priority: PRIORITY_DEFAULT,
    input_pinned_memory: { enable: true },
    output_pinned_memory: { enable: true },
    gather_kernel_buffer_threshold: 0,
    eager_batching: false
}

instance_group: [
    {
        name: "onnx_backend",
        kind: KIND_CPU,
        count: 1,
        gpus: [],
        secondary_devices: [],
        profile: [],
        passive: false,
        host_policy: ""
    }
]

default_model_filename: "model.onnx",
cc_model_filenames: {},
metric_tags: {},
parameters: {},
model_warmup: []
EOF