# Baseline for SIGMORPHON 2020

## Getting started

### Prepare

We recommend to use `conda` to manage environments, and follow these steps to start working with our baseline system:

1. Create a Python2 conda environment and activate it. Name it to `dynet` or something else (and replace `dynet` to the name you use in `scripts/activate_dynet.sh`).
2. Install [DyNet](https://github.com/clab/dynet) in the Python2 conda environment.
3. Install the [UZH system](https://github.com/ZurichNLP/emnlp2018-imitation-learning-for-neural-morphology).
4. Create a Python3 conda environment and activate it. Name it to `sharedtask` or something else (and replace `sharedtask` to the name you use in `scripts/activate_main.sh`).
5. Run `pip install -r requirements.txt` to install dependencies.
6. Install [Anchor-HMM](https://github.com/karlstratos/anchor).
7. Update paths in `scripts/paths.sh`.

### Run

You can just try the baseline scripts in `scripts/` in the Python3 environment with format

```
bash <SCRIPT> <SPLIT> <LANG>
```

where `<SCRIPT>` is the file name of the script, `<SPLIT>` is either `dev` or `test`, and `<LANG>` is the full name of the language (like `English`). 

## Evaluation

`python3 evaluate.py <reference_file> <prediction_file>`.

Both `<reference_file>` and `<prediction_file>` are lines of tab-separated triplets: lemma, inflected word, grammatical tags.

### Unit test

Install pytest and run `pytest` in the `code` folder.
