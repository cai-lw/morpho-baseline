import os
import pickle
import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--et', type=str, required=True, metavar='PATH',
                        help="the path to load the filtered edit trees")
    parser.add_argument('--lemmas', type=str, required=True, metavar='PATH',
                        help="the path to the lemma list")
    parser.add_argument('--output', type=str, required=True, metavar='PATH',
                        help="the path to save the predictions")
    args = parser.parse_args()

    # build paths
    et_path = os.path.abspath(args.et)
    lemmas_path = os.path.abspath(args.lemmas)
    output_path = os.path.abspath(args.output)
    output_dir = os.path.dirname(output_path)

    # read filtered edittrees
    with open(et_path, 'rb') as f:
        et_data = pickle.load(f)

    # read lemma
    lemmas = []
    with open(lemmas_path) as f:
        for line in f:
            lemmas.append(line.strip())

    # predict and output
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    with open(output_path, 'w') as f_out:
        for lemma in lemmas:
            for i, et_dict in enumerate(et_data):
                et = et_dict['et']
                inflected_word = et.apply(lemma)
                if inflected_word != -1:
                    f_out.write('{}\t{}\t{}\n'.format(lemma, inflected_word, i))
