if [ "$#" -ne 2 ]
then
  echo "Usage: bash run_lemma_baseline_gt.sh test/dev <LANG>"
  exit 1
fi

source paths.sh

DEV_GOLD_FILES=$(find $DATA_DIR -type f \( -iname "*.V-dev.gold" ! -iname "$2.V-$1.gold" \) -print0 | xargs -0)

python $CODE_DIR/lemma-baseline/lemma_baseline_dev.py --lemmas $DATA_DIR/$2.V-$1 --dev-golds $DEV_GOLD_FILES --output $OUTPUT_DIR/lemma_dev/$2.V-$1.output
python $CODE_DIR/lemma_baseline_evaluation.py $DATA_DIR/$2.V-$1.gold $OUTPUT_DIR/lemma_dev/$2.V-$1.output
