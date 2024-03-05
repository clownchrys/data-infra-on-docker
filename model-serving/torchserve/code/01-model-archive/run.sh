#!/bin/bash

# $ torch-model-archiver -h
# usage: torch-model-archiver [-h] --model-name MODEL_NAME  --version MODEL_VERSION_NUMBER
#                       --model-file MODEL_FILE_PATH --serialized-file MODEL_SERIALIZED_PATH
#                       --handler HANDLER [--runtime {python,python3}]
#                       [--export-path EXPORT_PATH] [-f] [--requirements-file] [--config-file]

# Model Archiver Tool

# optional arguments:
#   -h, --help            show this help message and exit
#   --model-name MODEL_NAME
#                         Exported model name. Exported file will be named as
#                         model-name.mar and saved in current working directory
#                         if no --export-path is specified, else it will be
#                         saved under the export path
#   --serialized-file SERIALIZED_FILE
#                         Path to .pt or .pth file containing state_dict in
#                         case of eager mode or an executable ScriptModule
#                         in case of TorchScript.
#   --model-file MODEL_FILE
#                         Path to python file containing model architecture.
#                         This parameter is mandatory for eager mode models.
#                         The model architecture file must contain only one
#                         class definition extended from torch.nn.Module.
#   --handler HANDLER     TorchServe's default handler name  or handler python
#                         file path to handle custom TorchServe inference logic.
#   --extra-files EXTRA_FILES
#                         Comma separated path to extra dependency files.
#   --runtime {python,python3}
#                         The runtime specifies which language to run your
#                         inference code on. The default runtime is
#                         RuntimeType.PYTHON. At the present moment we support
#                         the following runtimes python, python3
#   --export-path EXPORT_PATH
#                         Path where the exported .mar file will be saved. This
#                         is an optional parameter. If --export-path is not
#                         specified, the file will be saved in the current
#                         working directory.
#   --archive-format {tgz, no-archive, zip-store, default}
#                         The format in which the model artifacts are archived.
#                         "tgz": This creates the model-archive in <model-name>.tar.gz format.
#                         If platform hosting requires model-artifacts to be in ".tar.gz"
#                         use this option.
#                         "no-archive": This option creates an non-archived version of model artifacts
#                         at "export-path/{model-name}" location. As a result of this choice,
#                         MANIFEST file will be created at "export-path/{model-name}" location
#                         without archiving these model files
#                         "zip-store": This creates the model-archive in <model-name>.mar format
#                         but will skip deflating the files to speed up creation. Mainly used
#                         for testing purposes
#                         "default": This creates the model-archive in <model-name>.mar format.
#                         This is the default archiving format. Models archived in this format
#                         will be readily hostable on TorchServe.
#   -f, --force           When the -f or --force flag is specified, an existing
#                         .mar file with same name as that provided in --model-
#                         name in the path specified by --export-path will
#                         overwritten
#   -v, --version         Model's version.
#   -r, --requirements-file
#                         Path to requirements.txt file containing a list of model specific python
#                         packages to be installed by TorchServe for seamless model serving.
#   -c, --config-file         Path to a model config yaml file.

# Handler
# Handler can be TorchServe's inbuilt handler name or path to a py file to handle custom TorchServe inference logic. TorchServe supports the following handlers out of box:

# image_classifier
# object_detector
# text_classifier
# image_segmenter

# Custom Handler
# https://github.com/pytorch/serve/blob/master/docs/custom_service.md

MODEL_ARTIFACTS=/tmp/model-artifacts

mkdir -p ${MODEL_ARTIFACTS}
python model.py --artifact-dir ${MODEL_ARTIFACTS}

mkdir -p ${MODEL_STORE}
torch-model-archiver \
--model-name testmodel \
--version 1.0 \
--model-file ./model.py \
--handler ./model_handler.py \
--serialized-file ${MODEL_ARTIFACTS}/model.pth \
--extra-files ${MODEL_ARTIFACTS}/index2item.json,${MODEL_ARTIFACTS}/model_kwargs.json \
--export-path ${MODEL_STORE} \
--force
