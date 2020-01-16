import os
import pickle
import random
import argparse
from collections import defaultdict

TRAIN_DEV_RATIO = 0.2


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--et-groups', type=str, metavar='PATH',
                        help="the path to the edit trees with features")
    parser.add_argument('--lemmas', type=str, metavar='PATH',
                        help="the path to the lemma list")
    parser.add_argument('--output-train', type=str, metavar='PATH',
                        help="the path to save the uzh training samples")
    parser.add_argument('--output-dev', type=str, metavar='PATH',
                        help="the path to save the uzh dev samples")
    parser.add_argument('--output-test', type=str, metavar='PATH',
                        help="the path to save the uzh test samples")
    parser.add_argument('--verbose', action='store_true',
                        help="the flag to show more running details")
    args = parser.parse_args()


    # build paths
    et_groups_path = os.path.abspath(args.et_groups)
    lemmas_path = os.path.abspath(args.lemmas)
    output_train_path = os.path.abspath(args.output_train)
    output_train_dir = os.path.dirname(output_train_path)
    output_dev_path = os.path.abspath(args.output_dev)
    output_dev_dir = os.path.dirname(output_dev_path)
    output_test_path = os.path.abspath(args.output_test)
    output_test_dir = os.path.dirname(output_test_path)

    # read edittree groups
    with open(et_groups_path, 'rb') as f:
        et_groups = pickle.load(f)

    # read lemmas
    lemmas = []
    with open(lemmas_path, 'r') as f:
        for line in f:
            lemmas.append(line.strip())

    # build training data
    seq2seq_train = []
    seq2seq_dev = []
    seq2seq_test = []

    # standard lemmas
    for lemma in lemmas:
        for i, et_group in enumerate(et_groups):
            bj = False
            for et_pack in et_group:
                et = et_pack['et']
                lemma_record = et_pack['lemma_record']
                if lemma in lemma_record:
                    bj = True
                    if random.random() < TRAIN_DEV_RATIO:  
                        seq2seq_dev.append((lemma, et.apply(lemma), i))
                    else:
                        seq2seq_train.append((lemma, et.apply(lemma), i))
            if not bj and len(et_group) > 0:
                seq2seq_test.append((lemma, '', i))

    # new lemmas
    for i, et_group in enumerate(et_groups):
        bj = False
        for et_pack in et_group:
            et = et_pack['et']
            lemma_record = et_pack['lemma_record']
            for lemma in lemma_record:
                if lemma not in lemmas:
                    if random.random() < TRAIN_DEV_RATIO:  
                        seq2seq_dev.append((lemma, et.apply(lemma), i))
                    else:
                        seq2seq_train.append((lemma, et.apply(lemma), i))

    # output
    if not os.path.exists(output_train_dir):
        os.makedirs(output_train_dir)
    if not os.path.exists(output_dev_dir):
        os.makedirs(output_dev_dir)
    if not os.path.exists(output_test_dir):
        os.makedirs(output_test_dir)
    with open(output_train_path, 'w') as f_train:
        for l, w, i in seq2seq_train:
            f_train.write("{}\t{}\t{}\n".format(l, w, i))
    with open(output_dev_path, 'w') as f_dev:
        for l, w, i in seq2seq_dev:
            f_dev.write("{}\t{}\t{}\n".format(l, w, i))
    with open(output_test_path, 'w') as f_test:
        for l, w, i in seq2seq_test:
            f_test.write("{}\t{}\t{}\n".format(l, w, i))
