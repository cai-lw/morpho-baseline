import sys
sys.path.insert(0, './awd-lstm-lm')
import torch
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt

# Load model and vocab
model = torch.load('lm_output/english_chars.pt')[0]
model.eval()
vocab = torch.load('lm_output/corpus.0caf3e0f533ed61e968b41afe028b2f5.data').dictionary

# Get LM embedding of text
text = 'And God said, Let there be light: and there was light.'
processed_text = text.lower().replace(' ', '_')
x = torch.LongTensor([vocab.word2idx[c] for c in processed_text]).unsqueeze(1).cuda()
out, hidden = model(x, model.init_hidden(1))

# Visualization
labels = [text[i-5:i] + '[' + text[i] + ']' + text[i+1:i+6] for i in range(len(text))]
tsne = TSNE().fit_transform(out.detach().cpu().numpy())
color = torch.linspace(0, 1, len(text)).numpy()
plt.scatter(tsne[:, 0], tsne[:, 1], c=color, cmap=plt.get_cmap('viridis'))
for i in range(len(text)):
    plt.annotate(labels[i], (tsne[i, 0], tsne[i, 1]), fontsize='xx-small')
plt.show()
