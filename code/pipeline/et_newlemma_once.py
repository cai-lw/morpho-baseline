import os
import pickle
import argparse
from collections import defaultdict


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--text', type=str, metavar='PATH',
                        help="the path to the tokenized corpus")
    parser.add_argument('--lemmas', type=str, metavar='PATH',
                        help="the path to the lemma list")
    parser.add_argument('--et', type=str, metavar='PATH',
                        help="the path to the edit trees with features")
    parser.add_argument('--new-lemma-weight', type=float, metavar='FLOAT',
                        help="the weight of new lemmas")
    parser.add_argument('--output-et', type=str, metavar='PATH',
                        help="the path to save the edit trees with new lemma records")
    parser.add_argument('--output-lemmas', type=str, metavar='PATH',
                        help="the path to save the new lemmas with weights")
    parser.add_argument('--verbose', action='store_true',
                        help="the flag to show more running details")
    args = parser.parse_args()

    # build paths
    et_path = os.path.abspath(args.et)
    text_path = os.path.abspath(args.text)
    lemma_path = os.path.abspath(args.lemmas)
    output_et_path = os.path.abspath(args.output_et)
    output_et_dir = os.path.dirname(output_et_path)
    output_lemmas_path = os.path.abspath(args.output_lemmas)
    output_lemmas_dir = os.path.dirname(output_lemmas_path)

    # read edittrees
    with open(et_path, 'rb') as f:
        et_data = pickle.load(f)

    NEW_LEMMA_THRESHOLD = max(int(len(et_data) * 0.2), 3)
    if args.verbose:
        print("NEW_LEMMA_THRESHOLD: {}".format(NEW_LEMMA_THRESHOLD))

    vocab = set()
    lemmas = set()
    lemma_weight = {}
    new_lemmas = set()
    et_record = defaultdict(list)

    with open(lemma_path) as f:
        for line in f:
            row = line.strip().lower().split('\t')
            lemma = row[0]
            if len(row) > 1:  # weighted
                weight = float(row[1])
            else:
                weight = 1
            lemmas.add(lemma)
            lemma_weight[lemma] = weight

    with open(text_path) as f:
        for line in f:
            l = [w.lower() for w in line.strip().split()]
            for w in l:
                vocab.add(w)

    for word in vocab:
        if word not in lemmas:
            count = 0
            infed = []
            for et_pack in et_data:
                et = et_pack['et']
                inflected_word = et.apply(word)
                if inflected_word in vocab:
                    count += 1
                    infed.append((et, inflected_word))
            if count > NEW_LEMMA_THRESHOLD:
                new_lemmas.add(word)
                for et, inflected_word in infed:
                    et_record[et].append((word, inflected_word))
    if args.verbose:
        print("{} new lemmas".format(len(new_lemmas)))
        print(new_lemmas)
    
    # organize
    for et_pack in et_data:
        et = et_pack['et']
        lemma_word_record = et_pack['lemma_word_record']
        et_pack['lemma_word_record'] = set()
        for lemma, word, weight in lemma_word_record:
            et_pack['lemma_word_record'].add((lemma, word, weight))  # use existing weights for existing lemmas
        for lemma, word in et_record[et]:
            et_pack['lemma_word_record'].add((lemma, word, args.new_lemma_weight))  # use the new lemma weight for new lemmas

    # output et data
    if not os.path.exists(output_et_dir):
        os.makedirs(output_et_dir)
    with open(output_et_path, 'wb') as f:
        pickle.dump(et_data, f)

    # output lemmas
    if not os.path.exists(output_lemmas_dir):
        os.makedirs(output_lemmas_dir)
    with open(output_lemmas_path, 'w') as f:
        for lemma in lemmas:
            f.write('{}\t{}\n'.format(lemma, lemma_weight[lemma]))
        for lemma in new_lemmas:
            f.write('{}\t{}\n'.format(lemma, args.new_lemma_weight))
