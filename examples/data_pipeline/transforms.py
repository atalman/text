from collections import OrderedDict
from typing import List

import torch
import torch.nn as nn
from torch import Tensor
from torchtext.vocab import vocab


class PretrainedSPVocab(nn.Module):
    r"""Vocab based on a pretained sentencepiece model"""

    def __init__(self, sp_model):
        super(PretrainedSPVocab, self).__init__()
        self.sp_model = sp_model
        unk_id = self.sp_model.unk_id()
        unk_token = self.sp_model.IdToPiece(unk_id)
        vocab_list = [self.sp_model.IdToPiece(i) for i in range(self.sp_model.GetPieceSize())]
        self.vocab = vocab(OrderedDict([(token, 1) for token in vocab_list]), unk_token=unk_token)

    def forward(self, tokens: List[str]) -> List[int]:
        return self.vocab.lookup_indices(tokens)

    def insert_token(self, token: str, index: int) -> None:
        self.vocab.insert_token(token, index)


class PyTextVocabTransform(nn.Module):
    r"""PyTextVocabTransform transform"""

    def __init__(self, vocab):
        super(PyTextVocabTransform, self).__init__()
        self.vocab = vocab

    def forward(self, tokens_list: List[List[str]]) -> List[List[int]]:
        ids: List[List[int]] = self.vocab.lookup_all(tokens_list)
        return ids


class PyTextScriptVocabTransform(nn.Module):
    r"""PyTextScriptVocabTransform transform"""

    def __init__(self, vocab):
        super(PyTextScriptVocabTransform, self).__init__()
        self.vocab = vocab

    def forward(self, tokens: List[str]) -> List[int]:
        return self.vocab.lookup_indices_1d(tokens)


class ToLongTensor(nn.Module):
    r"""Convert a list of integers to long tensor"""

    def __init__(self):
        super(ToLongTensor, self).__init__()

    def forward(self, tokens: List[List[int]]) -> Tensor:
        return torch.tensor(tokens).to(torch.long)


def iterate_batch(pipeline):
    def func(data_batch):
        return [pipeline(data) for data in data_batch]

    return func


def vocab_func(vocab):
    def func(tokens_list_iter):
        return [vocab[tok] for tokens_list in tokens_list_iter for tok in tokens_list]

    return func


def vector_func(vector):
    def func(tokens_list_iter):
        return [vector.get_vecs_by_tokens(tokens_list) for tokens_list in tokens_list_iter]

    return func


def tokenizer_func(tokenizer):
    def func(lines):
        return [tokenizer(line) for line in lines]

    return func


class TextClassificationPipeline(nn.Module):
    r"""Text classification pipeline template"""

    def __init__(self, label_transform, text_transform):
        super(TextClassificationPipeline, self).__init__()
        self.label_transform = label_transform
        self.text_transform = text_transform

    def forward(self, label_text_tuple):
        return self.label_transform(label_text_tuple[0]), self.text_transform(label_text_tuple[1])
