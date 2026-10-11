# Optional research classifiers

The app works without these models. Enable them only if you need the original
graduation project's natural-language classification behavior.

## Fine-tuned intent model

Install the extra dependencies:

```sh
python -m pip install -e ".[ml]"
```

Place trusted classifier files in `models/intent-classifier/`, or point
`INTENT_MODEL_PATH` to an existing directory. Required files include:

```text
config.json
model.safetensors
tokenizer.json
tokenizer_config.json
special_tokens_map.json
vocab.txt
```

The original artifact is a BERT sequence classifier with 263 labels. Its semantic
label mapping is preserved in `website_builder/data/intent_labels.json`, including
legacy spelling, so the mapping remains aligned with the trained model.

After placing the required files in `models/intent-classifier/`, enable research
mode in your local `.env` file:

```dotenv
USE_ML_CLASSIFIERS=true
INTENT_MODEL_PATH=models/intent-classifier
```

For a fresh clone, model weights must be obtained separately from a source whose
ownership, license, and integrity you have verified. This release does not claim
that they are downloadable from a public model repository.

The original `training_args.bin` is not needed for inference. Do not load arbitrary
pickled training files. The CSV and Excel datasets are not needed to run this app
and are excluded from the public release.

## Zero-shot classifier

Research mode uses
`MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7` through Transformers.
The first relevant inference downloads its weights and tokenizer from Hugging
Face. It requires an internet connection, substantial disk space and memory, and
may take several minutes on a CPU. The app uses CPU inference unless Transformers
is separately configured by the operator.

Exact candidate answers bypass zero-shot inference. Missing local intent weights
produce a setup message without advancing the interview. Verify any model's
upstream terms before redistribution or hosted use.

## Validation limits

The standard release tests do not download or run the research models. Model
availability, inference quality, and hardware requirements need a separate smoke
test after you enable this optional mode. No accuracy benchmark or training
reproducibility claim is made; the original training pipeline was not included.
