import torch
import json
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
    parser.add_argument("--artifact-dir", default="./", type=str)
    args = parser.parse_args()

    model_kwargs = {
        "n_users": 1_998_070,
        "n_items": 2_229_701,
        "embedding_size": 64
    }

    model = Model(**model_kwargs)
    index2user = {k: v for (k, v) in enumerate(range(model_kwargs["n_users"]))}
    index2item = {k: v for (k, v) in enumerate(range(model_kwargs["n_items"]))}

    # case of eager mode
    torch.save(
        model,
        os.path.join(args.artifact_dir, "model.pth")
    )
    with open(os.path.join(args.artifact_dir, "model_kwargs.json"), "w") as f: json.dump(model_kwargs, f)

    # case of jit compiled
    torch.jit.save(
        torch.jit.trace(model.forward, [torch.IntTensor([0]), torch.IntTensor([0])]),
        os.path.join(args.artifact_dir, "traced_model.pt")
    )

    # dummy index2sth files
    with open(os.path.join(args.artifact_dir, "index2item.json"), "w") as f: json.dump(index2item, f)
    with open(os.path.join(args.artifact_dir, "index2user.json"), "w") as f: json.dump(index2user, f)


if __name__ == "__main__":
    main()
