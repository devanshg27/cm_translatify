# -*- coding: utf-8 -*-
"""Code_Mixed_NLI

Automatically generated by Colaboratory.
"""

# coding=utf-8
# Copyright (c) Microsoft Corporation. Licensed under the MIT license.
# Copyright 2018 The Google AI Language Team Authors and The HuggingFace Inc. team.
# Copyright (c) 2018, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

DATA_PATH = '/home/devanshg27/nli_dataset/Data/Translated_Data/NLI_EN_HI/'
model_checkpoint = "ynie/albert-xxlarge-v2-snli_mnli_fever_anli_R1_R2_R3-nli"
BATCH_SIZE = 8
MAX_SEQ_LEN = 256

# Commented out IPython magic to ensure Python compatibility.
# %%capture
# !pip install transformers

import argparse

def parse_args():
    parser = argparse.ArgumentParser(description='Finetuning for NLI')
    parser.add_argument('-n', '--experiment_id', type=str, required=True)
    return parser.parse_args()

args = parse_args()
EXPERIMENT_ID = args.experiment_id
TESTING=False

import torch
import os
from transformers import AutoTokenizer
from transformers import AutoConfig
from transformers import AutoModelForSequenceClassification, AutoModel
from transformers import xnli_processors as processors
from transformers import xnli_output_modes as output_modes
from transformers import glue_convert_examples_to_features as convert_examples_to_features
from torch.utils.data import DataLoader, RandomSampler, SequentialSampler, TensorDataset
from transformers.data.processors.utils import InputExample
from tqdm.notebook import tqdm
from sklearn.metrics import f1_score, accuracy_score, precision_score, recall_score, confusion_matrix
from torch.nn import CrossEntropyLoss

os.environ["HF_HOME"]="/scratch/huggingface_cache/"
os.makedirs(f'/scratch/devanshg27/{EXPERIMENT_ID}')

from torch import cuda
device = 'cuda' if cuda.is_available() else 'cpu'

tokenizer = AutoTokenizer.from_pretrained(model_checkpoint)#, use_fast=True)

config = AutoConfig.from_pretrained(model_checkpoint)
config.num_labels = 2
# hack to change num_labels of pretrained model (save without classification head, and then add new classification head while loading)
model = AutoModel.from_pretrained(model_checkpoint)
model.save_pretrained(f'/scratch/devanshg27_temp_{EXPERIMENT_ID}')
model = AutoModelForSequenceClassification.from_pretrained(f'/scratch/devanshg27_temp_{EXPERIMENT_ID}', config=config)
if torch.cuda.device_count() > 1:
    print("Let's use", torch.cuda.device_count(), "GPUs!")
    # dim = 0 [30, xxx] -> [10, ...], [10, ...], [10, ...] on 3 GPUs
    model = torch.nn.DataParallel(model)

model = model.to(device)

class GLUECoSNLIProcessor(processors['xnli']):
    def get_labels(self):
        return ["contradiction", "entailment"]
    
    def get_valid_examples(self, data_dir):
        lg = self.language if self.train_language is None else self.train_language
        lines = self._read_tsv(os.path.join(data_dir, "XNLI-MT-1.0/multinli/multinli.valid.{}.tsv".format(lg)))
        examples = []
        for (i, line) in enumerate(lines):
            if i == 0:
                continue
            guid = "%s-%s" % ("valid", i)
            text_a = line[0]
            text_b = line[1]
            label = "contradiction" if line[2] == "contradictory" else line[2]
            assert isinstance(text_a, str), f"Validation input {text_a} is not a string"
            assert isinstance(text_b, str), f"Validation input {text_b} is not a string"
            assert isinstance(label, str), f"Validation label {label} is not a string"
            examples.append(InputExample(guid=guid, text_a=text_a, text_b=text_b, label=label))
        return examples

def load_and_cache_examples(tokenizer, mode):

    processor = GLUECoSNLIProcessor(language='en', train_language=None)
    output_mode = output_modes["xnli"]
    
    print(f"Creating features from dataset file at {DATA_PATH}")
    label_list = processor.get_labels()
    if mode == "train":
        examples = processor.get_train_examples(DATA_PATH)
    elif mode == "valid":
        examples = processor.get_valid_examples(DATA_PATH)
    elif mode == "test":
        examples = processor.get_test_examples(DATA_PATH)
    else:
        assert(False)
    features = convert_examples_to_features(
        examples, tokenizer, max_length=MAX_SEQ_LEN, label_list=label_list, output_mode=output_mode,
    )

    # Convert to Tensors and build dataset
    all_input_ids = torch.tensor([f.input_ids for f in features], dtype=torch.long)
    all_attention_mask = torch.tensor([f.attention_mask for f in features], dtype=torch.long)
    # all_token_type_ids = torch.tensor([f.token_type_ids for f in features], dtype=torch.long)
    if output_mode == "classification":
        all_labels = torch.tensor([f.label for f in features], dtype=torch.long)
    else:
        raise ValueError("No other `output_mode` for XNLI.")

    # dataset = TensorDataset(all_input_ids, all_attention_mask, all_token_type_ids, all_labels)
    dataset = TensorDataset(all_input_ids, all_attention_mask, all_labels)
    return dataset

train_dataset = load_and_cache_examples(tokenizer, "train")
train_sampler = RandomSampler(train_dataset)
train_dataloader = DataLoader(train_dataset, sampler=train_sampler, batch_size=BATCH_SIZE)

