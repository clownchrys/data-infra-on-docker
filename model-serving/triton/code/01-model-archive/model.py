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
    parser.add_argument("--model-store", default="/model-store/testmodel/1", type=str)
    args = parser.parse_args()

    model_kwargs = {
        "n_users": 1_998_070,
        "n_items": 2_229_701,
        "embedding_size": 64
    }

    model = Model(**model_kwargs)
    index2user = {k: v for (k, v) in enumerate(range(model_kwargs["n_users"]))}
    index2item = {k: v for (k, v) in enumerate(range(model_kwargs["n_items"]))}

    os.makedirs(args.model_store, exist_ok=True)

    # onnx exports
    torch.onnx.export(
        model=model,
        args=(
            torch.IntTensor([0]),
            torch.IntTensor([0]),
        ),
        f=os.path.join(args.model_store,"model.onnx"),
        input_names=[
            "input__0",
            "input__1",
        ],
        output_names=[
            "output__0"
        ],
        verbose=True,
    )


if __name__ == "__main__":
    main()
