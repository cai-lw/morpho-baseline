if [ "$#" -ne 2 ]
then
  echo "Usage: bash run_lemma_baseline_gt.sh test/dev <LANG>"
  exit 1
fi

source paths.sh

python $CODE_DIR/lemma-baseline/lemma_baseline_gt.py --lemmas $DATA_DIR/$2.V-$1 --gold $DATA_DIR/$2.V-$1.gold --output $OUTPUT_DIR/lemma_gt/$2.V-$1.output
python $CODE_DIR/lemma_baseline_evaluation.py $DATA_DIR/$2.V-$1.gold $OUTPUT_DIR/lemma_gt/$2.V-$1.output
