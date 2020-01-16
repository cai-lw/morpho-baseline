import os
import argparse
from collections import defaultdict


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--lemmas', type=str, metavar='PATH',
                        help="the path to the lemma list")
    parser.add_argument('--uzh-train', type=str, metavar='PATH',
                        help="the path to read the uzh training samples")
    parser.add_argument('--uzh-dev', type=str, metavar='PATH',
                        help="the path to read the uzh dev samples")
    parser.add_argument('--uzh-test-pred', type=str, metavar='PATH',
                        help="the path to read the uzh test predictions")
    parser.add_argument('--output', type=str, metavar='PATH',
                        help="the path to save uzh outputs")
    parser.add_argument('--verbose', action='store_true',
                        help="the flag to show more running details")
    args = parser.parse_args()

    # build paths
    lemmas_path = os.path.abspath(args.lemmas)
    uzh_train_path = os.path.abspath(args.uzh_train)
    uzh_dev_path = os.path.abspath(args.uzh_dev)
    uzh_test_pred_path = os.path.abspath(args.uzh_test_pred)
    output_path = os.path.abspath(args.output)
    output_dir = os.path.dirname(output_path)

    # read lemmas
    lemmas = []
    with open(lemmas_path, 'r') as f:
        for line in f:
            lemmas.append(line.strip())
    lemmas = set(lemmas)

    predictions = defaultdict(dict)

    # read train samples
    with open(uzh_train_path, 'r') as f:
        for line in f:
            l, w, t = line.strip().split('\t')
            if l in lemmas and t != '-1':
                predictions[l][t] = w
    
    # read dev samples
    with open(uzh_dev_path, 'r') as f:
        for line in f:
            l, w, t = line.strip().split('\t')
            if l in lemmas and t != '-1':
                predictions[l][t] = w

    # read test predictions
    with open(uzh_test_pred_path, 'r') as f:
        for line in f:
            l, w, t = line.strip().split('\t')
            if l in lemmas and t != '-1':
                predictions[l][t] = w

    # output
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    with open(output_path, 'w') as f_out:
        for lemma in predictions:
            for tag, word in predictions[lemma].items():
                f_out.write('{}\t{}\t{}\n'.format(lemma, word, tag))
