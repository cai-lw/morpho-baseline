import os
import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="The lemma baseline which predicts all inflected forms "
                    "directly using the lemmas. The number of paradigm slots "
                    "is from the ground truth.")
    parser.add_argument('--lemmas', type=str, required=True, metavar='PATH',
                        help="the path to the lemma list file")
    parser.add_argument('--gold', type=str, required=True, metavar='PATH',
                        help="the path to the ground truth file")
    parser.add_argument('--output', type=str, required=True, metavar='PATH',
                        help="the path to save the predictions")
    args = parser.parse_args()

    # build paths
    lemmas_path = os.path.abspath(args.lemmas)
    gold_path = os.path.abspath(args.gold)
    output_path = os.path.abspath(args.output)
    output_dir = os.path.dirname(output_path)
    
    # predict and output
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    tags = set()
    with open(gold_path) as f_in:
        for line in f_in:
            lemma, word, tag = line.strip().split('\t')
            tags.add(tag)

    lemmas = []
    with open(lemmas_path) as f_in:
        for line in f_in:
            lemmas.append(line.strip())

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    with open(output_path, 'w') as f_out:
        for lemma in lemmas:
            for tag in tags:
                f_out.write("{}\t{}\t{}\n".format(lemma, lemma, tag))
