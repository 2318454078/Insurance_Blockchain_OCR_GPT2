
"""Tokenization classes for OpenAI GPT."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import json
from io import open
import sentencepiece as spm
import jieba

try:
    from functools import lru_cache
except ImportError:
    # Just a dummy decorator to get the checks to run on python2
    # because honestly I don't want to support a byte-level unicode BPE tokenizer on python 2 right now.
    def lru_cache():
        return lambda func: func

class GPT2Tokenizer(object):
    def __init__(self, vocab_file, model_file, max_len=None):
        self.max_len = max_len if max_len is not None else int(1e12)
        self.encoder = json.load(open(vocab_file))
        self.decoder = {v:k for k,v in self.encoder.items()}

        self.sp = spm.SentencePieceProcessor(model_file=model_file)
        self.translator = str.maketrans(" \n", "\u2582\u2583")

        self.eod_id = self.encoder['<eod>']

    @property
    def vocab_size(self):
        return len(self.encoder)

    def __len__(self):
        return len(self.encoder) + len(self.special_tokens)

    @property
    def eod(self):
        return self.eod_id

    def tokenize(self, text):
        """ Tokenize a string. """
        seg_list = [x.translate(self.translator) for x in jieba.cut(text, cut_all=False)]
        new_seg = " ".join(seg_list)
        return self.sp.encode(new_seg)

    def encode(self, text):
        res = self.tokenize(text)
        return res

    def decode(self, tokens):
        text = self.sp.decode(tokens)
        text = text.replace(' ', '').replace('\u2582', ' ').replace('\u2583', '\n')
        return text


#-----MODEL---------MODEL-----------MODEL-----------MODEL------------MODEL--------#
import math
import torch
import torch.nn as nn
import torch.nn.functional as F


class MLP(nn.Module):
    def __init__(self, embedding_size):
        super(MLP, self).__init__()
        self.dense_h_to_4h = nn.Linear(embedding_size, embedding_size*4)
        self.dense_4h_to_h = nn.Linear(embedding_size*4, embedding_size)
        self.act = nn.functional.gelu

    def forward(self, x):
        h = self.act(self.dense_h_to_4h(x))
        h2 = self.dense_4h_to_h(h)
        return h2

class Attention(nn.Module):
    def __init__(self, 
                embedding_size, 
                num_attention_heads,
                attention_dropout,
                residual_dropout):
        super(Attention, self).__init__()
        
        self.num_attention_heads = num_attention_heads
        self.size_per_head = embedding_size // num_attention_heads
        self.embedding_size = embedding_size

        self.query_key_value = nn.Linear(embedding_size, embedding_size * 3)
        self.attn_drop = nn.Dropout(attention_dropout)
        self.resid_drop = nn.Dropout(residual_dropout)
        self.dense = nn.Linear(embedding_size, embedding_size)

    def split_heads(self, x):
        x = x.reshape([-1, self.seq_len, self.num_attention_heads, self.size_per_head])
        return x.permute(0, 2, 1, 3)

    def forward(self, x, kv_cache=None):
        self.seq_len = x.shape[1]
        x = self.query_key_value(x)
        q, k, v = torch.split(x, split_size_or_sections=self.embedding_size, dim=2)
        
        q = self.split_heads(q)
        k = self.split_heads(k)
        v = self.split_heads(v)
        
        if kv_cache is not None:
            pk, pv = kv_cache[0], kv_cache[1]
            k = torch.cat([pk, k], dim=-2)
            v = torch.cat([pv, v], dim=-2)

        cached_kv = torch.stack([k, v])

        attn = torch.matmul(q, k.transpose(-1, -2))  # [B, N, L, S]
        attn = attn / math.sqrt(self.size_per_head)

        # [L, S]
        attention_mask = torch.tril(torch.ones(self.seq_len, self.seq_len, dtype=torch.float32, device=x.device))
        attention_mask = attention_mask.reshape([1, 1, self.seq_len, self.seq_len])

        # adding to softmax -> its like removing them entirely
        attn = attn * attention_mask - 10000.0 * (1.0 - attention_mask)
        attn = nn.Softmax(dim=-1)(attn)
        attn = self.attn_drop(attn)

        y = torch.matmul(attn, v)
        # [B, N, L, S] -> [B, L, N, S]
        y = y.permute(0, 2, 1, 3)
        y = torch.reshape(y, [-1, self.seq_len, self.embedding_size])
        y = self.resid_drop(self.dense(y))

        return y, cached_kv

class Block(nn.Module):
    def __init__(self, 
                embedding_size, 
                num_attention_heads,
                attention_dropout,
                residual_dropout):
        super(Block, self).__init__()
        self.input_layernorm = nn.LayerNorm(embedding_size, eps=1e-5)
        self.attention = Attention(embedding_size, num_attention_heads, attention_dropout, residual_dropout)
        self.post_attention_layernorm = nn.LayerNorm(embedding_size, eps=1e-5)
        self.mlp = MLP(embedding_size)

    def forward(self, x, kv_cache=None):
        attn, cached_kv = self.attention(self.input_layernorm(x), kv_cache=kv_cache)
        x = x + attn
        z = self.post_attention_layernorm(x)
        z = self.mlp(z)
        x = x + z
        return x, cached_kv

class Transformer(nn.Module):
    def __init__(self, 
                layer_size,
                embedding_size, 
                num_attention_heads,
                attention_dropout,
                residual_dropout):
        super(Transformer, self).__init__()

        self.layers = nn.ModuleList([Block(
                embedding_size, 
                num_attention_heads,
                attention_dropout,
                residual_dropout) 
            for _ in range(layer_size)])

        self.final_layernorm = nn.LayerNorm(embedding_size, eps=1e-5)
    
    def forward(self, x, kv_cache=None):
        cached_kvs = []
        for i, layer in enumerate(self.layers):
            x, cached_kv = layer(
                x, 
                kv_cache=kv_cache[i] if kv_cache is not None else None)
            cached_kvs.append(cached_kv)
        x = self.final_layernorm(x)
        return x, torch.stack(cached_kvs)


class GPT2Model(nn.Module):
    def __init__(self,
                 vocab_size,
                 layer_size,
                 block_size,
                 embedding_dropout,
                 embedding_size,
                 num_attention_heads,
                 attention_dropout,
                 residual_dropout):
        super(GPT2Model, self).__init__()
        
        self.word_embeddings = nn.Embedding(vocab_size, embedding_size)
        self.position_embeddings = nn.Embedding(block_size, embedding_size)
        self.emb_drop = nn.Dropout(embedding_dropout)
        self.transformer = Transformer(
            layer_size,
            embedding_size, 
            num_attention_heads,
            attention_dropout,
            residual_dropout)

    def forward(self, x, kv_cache=None, use_cache=False):
        # position_ids 和外面计算的一样，
        if kv_cache is None:
            past_length = 0
        else:
            past_length = kv_cache[0][0].shape[-2]

        position_ids = torch.arange(past_length, x.shape[-1] + past_length, dtype=torch.int64, device=x.device)
        position_ids = position_ids.unsqueeze(0).expand_as(x)
        
        x = self.word_embeddings(x)  # input ids
        x = self.emb_drop(x + self.position_embeddings(position_ids))  # position
        
        x, cached_kvs = self.transformer(x, kv_cache)  # kv_cache 是 attention mask
        x = torch.matmul(x, self.word_embeddings.weight.transpose(-1, -2))
        if use_cache:
            return x, cached_kvs
        return x

import re
import numpy as np

def sample(model, tokenizer, text, max_len=10):
    ids = tokenizer.encode(text)
    input_id = torch.from_numpy(np.array(ids).reshape(1, -1)).long()
    output, cached_kvs = model(input_id, use_cache=True)
    nid = int(np.argmax(output[0, -1].detach().cpu().numpy()))
    ids += [nid]
    out = [nid]
    for i in range(max_len):
        input_id = torch.from_numpy(np.array([nid]).reshape(1, -1)).long()
        output, cached_kvs = model(input_id, cached_kvs, use_cache=True)
        nid = int(np.argmax(output[0, -1].detach().cpu().numpy()))
        ids += [nid]
        if nid==3:
            break
        out.append(nid)
    return (tokenizer.decode(out))

def similarity(nextstr, reslist):
    '''
        如果下一个字符串与之前的60%以上重复则不选取
    '''
    res = 0
    for stri in reslist:
        num = 0
        for i in nextstr:
            if i in stri:
                num = num + 1
        if num/len(nextstr) > 0.6:
            res = 1
    return res

def ask_question(model, tokenizer, question, max_len=10):
    '''
        正则去标点符号，去重后拼接句子
    '''
    # res = sample('''问题：%s 答案：''' % question, max_len)
    res = sample(model, tokenizer,
                    '''
                    问题：%s
                    答案：''' % question, max_len)
    res = re.findall(r"[\w']+", res)
    reslist = [res[0]] if len(res[0]) > 1 else []
    for i in range(0,len(res)-1):
        if len(res[i+1]) < 2:
            continue
        if similarity(res[i+1], reslist) == 0:
            reslist.append(res[i+1])
    res = ','.join(reslist)+'。'
    return res if len(res) > 1 else '对不起，我不知道。'