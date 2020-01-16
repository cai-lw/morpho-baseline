import os
import pickle
import argparse
from collections import defaultdict

import numpy as np

BEST_SIM_THRESHOLD = 0.3


def cos_sim(x1, x2):
    sim = np.dot(x1, x2)/(np.linalg.norm(x1)*np.linalg.norm(x2))
    return sim


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--et', type=str, metavar='PATH',
                        help="the path to the edit trees with features")
    parser.add_argument('--output', type=str, metavar='PATH',
                        help="the path to save the features with edit trees")
    parser.add_argument('--verbose', action='store_true',
                        help="the flag to show more running details")
    args = parser.parse_args()

    # build paths
    et_path = os.path.abspath(args.et)
    output_path = os.path.abspath(args.output)
    output_dir = os.path.dirname(output_path)

    # read edittrees
    with open(et_path, 'rb') as f:
        et_data = pickle.load(f)

    et_groups = []
    et_lemma_record = defaultdict(set)
    et_all_lemma_record = defaultdict(set)
    et_features = {}

    for et_pack in et_data:
        et = et_pack['et']
        et_groups.append(set([et]))
        lemma_word_records = et_pack['lemma_word_record']
        for lemma_word_record in lemma_word_records:
            lemma = lemma_word_record[0]
            if len(lemma_word_record) == 3:  # weight used
                weight = lemma_word_record[2]
            else:
                weight = 1
            # only record gold lemmas
            if weight > 0.9:
                et_lemma_record[et].add(lemma)
            et_all_lemma_record[et].add(lemma)
        feature = et_pack['feature']
        et_features[et] = feature

    # merge
    if args.verbose:
        print("Merging edit trees ...", flush=True)
    while True:
        if args.verbose:
            for i, et_group in enumerate(et_groups):
                print("#### Group {} ####:".format(i))
                for et in et_group:
                    print(et)
        # calculate tree group f1
        et_F = defaultdict(dict)
        et_sim = []
        if args.verbose:
            print("calculate tree group f1 ...")
        for i, et_group_i in enumerate(et_groups):
            set_i = set()
            for et in et_group_i:
                set_i = set_i.union(et_lemma_record[et])
            if len(set_i) == 0:
                continue
            for j, et_group_j in enumerate(et_groups):
                if j <= i:
                    continue
                set_j = set()
                for et in et_group_j:
                    set_j = set_j.union(et_lemma_record[et])
                if len(set_j) == 0:
                    continue
                set_inter = set_i.intersection(set_j)
                if len(set_inter) > 0:
                    P = len(set_inter) / len(set_i)
                    R = len(set_inter) / len(set_j)
                    F = 2 * P * R / (P + R)
                else:
                    F = 0
                et_F[i][j] = F
                if args.verbose:
                    print(i, j, F)

        # calculate tree group similarity
        if args.verbose:
            print("calculate tree group similarity ...")
        for i in et_F:
            for j in et_F[i]:
                if et_F[i][j] == 0:
                    et_feature_i = np.sum([et_features[et] for et in et_groups[i]], axis=0)
                    et_feature_j = np.sum([et_features[et] for et in et_groups[j]], axis=0)
                    sim = cos_sim(et_feature_i, et_feature_j)
                    et_sim.append((i, j, sim))
                    if args.verbose:
                        print(i, j, sim)
        
        if len(et_sim) == 0:
            break
        else:
            et_sim = sorted(et_sim, key=lambda x: -x[2])
            best_i, best_j, best_sim = et_sim[0]
            best_et_group_i = et_groups[best_i]
            best_et_group_j = et_groups[best_j]
            if args.verbose:
                print("best similarity: {}".format(best_sim))
            if best_sim > BEST_SIM_THRESHOLD:
                # merge j -> i
                if args.verbose:
                    print("merge {} -> {}".format(best_j, best_i))
                et_groups[best_j] = set()
                et_groups[best_i] = best_et_group_i.union(best_et_group_j)
            else:
                break

    if args.verbose:
        print("Merge results:")
        for i, et_group in enumerate(et_groups):
            print("#### Group {} ####:".format(i))
            for et in et_group:
                print(et)

    output_groups = []
    for et_group in et_groups:
        if len(et_group) > 0:
            output_groups.append([])
            for et in et_group:
                et_pack = {
                    'et': et,
                    'lemma_record': et_all_lemma_record[et]
                }
                output_groups[-1].append(et_pack)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    with open(output_path, 'wb') as f:
        pickle.dump(output_groups, f)
