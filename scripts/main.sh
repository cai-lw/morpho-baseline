if [ "$#" -eq 2 ]
then
  echo "Received 2 arguments; will run the default pipeline: PCS-I+II+III-H"
  PIPELINE="PCS-I+II+III-H"
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
  PCS-I)
    bash run_edittree_baseline.sh $SPLIT $LANG
    ;;
  PCS-I+II-a)
    bash run_newlemma_baseline.sh $SPLIT $LANG
    ;;
  PCS-I+II-b)
    bash run_newlemma2_baseline.sh $SPLIT $LANG
    ;;
  PCS-I+III-C)
    bash run_merge_conll17_baseline.sh $SPLIT $LANG
    ;;
  PCS-I+III-H)
    bash run_merge_uzh_baseline.sh $SPLIT $LANG
    ;;
  PCS-I+II+III-C)
    bash run_newlemma_merge_conll17_baseline.sh $SPLIT $LANG
    ;;
  PCS-I+II+III-H)
    bash run_newlemma_merge_uzh_baseline.sh $SPLIT $LANG
    ;;
  *)
    echo "Invalid pipeline: $PIPELINE"
  esac
