from transformer import Transformer
from collections import defaultdict
import torch.utils.data as D
import torch
import numpy as np
import time
# <s> a b c </s> <tag1> <tag2> …\t<s> a b c d </s> #

class MorphData(D.Dataset):
    def __init__(self, filename):
        self.srcs = []
        self.tgts = []
        with open(filename, 'r') as f:
            for line in f.readlines():
                inputs, outputs = line.strip().split(',')
                inputs, outputs = f"<sos> {inputs} <eos>", f"<sos> {outputs} <eos>"
                self.srcs.append([src_dict[w] for w in inputs.split()])
                self.tgts.append([tgt_dict[w] for w in outputs.split()])

    def __len__(self):
        assert len(self.srcs) == len(self.tgts)
        return len(self.srcs)

    def __getitem__(self,idx):
        return (self.srcs[idx], self.tgts[idx])

class MorphDataloader(D.DataLoader):
    def __init__(self, dataset, **kwargs):
        super(MorphDataloader, self).__init__(
            dataset=dataset,
            collate_fn=self.collate_fn,
            **kwargs
        )
    
    def collate_fn(self, batches):
        srcs, tgts = list(zip(*batches))
        srcs_padded, src_mask = self.zero_pad_concat(srcs, src_dict['<pad>'])
        tgts_padded, _ = self.zero_pad_concat(tgts, tgt_dict['<pad>'])

        return srcs_padded, tgts_padded, src_mask
        
    def zero_pad_concat(self, sents, pad_idx):
        lengths = [len(sent) for sent in sents]
        max_len = max(lengths)
        bsz = len(lengths)
        # Tensor containing the (right) padded tokens
        tokens = torch.full((max_len, bsz), pad_idx).long()
        for i in range(bsz):
            tokens[:lengths[i], i] = torch.LongTensor(sents[i])
        # Mask such that mask[i, b] = 1 iff lengths[b] < i
        lengths = torch.LongTensor(lengths).view(1, -1)
        mask = torch.gt(torch.arange(max_len).view(-1, 1), lengths)

        return tokens, mask

def greedy(model, src_tokens, max_len=5, device=None):
    # Either decode on the model's device or specified device
    # (in which case move the model accordingly)
    if device is None:
        device = list(model.parameters())[0].device
    else:
        model = model.to(device)
    # Go into eval mode (e.g. disable dropout)
    # Encode source sentece
    src_tensor = torch.LongTensor(src_tokens).to(device).view(-1, 1)
    encodings = model.encode(src_tensor)
    # Initialize decoder state
    state = model.initial_state()
    # Start decoding
    out_tokens = [tgt_dict["<sos>"]]
    eos_token = tgt_dict["<eos>"]
    while out_tokens[-1] != eos_token and len(out_tokens) <= max_len:
        current_token = torch.LongTensor([out_tokens[-1]]).view(1, 1).to(device)
        # One step of the decoder
        log_p, state = model.decode_step(current_token, encodings, state)
        # Sample
        next_token = log_p.view(-1).argmax()
        # Add to the generated sentence
        out_tokens.append(next_token.item())
    # Return generated token (idxs) without <sos> and <eos>
    out_tokens = out_tokens[1:]
    if out_tokens[-1] == eos_token:
        out_tokens = out_tokens[:-1]
    return out_tokens

if __name__ == '__main__':
    src_dict = defaultdict(lambda: len(src_dict))
    tgt_dict = defaultdict(lambda: len(tgt_dict))
    pad_src = src_dict["<pad>"]
    sos_src = src_dict["<sos>"]
    eos_src = src_dict["<eos>"]
    unk_src = src_dict["<unk>"]

    pad_tgt = tgt_dict["<pad>"]
    sos_tgt = tgt_dict["<sos>"]
    eos_tgt = tgt_dict["<eos>"]
    unk_tgt = tgt_dict["<unk>"]

    train_dataset = MorphData("sample_dataset.txt")
    train_dataloader = MorphDataloader(train_dataset, batch_size=2)
    test_sents = []
    with open('test.txt', 'r') as f:
        for line in f.readlines():
            src = line.strip()
            src = f"<sos> {src} <eos>"
            test_sents.append([src_dict.get(w, unk_src) for w in src.split()])
    src_invert = {v:k for k, v in src_dict.items()}
    tgt_invert = {v:k for k, v in tgt_dict.items()}

    # training process
    lr = 1e-3 # learning rate
    model = Transformer(n_layers=1, embed_dim=32, hidden_dim=64, n_heads=8, vocab=(src_dict, tgt_dict), dropout=0., word_dropout=0.)
    # model = Seq2Seq(transformer, embedding_size=16)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr, betas=(0.9, 0.98))
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, 1000, gamma=0.5)
    for epoch in range(10000):
        model.train()
        total_loss = 0
        start_time = time.time()
        for batch, (src, tgt, src_mask) in enumerate(train_dataloader):
            optimizer.zero_grad()
            log_p = model(src, tgt[:-1], src_mask)
            nll = torch.nn.functional.nll_loss(
                # Log probabilities (flattened to (l*b) x V)
                log_p.view(-1, log_p.size(-1)),
                # Target tokens (we start from the 1st real token, ignoring <sos>)
                tgt[1:].view(-1),
                # Don't compute the nll of padding tokens
                ignore_index=tgt_dict["<pad>"],
                # Take the average
                reduction="mean",
            )
            nll.backward()
            # torch.nn.utils.clip_grad_norm_(model.parameters(), 0.5)
            optimizer.step()

            total_loss += nll.item()
            log_interval = 20
            if batch % log_interval == 0:
                cur_loss = total_loss
                elapsed = time.time() - start_time
                print('epoch {:3d} | '
                        'lr {:02.5f} | ms/batch {:5.2f} | '
                        'loss {:5.2f}'.format(
                        epoch, scheduler.get_lr()[0],
                        elapsed * 1000 / log_interval,
                        cur_loss))
                total_loss = 0
                start_time = time.time()
        scheduler.step()

        model.eval()
        decoded_sents = []
        with torch.no_grad():
            for sent in test_sents:
                decoded_sent = greedy(model, sent)
                decoded_sents.append([tgt_invert[idx] for idx in decoded_sent])
        print(decoded_sents)

