import os
import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--uzh-train', type=str, metavar='PATH',
                        help="the path to the uzh training data")
    parser.add_argument('--uzh-dev', type=str, metavar='PATH',
                        help="the path to the uzh dev data")
    parser.add_argument('--uzh-test', type=str, metavar='PATH',
                        help="the path to the uzh test data")
    parser.add_argument('--conll17-output-dir', type=str, metavar='PATH',
                        help="the dir to save the conll 17 data")
    args = parser.parse_args()

    # build paths
    uzh_train_path = os.path.abspath(args.uzh_train)
    uzh_dev_path = os.path.abspath(args.uzh_dev)
    uzh_test_path = os.path.abspath(args.uzh_test)
    conll17_output_dir = os.path.abspath(args.conll17_output_dir)
    conll17_output_dir = os.path.join(conll17_output_dir, 'task2')

    train_samples = []
    test_samples = []

    with open(uzh_train_path) as f:
        for line in f:
            l, w, t = line.strip().split('\t')
            train_samples.append((l, w, t))

    with open(uzh_dev_path) as f:
        for line in f:
            l, w, t = line.strip().split('\t')
            train_samples.append((l, w, t))

    with open(uzh_test_path) as f:
        for line in f:
            l, w, t = line.strip().split('\t')
            test_samples.append((l, w, t))

    # output
    if not os.path.exists(conll17_output_dir):
        os.makedirs(conll17_output_dir)
    with open(os.path.join(conll17_output_dir, 'conll17-train-low'), 'w') as f:
        for l, w, t in train_samples:
            f.write('{}\t{}\t{}\n'.format(l, w, t))
    with open(os.path.join(conll17_output_dir, 'conll17-covered-dev'), 'w') as f:
        for l, w, t in test_samples:
            f.write('{}\t{}\t{}\n'.format(l, w, t))
    with open(os.path.join(conll17_output_dir, 'conll17-uncovered-dev'), 'w') as f:
        for l, w, t in test_samples:
            f.write('{}\t{}\t{}\n'.format(l, '<unk>', t))
