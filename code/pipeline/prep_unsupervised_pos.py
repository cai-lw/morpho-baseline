import os
import sys
import argparse
import subprocess


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--text', type=str, required=True, metavar='PATH')
    parser.add_argument('--tmp-text', type=str, required=True, metavar='PATH')
    parser.add_argument('--tmp-ans', type=str, required=True, metavar='PATH')
    args = parser.parse_args()

    # build paths
    text_path = os.path.abspath(args.text)
    tmp_text_path = os.path.abspath(args.tmp_text)
    tmp_answer_path = os.path.abspath(args.tmp_ans)
    if not os.path.exists(os.path.dirname(tmp_text_path)):
        os.makedirs(os.path.dirname(tmp_text_path))
    if not os.path.exists(os.path.dirname(tmp_answer_path)):
        os.makedirs(os.path.dirname(tmp_answer_path))

    # lower corpus and make pseudo answer
    with open(text_path) as f_in:
        with open(tmp_text_path, 'w') as f_out_text:
            with open(tmp_answer_path, 'w') as f_out_ans:
                for line in f_in:
                    line = line.lower().strip().split()
                    f_out_text.write(' '.join(line) + '\n')
                    pseudo_answers = [w+'__<label>__0' for w in line]
                    f_out_ans.write(' '.join(pseudo_answers) + '\n')