valid_dataset = load_and_cache_examples(tokenizer, "valid")
valid_sampler = SequentialSampler(valid_dataset)
valid_dataloader = DataLoader(valid_dataset, sampler=valid_sampler, batch_size=BATCH_SIZE)

test_dataset = load_and_cache_examples(tokenizer, "test")
test_sampler = SequentialSampler(test_dataset)
test_dataloader = DataLoader(test_dataset, sampler=test_sampler, batch_size=BATCH_SIZE)

def save_model(model, name, data):
    DIR = f'/scratch/devanshg27/{EXPERIMENT_ID}/'
    # model.save_pretrained(f'{DIR}/model_{name}')
    torch.save(model.module.state_dict(), f'{DIR}/model_{name}.pt')
    label_list = GLUECoSNLIProcessor(language="en", train_language=None).get_labels()
    with open(f'{DIR}/valid_{name}.txt', 'w') as f:
        pred_labels = [label_list[x] for x in data['valid_preds']]
        f.write('\n'.join(pred_labels))
    with open(f'{DIR}/test_{name}.txt', 'w') as f:
        pred_labels = [label_list[x] for x in data['test_preds']]
        f.write('\n'.join(pred_labels))
    print('Model stored!', flush=True)

class ScorePreds:
    def __init__(self, keep_model=False):
        self.best_metrics = [0]
        self.best_model_cnt = 0
        self.test_score = 0

    def update_best_score(self, model, metrics, preds):
        if metrics[0] <= self.best_metrics[0]:
            return
        print(f'Exceeded the past model with {self.best_metrics[0]} with a score of {metrics[0]}', flush=True)
        print(metrics, flush=True)
        test_preds, test_gt = validate(test_dataloader, fast=False)
        self.test_score = accuracy_score(test_gt, test_preds) * 100
        print(self.test_score)
        data = {
            'valid_preds': preds,
            'test_preds': test_preds,
        }
        save_model(model, f'nli_{self.best_model_cnt}', data)
        self.best_model_cnt += 1
        self.best_metrics = metrics

    def calc_score(self, model, preds, gt):
        assert len(preds) == len(gt)

        metrics = (
            # f1_score(gt, preds, average='micro', labels=labels),
            # f1_score(gt, preds, average='macro', labels=labels),
            accuracy_score(gt, preds) * 100,
            confusion_matrix(gt, preds),
        )

        self.update_best_score(model, metrics, preds)
        return metrics

main_scorer = ScorePreds(keep_model=False)

def validate(dataloader, fast=True):
    preds = []
    gt = []

    model.eval()
    with torch.no_grad():
        for (_, batch_data) in tqdm(enumerate(dataloader, 0), disable=True):
            batch = tuple(t.to(device) for t in batch_data)
            # inputs = {"input_ids": batch[0], "attention_mask": batch[1], "token_type_ids": batch[2], "labels": batch[3]}
            inputs = {"input_ids": batch[0], "attention_mask": batch[1], "labels": batch[2]}
            outputs = model(**inputs)

            temp = outputs.logits.cpu().detach().numpy().tolist()
            pred = [max(enumerate(x[:2]), key=lambda x: x[1])[0] for x in temp]
            preds.extend(pred)

            labels = inputs['labels']
            gt.extend([gt_label.item() for gt_label in labels])

            # if fast and _ > 20:
            #     break
    return preds, gt

optimizer = None

loss_fct = CrossEntropyLoss()
num_labels = len(GLUECoSNLIProcessor(language="en", train_language=None).get_labels())

def train(epochs=1, steps=0):
    if epochs == 0 and steps > 0:
        epochs = 1
    for epoch in range(epochs):
        model.train()
        for idx, batch_data in enumerate(train_dataloader):
            # get the inputs;
            batch = tuple(t.to(device) for t in batch_data)
            # inputs = {"input_ids": batch[0], "attention_mask": batch[1], "token_type_ids": batch[2], "labels": batch[3]}
            # inputs = {"input_ids": batch[0], "attention_mask": batch[1], "labels": batch[2]}
            inputs = {"input_ids": batch[0], "attention_mask": batch[1]}
            # zero the parameter gradients
            optimizer.zero_grad()

            # forward   backward   optimize
            outputs = model(**inputs)
            loss = loss_fct(outputs.logits.view(-1, 2), batch[2].view(-1))

            if idx%5 == 0:
                print(f"Epoch Step: {idx}, Loss:  {loss.item()}", flush=True)

            loss.backward()
            optimizer.step()

            if steps > 0 and idx >= steps:
                break
            if idx > 0 and idx%100 == 0:
                print(main_scorer.calc_score(model, *validate(valid_dataloader, fast=False)), flush=True)
                model.train()
    return epochs

optimizer = torch.optim.AdamW(model.parameters(), lr=1e-6)
TRAIN_EPOCHS = 5

print('\n\nTraining entire model...\n', flush=True)
for i in range(TRAIN_EPOCHS):
    train(1)
    print(f'Epochs = {i + 1}', flush=True)
    preds, gt = validate(valid_dataloader, fast=False)
    metrics = main_scorer.calc_score(model, preds, gt)
    print('VAL SET SCORE', metrics, flush=True)

print('TEST SCORE:', main_scorer.test_score)