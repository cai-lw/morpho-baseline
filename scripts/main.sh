if [ "$#" -eq 2 ]
then
  echo "Received 2 arguments; will run the default pipeline: PCS"
  PIPELINE="PCS"
  SPLIT=$1
  LANG=$2
elif [ "$#" -eq 3 ]
then
  PIPELINE=$1
  SPLIT=$2
  LANG=$3
else
  echo "Invalid number of arguments."
  echo "Usage:"
  echo "    Run with 2 arguments: test/dev <LANG>"
  echo "    or 3 arguments: <PIPELINE> test/dev <LANG>"
  exit 1
fi

source /opt/conda/etc/profile.d/conda.sh
source activate_main.sh

echo "Running $PIPELINE baseline..."
case $PIPELINE in
  LB-GT)
    bash run_lemma_baseline_gt.sh $SPLIT $LANG
    ;;
  LB-Dev)
    bash run_lemma_baseline_dev.sh $SPLIT $LANG
    ;;
  PCS)
    bash run_newlemma_merge_uzh_baseline_prepare_seq2seq.sh $SPLIT $LANG
    bash run_newlemma_merge_uzh_baseline_train_seq2seq.sh $SPLIT $LANG
    ;;
  PCS-prepare-seq2seq)
    bash run_newlemma_merge_uzh_baseline_prepare_seq2seq.sh $SPLIT $LANG
    ;;
  PCS-train-seq2seq)
    bash run_newlemma_merge_uzh_baseline_train_seq2seq.sh $SPLIT $LANG
    ;;
  *)
    echo "Invalid pipeline: $PIPELINE"
  esac
