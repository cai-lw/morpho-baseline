# Baseline for SIGMORPHON 2020

`pip install -r requirements.txt` to install dependencies.

## Evaluation

`python3 evaluate.py <reference_file> <prediction_file>`.

Both `<reference_file>` and `<prediction_file>` are lines of tab-separated triplets: lemma, inflected word, grammatical tags.

## Unit test

Install pytest and run `pytest` in the root folder.

## Language Model

We directly use the original [AWD-LSTM](https://github.com/salesforce/awd-lstm-lm) code.
Training only works with PyTorch 0.4.0, but inference works with PyTorch 1.x (with a bunch of warning).

Use `make_lm_dataset.py` to generate character LM dataset. See the `awd-lstm-lm/README.md` for how to train. See `lm_example.py` and `word_prob_example.py` for how to inference.
