# Baseline for SIGMORPHON 2020

## Evaluation

NetworkX 2.4rc1 is not on pip yet. Please follow https://networkx.github.io/documentation/latest/install.html#install-the-development-version to install it.

## Unit test

Install pytest and run `pytest` in the root folder.

## Language Model

We directly use the original [AWD-LSTM](https://github.com/salesforce/awd-lstm-lm) code.
Training only works with PyTorch 0.4.0, but inference works with PyTorch 1.x (with a bunch of warning).

Use `make_lm_dataset.py` to generate character LM dataset. See the `awd-lstm-lm/README.md` for how to train. See `lm_example.py` for how to inference.
