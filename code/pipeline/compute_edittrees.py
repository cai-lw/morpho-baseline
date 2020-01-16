import os
import pickle
import argparse
from collections import Counter, defaultdict

from edittree import editTree


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--pairs', type=str, metavar='PATH',
                        help="the path to the (lemma, word) pair list")
    parser.add_argument('--output', type=str, metavar='PATH',
                        help="the path to save the filtered edit trees")
    parser.add_argument('--verbose', action='store_true',
                        help="the flag to show more running details")
    args = parser.parse_args()

    # build paths
    pairs_path = os.path.abspath(args.pairs)
    output_path = os.path.abspath(args.output)
    output_dir = os.path.dirname(output_path)

    lemma_weight = defaultdict(float)

    # read plausible pairs
    plausible_lw_pairs = defaultdict(set)
    pair_weight = {}
    with open(pairs_path) as f:
        for line in f:
            lemma, word, weight = line.strip().split('\t')
            weight = float(weight)
            plausible_lw_pairs[lemma].add(word)
            pair_weight[(lemma, word)] = weight
            if weight > lemma_weight[lemma]:
                lemma_weight[lemma] = weight

    total_weight = 0.0
    for lemma, weight in lemma_weight.items():
        total_weight += weight
    print("total weight: {}".format(total_weight))
    ET_THRESHOLD = max(0.05 * total_weight, 2)
    print("ET_THRESHOLD: {}".format(ET_THRESHOLD))

    # compute edit trees
    et_weight = defaultdict(float)
    et_record = defaultdict(list)
    print("Computing edit trees ... ", end='', flush=True)
    for lemma in plausible_lw_pairs:
        for word in plausible_lw_pairs[lemma]:
            et = editTree(lemma, word)
            weight = pair_weight[(lemma, word)]
            et_record[et].append((lemma, word, weight))
            et_weight[et] += weight
    print("Done. ({} edit trees)".format(len(et_record)))

    if args.verbose:
        print("Top edit trees:")
        for et, count in sorted(et_weight.items(), key=lambda x:x[1], reverse=True)[:40]:
            print(et)
            print(count)
            print(et_record[et][:5])
            print('----------')

    # filter edit trees
    et_filtered = []
    print("Filtering edit trees ... ", end='', flush=True)
    for et, count in sorted(et_weight.items(), key=lambda x:x[1]):
        if count >= ET_THRESHOLD:
            et_filtered.append(et)
    print("Done. ({} edit trees)".format(len(et_filtered)))
        
    # output
    output_et = []
    for et in et_filtered:
        output_et.append({
            'et': et,
            'lemma_word_record': et_record[et]
        })
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    with open(output_path, 'wb') as f:
        pickle.dump(output_et, f)
