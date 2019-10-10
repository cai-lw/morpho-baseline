import os
import random
from collections import Counter
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument('--test_lines', type=int, default=1000)
parser.add_argument('--input_file', default='data/English.txt')
parser.add_argument('--output_dir', default='data/english_chars')
parser.add_argument('--per_word', action='store_true')
parser.add_argument('--min_word_len', type=int, default=3)
parser.add_argument('--max_word_freq', type=float, default=0.01)
args = parser.parse_args()


def get_lines():
    lines = []
    with open(args.input_file, encoding='utf8') as f:
        for line in f:
            new_line = ''
            for char in line.strip().lower():
                if new_line:
                    new_line += ' '
                new_line += '_' if char == ' ' else char
            if new_line:
                lines.append(new_line)
    print('Get {} lines.'.format(len(lines)))
    return lines


def get_lines_of_words():
    lines = []
    with open(args.input_file, encoding='utf8') as f:
        for line in f:
            # Should use a tokenizer here.
            for word in line.strip().lower().split(' '):
                word = ''.join(c for c in word if c.isalnum())
                if len(word) < args.min_word_len:
                    continue
                lines.append(' '.join(word))
    counter = Counter(lines)
    print('Get {} tokens ({} distinct).'.format(len(lines), len(counter)))
    stop_words = frozenset(k for k, v in counter.items() if v > len(lines) * args.max_word_freq)
    lines = [l for l in lines if l not in stop_words]
    random.shuffle(lines)
    print('Filtered {} frequent words. Kept {} tokens.'.format(len(stop_words), len(lines)))
    return lines

os.makedirs(args.output_dir, exist_ok=True)
if args.per_word:
    lines = get_lines_of_words()
else:
    lines = get_lines()
with open(os.path.join(args.output_dir, 'test.txt'), 'w', encoding='utf8') as f:
    for line in lines[:args.test_lines]:
        print(line, file=f)
with open(os.path.join(args.output_dir, 'valid.txt'), 'w', encoding='utf8') as f:
    for line in lines[args.test_lines:2 * args.test_lines]:
        print(line, file=f)
with open(os.path.join(args.output_dir, 'train.txt'), 'w', encoding='utf8') as f:
    for line in lines[2 * args.test_lines:]:
        print(line, file=f)
