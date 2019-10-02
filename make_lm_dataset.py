import sys
import os
import random
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument('--test_lines', type=int, default=1000)
parser.add_argument('--input_file', default='data/English.txt')
parser.add_argument('--output_dir', default='data/english_chars')
args = parser.parse_args()


def line_gen():
    with open(args.input_file, encoding='utf8') as f:
        for line in f:
            new_line = ''
            for char in line.strip().lower():
                if new_line:
                    new_line += ' '
                new_line += '_' if char == ' ' else char
            yield new_line

os.makedirs(args.output_dir, exist_ok=True)
lines = line_gen()
with open(os.path.join(args.output_dir, 'test.txt'), 'w', encoding='utf8') as f:
    for _, line in zip(range(1000), lines):
        print(line, file=f)
with open(os.path.join(args.output_dir, 'valid.txt'), 'w', encoding='utf8') as f:
    for _, line in zip(range(1000), lines):
        print(line, file=f)
with open(os.path.join(args.output_dir, 'train.txt'), 'w', encoding='utf8') as f:
    for line in lines:
        print(line, file=f)
