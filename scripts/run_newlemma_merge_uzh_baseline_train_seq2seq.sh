if [ "$#" -ne 2 ]
then
  echo "Usage: bash run_newlemma_merge_uzh_baseline_train_seq2seq.sh test/dev <LANG>"
  exit 1
fi

source paths.sh
source activate_dynet.sh

cd $UZH_LIB

python $UZH_LIB/run_transducer.py --dynet-seed 1 --dynet-mem 500 --dynet-autobatch 0  --transducer=haem --sigm2017format \
--input=100 --feat-input=20 --action-input=100 --pos-emb  --enc-hidden=200 --dec-hidden=200 --enc-layers=1 \
--dec-layers=1   --mlp=0 --nonlin=ReLU --il-optimal-oracle --il-loss=nll --il-beta=0.5 --il-global-rollout \
--dropout=0 --optimization=ADADELTA --l2=0  --batch-size=1 --decbatch-size=25  --patience=5 --epochs=20 \
--tag-wraps=both --param-tying  --mode=il   --beam-width=0 --beam-widths=4  $OUTPUT_DIR/PCS/$2/uzh.train  $OUTPUT_DIR/PCS/$2/uzh.dev  $OUTPUT_DIR/PCS/$2/uzh_results \
--test-path=$OUTPUT_DIR/PCS/$2/uzh.test

cd $SHELL_DIR

source activate_main.sh

python $CODE_DIR/pipeline/organize_uzh.py --lemmas $DATA_DIR/$2.V-$1 --uzh-train $OUTPUT_DIR/PCS/$2/uzh.train --uzh-dev $OUTPUT_DIR/PCS/$2/uzh.dev --uzh-test-pred $OUTPUT_DIR/PCS/$2/uzh_results/f.beam4.test.predictions --output $OUTPUT_DIR/PCS/$2/$2.V-$1.output --verbose
python $CODE_DIR/evaluate.py $DATA_DIR/$2.V-$1.gold $OUTPUT_DIR/PCS/$2/$2.V-$1.output
