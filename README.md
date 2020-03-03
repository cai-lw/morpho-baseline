# Baseline for SIGMORPHON 2020

## Getting started

### Prepare Docker

1. Install [Docker](https://www.docker.com/)
2. Run `docker build -t morpho-baseline .`

### Run with Docker

Run with:
```
docker run -v $<DATA_DIR>:/app/data -v $<OUTPUT_DIR>:/app/output morpho-baseline <PIPELINE> test/dev <LANG>
```
or 
```
docker run -v $<DATA_DIR>:/app/data -v $<OUTPUT_DIR>:/app/output morpho-baseline test/dev <LANG>
```
where `<DATA_DIR>` is the absolute path to the local data directory, and `<OUTPUT_DIR>` is the absolute path to the desired directory to save outputs. For example:
```
docker run -v $(pwd)/data:/app/data -v $(pwd)/output:/app/output morpho-baseline PCS-I+II+III-H test English
```

If you run with the later command, it will run the default pipeline.

#### Available Pipelines
* LB-GT
* LB-Dev
* PCS-I
* PCS-I+II-a
* PCS-I+II-b
* PCS-I+III-C
* PCS-I+III-H
* PCS-I+II+III-C
* PCS-I+II+III-H (default)

## Evaluation

`python3 evaluate.py <reference_file> <prediction_file>`.

Both `<reference_file>` and `<prediction_file>` are lines of tab-separated triplets: lemma, inflected word, grammatical tags.

### Unit test

Install pytest and run `pytest` in the `code` folder.
