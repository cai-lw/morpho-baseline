# Baseline for SIGMORPHON 2020, Task 2

This is the official baseline for SIGMORPHON 2020 Task 2: **Unsupervised Discovery of Morphological Paradigms**.

## Getting Started

### Preparing Docker

1. Install [Docker](https://www.docker.com/)
2. Run `docker build -t morpho-baseline .`

### Running the Official Baseline with Docker

Run with:
```
docker run -v $<DATA_DIR>:/app/data -v $<OUTPUT_DIR>:/app/output morpho-baseline [test|dev] <LANG>
```
where `<DATA_DIR>` is the absolute path to the local data directory, and `<OUTPUT_DIR>` is the absolute path to the desired directory to save outputs. For example:
```
docker run -v $(pwd)/data:/app/data -v $(pwd)/output:/app/output morpho-baseline dev Maltese
```

### Other Options

We additionally provide two trivial baseline systems:

* LB-GT: this baseline generates inflected forms identical to the lemma for each paradigm slot; the gold number of paradigm slots is *given*
* LB-Dev: this baseline generates inflected forms identical to the lemma for each paradigm slot; the number of paradigm slots is *the averge of all development languages*

To use any system besides the official baseline, run:
```
docker run -v $<DATA_DIR>:/app/data -v $<OUTPUT_DIR>:/app/output morpho-baseline <SYSTEM> [test|dev] <LANG>
```
For example:
```
docker run -v $(pwd)/data:/app/data -v $(pwd)/output:/app/output morpho-baseline LB-GT dev Maltese
```

## Evaluation

`python3 evaluate.py <reference_file> <prediction_file>`.

Both `<reference_file>` and `<prediction_file>` are lines of tab-separated triplets: lemma, inflected word, morphological tags.

### Unit Testing

Install pytest and run `pytest` in the `code` folder.
