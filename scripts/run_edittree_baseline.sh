if [ "$#" -ne 2 ]
then
  echo "Usage: bash run_lemma_baseline.sh test/dev <LANG>"
  exit 1
fi

source paths.sh

python $CODE_DIR/pipeline/make_plausible_pairs.py --text $DATA_DIR/$2.bible.txt --lemmas $DATA_DIR/$2.V-$1 --output $TMP_DIR/$2/plausible_pairs.txt
python $CODE_DIR/pipeline/compute_edittrees.py --pairs $TMP_DIR/$2/plausible_pairs.txt --output $TMP_DIR/$2/filtered_edittrees.pkl --verbose

echo "Predict without merging"
python $CODE_DIR/pipeline/predict_by_edittrees.py --et $TMP_DIR/$2/filtered_edittrees.pkl --lemmas $DATA_DIR/$2.V-$1 --output $OUTPUT_DIR/edittree/$2.V-$1.output
python $CODE_DIR/evaluate.py $DATA_DIR/$2.V-$1.gold $OUTPUT_DIR/edittree/$2.V-$1.output
