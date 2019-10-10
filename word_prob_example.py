import sys
sys.path.insert(0, './awd-lstm-lm')
import warnings
import torch
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt

# Load model and vocab
model, criterion, _ = torch.load('lm_output/english_chars_words.pt')
model.eval()
vocab = torch.load('lm_output/corpus.4d38d648f24f1b871c7b1e3184fa7099.data').dictionary

# Get LM embedding of text
while True:
    text = input('Input a word:')
    chars = [c for c in text if c.isalnum()]
    print('Processed word: {}'.format(''.join(chars)))
    x = torch.LongTensor([vocab.word2idx[c] for c in ['<eos>'] + chars]).unsqueeze(1).cuda()
    y = torch.LongTensor([vocab.word2idx[c] for c in chars + ['<eos>']]).unsqueeze(1).cuda()
    out, hidden = model(x, model.init_hidden(1))
    loss = criterion(model.decoder.weight, model.decoder.bias, out, y)
    print('Per-character average NLL: {:.4f}'.format(loss))
