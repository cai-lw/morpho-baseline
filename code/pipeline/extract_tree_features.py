import os
import pickle
import argparse
from collections import Counter, defaultdict

import numpy as np

W = 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--pos', type=str, metavar='PATH',
                        help="the path to the pos pred file")
    parser.add_argument('--et', type=str, metavar='PATH',
                        help="the path to the edit trees")
    parser.add_argument('--output', type=str, metavar='PATH',
                        help="the path to save the features with edit trees")
    parser.add_argument('--verbose', action='store_true',
                        help="the flag to show more running details")
    args = parser.parse_args()

    # build paths
    pos_path = os.path.abspath(args.pos)
    et_path = os.path.abspath(args.et)
    output_path = os.path.abspath(args.output)
    output_dir = os.path.dirname(output_path)

    # read result POS tags
    corpus_and_pos = [[]]
    with open(pos_path) as f:
        for line in f:
            line = line.strip()
            if len(line) == 0:
                corpus_and_pos.append([])
            else:
                l = line.split()
                corpus_and_pos[-1].append((l[0], l[3]))

    # read edittrees
    with open(et_path, 'rb') as f:
        et_data = pickle.load(f)

    # extract edit tree features
    et2feature = defaultdict(lambda: defaultdict(float))
    feature2id = {}
    if args.verbose:
        print("Extracting edit tree features ... ", end='', flush=True)
    for et_pack in et_data:
        et = et_pack['et']
        lemma_word_records = et_pack['lemma_word_record']
        for lemma_word_record in lemma_word_records:
            word = lemma_word_record[1]
            if len(lemma_word_record) == 3:  # weight used
                weight = lemma_word_record[2]
            else:
                weight = 1
            for line in corpus_and_pos:
                for i, (w_curr, p_curr) in enumerate(line):
                    if w_curr == word:
                        f_curr = []
                        for j in range(i-W, i+W+1):
                            if j < 0:
                                f_curr.append('.#.')
                            elif j >= len(line):
                                f_curr.append('.#.')
                            else:
                                f_curr.append(line[j][1])
                        f_curr = tuple(f_curr)
                        et2feature[et][f_curr] += weight
                        if f_curr not in feature2id:
                            feature2id[f_curr] = len(feature2id)
    et2feature_np = np.zeros((len(et_data), len(feature2id)))
    for i, et_pack in enumerate(et_data):
        et = et_pack['et']
        for feature, j in feature2id.items():
            et2feature_np[i][j] = et2feature[et][feature]
    if args.verbose:
        print("Done. ({} features)".format(et2feature_np.shape[1]))

    for i, et_pack in enumerate(et_data):
        et_pack['feature'] = et2feature_np[i]

    # output
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    with open(output_path, 'wb') as f:
        pickle.dump(et_data, f)
