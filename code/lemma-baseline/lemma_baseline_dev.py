import os
import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="The lemma baseline which predicts all inflected forms "
                    "directly using the lemmas. The number of paradigm slots "
                    "is the average number of slots of all (other) dev "
                    "languages.")
    parser.add_argument('--lemmas', type=str, required=True, metavar='PATH',
                        help="the path to the lemma list file")
    parser.add_argument('--dev-golds', nargs='+', required=True, metavar='PATH',
                        help="the paths to the gold file of dev languages")
    parser.add_argument('--output', type=str, required=True, metavar='PATH',
                        help="the path to save the predictions")
    args = parser.parse_args()

    # build paths
    lemmas_path = os.path.abspath(args.lemmas)
    dev_gold_paths = []
    for path in args.dev_golds:
        dev_gold_paths.append(os.path.abspath(path))
    output_path = os.path.abspath(args.output)
    output_dir = os.path.dirname(output_path)
    
    # count slots
    slots = 0.0
    for path in dev_gold_paths:
        tags = set()
        with open(path) as f:
            for line in f:
                l, w, t = line.strip().split('\t')
                tags.add(t)
        print(path, len(tags))
        slots += len(tags)
    slots /= len(dev_gold_paths)
    slots = int(slots + 0.5)

    # predict and output
    print("{} slots".format(slots))
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    with open(lemmas_path) as f_in:
        with open(output_path, 'w') as f_out:
            for line in f_in:
                lemma = line.strip()
                for i in range(slots):
                    f_out.write("{}\t{}\t{}\n".format(lemma, lemma, i))
