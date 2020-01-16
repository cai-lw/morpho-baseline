import os
import argparse

from edittree import longestSubstring

PLAUSIBLE_THRESHOLD = 0.5


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--text', type=str, metavar='PATH',
                        help="the path to the tokenized corpus")
    parser.add_argument('--lemmas', type=str, metavar='PATH',
                        help="the path to the lemma list")
    parser.add_argument('--weight', action='store_true',
                        help="lemmas has weights")
    parser.add_argument('--output', type=str, metavar='PATH',
                        help="the path to save the plausible pairs")
    args = parser.parse_args()

    # build paths
    text_path = os.path.abspath(args.text)
    lemmas_path = os.path.abspath(args.lemmas)
    output_path = os.path.abspath(args.output)
    output_dir = os.path.dirname(output_path)

    # read corpus
    corpus = []
    num_words_in_corpus = 0
    vocab = set()
    print("Reading corpus ... ", end='', flush=True)
    with open(text_path) as f:
        for line in f:
            l = [w.lower() for w in line.strip().split()]
            corpus.append(l)
            num_words_in_corpus += len(l)
            for w in l:
                vocab.add(w)
    print("Done. ({} lines, {} words, vocab size: {})".format(len(corpus), num_words_in_corpus, len(vocab)))

    # read lemmas
    lemmas = []
    lemma_weight = {}
    print("Reading lemmas ... ", end='', flush=True)
    with open(lemmas_path) as f:
        for line in f:
            row = line.strip().lower().split('\t')
            lemma = row[0]
            if args.weight:
                weight = row[1]
            else:
                weight = 1
            lemmas.append(lemma)
            lemma_weight[lemma] = weight
    print("Done. ({} lemmas)".format(len(lemmas)))

    # pair vocabs and lemmas
    pairs = 0
    plausible_lw_pairs = {}
    print("Pairing and filtering vocabs and lemmas ... ", end='', flush=True)
    for lemma in lemmas:
        plausible_lw_pairs[lemma] = set()
        for word in vocab:
            idx1, idx2, size = longestSubstring(lemma, word)
            if (float(size) / len(lemma) >= PLAUSIBLE_THRESHOLD):
                plausible_lw_pairs[lemma].add(word)
        pairs += len(plausible_lw_pairs[lemma])
    print("Done. ({} pairs)".format(pairs))

    # output
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    with open(output_path, 'w') as f_out:
        for lemma in plausible_lw_pairs:
            weight = lemma_weight[lemma]
            for word in plausible_lw_pairs[lemma]:
                f_out.write("{}\t{}\t{}\n".format(lemma, word, weight))
