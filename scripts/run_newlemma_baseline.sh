if [ "$#" -ne 2 ]
then
  echo "Usage: bash run_lemma_baseline.sh test/dev <LANG>"
  exit 1
fi

source paths.sh

python $CODE_DIR/pipeline/make_plausible_pairs.py --text $DATA_DIR/$2.bible.txt --lemmas $DATA_DIR/$2.V-$1 --output $TMP_DIR/$2/plausible_pairs.txt
python $CODE_DIR/pipeline/compute_edittrees.py --pairs $TMP_DIR/$2/plausible_pairs.txt --output $TMP_DIR/$2/filtered_edittrees.pkl --verbose

# first time of new lemma discovery
python $CODE_DIR/pipeline/et_newlemma_once.py --text $DATA_DIR/$2.bible.txt --lemmas $DATA_DIR/$2.V-$1 --et $TMP_DIR/$2/filtered_edittrees.pkl --new-lemma-weight 0.5 --output-et $TMP_DIR/$2/newlemma_edittrees.pkl --output-lemmas $TMP_DIR/$2/updated_lemmas_1.txt --verbose

python $CODE_DIR/pipeline/make_plausible_pairs.py --text $DATA_DIR/$2.bible.txt --lemmas $TMP_DIR/$2/updated_lemmas_1.txt --output $TMP_DIR/$2/plausible_pairs_2.txt --weight
python $CODE_DIR/pipeline/compute_edittrees.py --pairs $TMP_DIR/$2/plausible_pairs_2.txt --output $TMP_DIR/$2/filtered_edittrees_2.pkl --verbose

echo "Predict without merging"
python $CODE_DIR/pipeline/predict_by_edittrees.py --et $TMP_DIR/$2/filtered_edittrees_2.pkl --lemmas $DATA_DIR/$2.V-$1 --output $OUTPUT_DIR/newlemma_1/$2.V-$1.output
python $CODE_DIR/evaluate.py $DATA_DIR/$2.V-$1.gold $OUTPUT_DIR/newlemma_1/$2.V-$1.output
