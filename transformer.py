import torch
import torch.nn as nn
from collections import defaultdict
import torch.utils.data as D
import numpy as np

import time
# <s> a b c </s> <tag1> <tag2> …\t<s> a b c d </s> #
src_dict = defaultdict(lambda: len(src_dict))
tgt_dict = defaultdict(lambda: len(tgt_dict))
pad_src = src_dict["<pad>"]
unk_src = src_dict["<unk>"]
sos_src = src_dict["<s>"]
eos_src = src_dict["</s>"]

pad_tgt = tgt_dict["<pad>"]
unk_tgt = tgt_dict["<unk>"]
sos_tgt = tgt_dict["<s>"]
eos_tgt = tgt_dict["</s>"]

class MorphData(D.Dataset):
    def __init__(self, filename):
        self.srcs = []
        self.tgts = []
        with open(filename, 'r') as f:
            for line in f.readlines():
                inputs, outputs = line.strip().split(',')
                self.srcs.append([src_dict[w] for w in inputs.split()])
                self.tgts.append([tgt_dict[w] for w in outputs.split()])

    def __len__(self):
        assert len(self.srcs) == len(self.tgts)
        return len(self.srcs)

    def __getitem__(self,idx):
        return (self.srcs[idx], self.tgts[idx])

class MorphDataloader(D.DataLoader):
    def __init__(self, dataset, left_padding=False, **kwargs):
        super(MorphDataloader, self).__init__(
            dataset=dataset,
            collate_fn=self.collate_fn,
            **kwargs
        )
    
    def collate_fn(self, batches):
        srcs, tgts = list(zip(*batches))
        srcs_padded = self.zero_pad_concat(srcs, src_dict['<pad>'])
        tgts_padded = self.zero_pad_concat(tgts, tgt_dict['<pad>'])
        return (torch.from_numpy(srcs_padded).long(), torch.from_numpy(tgts_padded).long())
        
    def zero_pad_concat(self, inputs, pad_value, left_padding=False):
        max_t = max(len(inp) for inp in inputs)
        shape = (len(inputs), max_t)
        input_mat = np.full(shape, pad_value, dtype=np.int64)
        if left_padding:
            for e, inp in enumerate(inputs):
                input_mat[e, -len(inp):] = inp
        else:
            for e, inp in enumerate(inputs):
                input_mat[e, :len(inp)] = inp
        return input_mat

class Seq2Seq(nn.Module):
    def __init__(self, model, embedding_size):
        super(Seq2Seq, self).__init__()
        self.model = model
        self.embedding_size = embedding_size
        self.src_lookup = nn.Embedding(len(src_dict), embedding_size, padding_idx=src_dict['<pad>'])
        self.tgt_lookup = nn.Embedding(len(tgt_dict), embedding_size, padding_idx=tgt_dict['<pad>'])
        self.pred_layer = nn.Linear(self.embedding_size, len(tgt_dict))

    def forward(self, src, tgt):
        src_embedding = self.src_lookup(src)
        tgt_embedding = self.tgt_lookup(tgt)
        outputs = self.model(src_embedding.transpose(0,1), tgt_embedding.transpose(0,1))
        logits = self.pred_layer(outputs)
        return logits


if __name__ == '__main__':
    dataset = MorphData("sample_dataset.txt")
    dataloader = MorphDataloader(dataset, batch_size=2)
    criterion = nn.CrossEntropyLoss()
    lr = 5.0 # learning rate
    transformer = nn.Transformer(d_model=16, nhead=4, num_encoder_layers=4, dim_feedforward=32, dropout=0.1)
    model = Seq2Seq(transformer, embedding_size=16)
    optimizer = torch.optim.SGD(model.parameters(), lr=lr)
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, 1.0, gamma=0.95)
    for epoch in range(10):
        model.train()
        total_loss = 0
        start_time = time.time()
        for batch, (src, tgt) in enumerate(dataloader):
            optimizer.zero_grad()
            output = model(src, tgt).transpose(0, 1)
            loss = criterion(output.reshape(-1, len(tgt_dict)), tgt.view(-1))
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 0.5)
            optimizer.step()

            total_loss += loss.item()
            log_interval = 20
            if batch % log_interval == 0:
                cur_loss = total_loss / log_interval
                elapsed = time.time() - start_time
                print('epoch {:3d} | '
                        'lr {:02.2f} | ms/batch {:5.2f} | '
                        'loss {:5.2f}'.format(
                        epoch, scheduler.get_lr()[0],
                        elapsed * 1000 / log_interval,
                        cur_loss))
                total_loss = 0
                start_time = time.time()