if [ "$#" -ne 2 ]
then
  echo "Usage: bash run_lemma_baseline.sh test/dev <LANG>"
  exit 1
fi

source paths.sh

python $CODE_DIR/pipeline/make_plausible_pairs.py --text $DATA_DIR/$2.bible.txt --lemmas $DATA_DIR/$2.V-$1 --output $TMP_DIR/$2/plausible_pairs.txt
python $CODE_DIR/pipeline/compute_edittrees.py --pairs $TMP_DIR/$2/plausible_pairs.txt --output $TMP_DIR/$2/filtered_edittrees.pkl --verbose
python $CODE_DIR/pipeline/prep_unsupervised_pos.py --text $DATA_DIR/$2.bible.txt --tmp-text $TMP_DIR/$2/lower_text.txt --tmp-ans $TMP_DIR/$2/pos_pseudo_answer.txt

# unsupervised pos tagging
$ANCHOR_EXT --output $TMP_DIR/$2/anchor --data $TMP_DIR/$2/lower_text.txt --train --unsup anchor --states 8 --triter 50
$ANCHOR_EXT --output $TMP_DIR/$2/anchor --data $TMP_DIR/$2/pos_pseudo_answer.txt --pred $TMP_DIR/$2/pos_pred.txt

python $CODE_DIR/pipeline/extract_tree_features.py --pos $TMP_DIR/$2/pos_pred.txt --et $TMP_DIR/$2/filtered_edittrees.pkl --output $TMP_DIR/$2/tree_features.pkl --verbose
python $CODE_DIR/pipeline/merge_tree_by_features.py --et $TMP_DIR/$2/tree_features.pkl --output $TMP_DIR/$2/et_groups.pkl --verbose
python $CODE_DIR/pipeline/make_uzh_samples_byetgroups.py --et-groups $TMP_DIR/$2/et_groups.pkl --lemmas $DATA_DIR/$2.V-$1 --output-train $TMP_DIR/$2/uzh.train --output-dev $TMP_DIR/$2/uzh.dev --output-test $TMP_DIR/$2/uzh.test --verbose

python $CODE_DIR/pipeline/make_conll17_samples.py --uzh-train $TMP_DIR/$2/uzh.train --uzh-dev $TMP_DIR/$2/uzh.dev --uzh-test $TMP_DIR/$2/uzh.test --conll17-output-dir $TMP_DIR/$2/conll17/

source activate_dynet.sh

python $CODE_DIR/pipeline/conll17.py -o -p $TMP_DIR/$2/conll17/

source activate_main.sh

python $CODE_DIR/pipeline/organize_uzh.py --lemmas $DATA_DIR/$2.V-$1 --uzh-train $TMP_DIR/$2/uzh.train --uzh-dev $TMP_DIR/$2/uzh.dev --uzh-test-pred $TMP_DIR/$2/conll17/task2/conll17-low-out --output $OUTPUT_DIR/merge_conll17/$2.V-$1.output --verbose
python $CODE_DIR/evaluate.py $DATA_DIR/$2.V-$1.gold $OUTPUT_DIR/merge_conll17/$2.V-$1.output
