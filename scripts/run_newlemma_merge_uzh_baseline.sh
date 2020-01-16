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

python $CODE_DIR/pipeline/prep_unsupervised_pos.py --text $DATA_DIR/$2.bible.txt --tmp-text $TMP_DIR/$2/lower_text.txt --tmp-ans $TMP_DIR/$2/pos_pseudo_answer.txt

# unsupervised pos tagging
$ANCHOR_EXT --output $TMP_DIR/$2/anchor --data $TMP_DIR/$2/lower_text.txt --train --unsup anchor --states 8 --triter 50
$ANCHOR_EXT --output $TMP_DIR/$2/anchor --data $TMP_DIR/$2/pos_pseudo_answer.txt --pred $TMP_DIR/$2/pos_pred.txt

python $CODE_DIR/pipeline/extract_tree_features.py --pos $TMP_DIR/$2/pos_pred.txt --et $TMP_DIR/$2/newlemma_edittrees.pkl --output $TMP_DIR/$2/tree_features.pkl --verbose
python $CODE_DIR/pipeline/merge_tree_by_features.py --et $TMP_DIR/$2/tree_features.pkl --output $TMP_DIR/$2/et_groups.pkl --verbose
python $CODE_DIR/pipeline/make_uzh_samples_byetgroups.py --et-groups $TMP_DIR/$2/et_groups.pkl --lemmas $DATA_DIR/$2.V-$1 --output-train $TMP_DIR/$2/uzh.train --output-dev $TMP_DIR/$2/uzh.dev --output-test $TMP_DIR/$2/uzh.test --verbose

source activate_dynet.sh

cd $UZH_LIB

python $UZH_LIB/run_transducer.py --dynet-seed 1 --dynet-mem 500 --dynet-autobatch 0  --transducer=haem --sigm2017format \
--input=100 --feat-input=20 --action-input=100 --pos-emb  --enc-hidden=200 --dec-hidden=200 --enc-layers=1 \
--dec-layers=1   --mlp=0 --nonlin=ReLU --il-optimal-oracle --il-loss=nll --il-beta=0.5 --il-global-rollout \
--dropout=0 --optimization=ADADELTA --l2=0  --batch-size=1 --decbatch-size=25  --patience=5 --epochs=20 \
--tag-wraps=both --param-tying  --mode=il   --beam-width=0 --beam-widths=4  $TMP_DIR/$2/uzh.train  $TMP_DIR/$2/uzh.dev  $TMP_DIR/$2/uzh_results \
--test-path=$TMP_DIR/$2/uzh.test

source activate_main.sh

python $CODE_DIR/pipeline/organize_uzh.py --lemmas $DATA_DIR/$2.V-$1 --uzh-train $TMP_DIR/$2/uzh.train --uzh-dev $TMP_DIR/$2/uzh.dev --uzh-test-pred $TMP_DIR/$2/uzh_results/f.beam4.test.predictions --output $OUTPUT_DIR/merge_newlemma_uzh/$2.V-$1.output --verbose
python $CODE_DIR/evaluate.py $DATA_DIR/$2.V-$1.gold $OUTPUT_DIR/merge_newlemma_uzh/$2.V-$1.output
