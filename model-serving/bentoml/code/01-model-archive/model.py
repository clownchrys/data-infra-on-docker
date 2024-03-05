import torch
import json
import argparse
import os
from datetime import datetime
from pytz import timezone
from bentoml.pytorch import save_model


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
    parser.add_argument("--artifact-dir", default="/tmp/model-artifacts", type=str)
    args = parser.parse_args()

    model_kwargs = {
        "n_users": 1_998_070,
        "n_items": 2_229_701,
        "embedding_size": 64
    }

    model = Model(**model_kwargs)
    index2user = {k: v for (k, v) in enumerate(range(model_kwargs["n_users"]))}
    index2item = {k: v for (k, v) in enumerate(range(model_kwargs["n_items"]))}

    os.makedirs(args.artifact_dir, exist_ok=True)

    # bento model exports
    """
    save_model(name: 'str', model: "'torch.nn.Module'", *, signatures: 'ModelSignaturesType | None' = None, labels: 't.Dict[str, str] | None' = None, custom_objects: 't.Dict[str, t.Any] | None' = None, external_modules: 't.List[ModuleType] | None' = N
    one, metadata: 't.Dict[str, t.Any] | None' = None) -> 'bentoml.Model'
        Save a model instance to BentoML modelstore.
        
        Args:
            name (:code:`str`):
                Name for given model instance. This should pass Python identifier check.
            model (:code:`torch.nn.Module`):
                Instance of model to be saved
            signatures (:code:`ModelSignaturesType`, `optional`, default to :code:`None`):
                A dictionary of method names and their corresponding signatures.
            labels (:code:`Dict[str, str]`, `optional`, default to :code:`None`):
                user-defined labels for managing models, e.g. team=nlp, stage=dev
            custom_objects (:code:`Dict[str, Any]]`, `optional`, default to :code:`None`):
                user-defined additional python objects to be saved alongside the model,
                e.g. a tokenizer instance, preprocessor function, model configuration json
            external_modules (:code:`List[ModuleType]`, `optional`, default to :code:`None`):
                user-defined additional python modules to be saved alongside the model or custom objects,
                e.g. a tokenizer module, preprocessor module, model configuration module
            metadata (:code:`Dict[str, Any]`, `optional`,  default to :code:`None`):
                Custom metadata for given model.
        
        Returns:
            :obj:`~bentoml.Tag`: A :obj:`tag` with a format `name:version` where `name` is the user-defined model's name, and a generated `version` by BentoML.
    """
    tag = datetime.now().astimezone(timezone("Asia/Seoul")).strftime('%Y-%m-%d_%H-%M-%S_%Z')
    bento_model = save_model(
        name=f"testmodel:{tag}",
        model=model,
        signatures={
            "__call__": {"batchable": True, "batch_dim": 0},
        },
        labels={
            "PRJ": "TEST PROJECT",
            "STAGE": "DEV"
        },
        external_modules=[
            os
        ],
        metadata={
            "description": "test model"
        }
    )

    # onnx exports
    torch.onnx.export(
        model=model,
        args=(
            torch.IntTensor([0]),
            torch.IntTensor([0]),
        ),
        f=os.path.join(args.artifact_dir,"model.onnx"),
        input_names=[
            "features"
        ],
        output_names=[
            "output"
        ],
        verbose=True,
    )

    # jit compiled exports
    torch.jit.save(
        torch.jit.trace(model.forward, [torch.IntTensor([0]), torch.IntTensor([0])]),
        os.path.join(args.artifact_dir, "traced_model.pt")
    )

    # dummy index2sth files
    with open(os.path.join(args.artifact_dir, "index2item.json"), "w") as f: json.dump(index2item, f)
    with open(os.path.join(args.artifact_dir, "index2user.json"), "w") as f: json.dump(index2user, f)


if __name__ == "__main__":
    main()
