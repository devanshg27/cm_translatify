# Translate and Classify

## Translation

### Data Preparation

To transliterate the datasets, use the scripts in `translation/preprocessing/`. They use the fork of csnli available [here](https://github.com/devanshg27/csnli). The transliterated versions of the datasets have also been provided in `translation/preprocessing/preprocessed_data/`.

Download and extract [IIT Bombay English-Hindi Corpus v3.0](https://www.cfilt.iitb.ac.in/~parallelcorp/iitb_en_hi_parallel/) to a directory. Also copy the transliterated datasets to the same directory. The final directory should look like this:

```
.
├── iitb_corpus
│   ├── dev_test
│   │   ├── dev.en
│   │   ├── dev.hi
│   │   ├── test.en
│   │   └── test.hi
│   └── parallel
│       ├── IITB.en-hi.en
│       └── IITB.en-hi.hi
├── mrinal_dhar.jsonl
└── phinc.jsonl
```

### Training

Install the dependencies using

```bash
conda env create --file environment.yml
conda activate cmtranslation2
```

Download mBART pre-trained checkpoint:

```bash
wget -c https://dl.fbaipublicfiles.com/fairseq/models/mbart/mbart.cc25.v2.tar.gz
```

Finally, to train the model:

```bash
bash train.sh <path to mbart.cc25.v2.tar.gz or mBART-hien temporary directory when training mBART-hien-cm> <temporary directory which will be created> <path to dataset directory>
```

The checkpoints are stored in the directory `<temporary directory>/checkpoint`.

### Evaluation

```bash
bash eval.sh <temporary directory> <path to best checkpoint>
bash eval_phinc.sh <temporary directory> <path to best checkpoint>
```

## Classification

We show our performance on the [GLUECoS benchmark](https://github.com/microsoft/GLUECoS). Our dataset parsing and training codes are also based on their codebase.

We provide the preprocessed data which can be used directly. To download and translate the datasets by yourself, run `datasets/download_data.sh`, `datasets/Data/Preprocess_Scripts/preprocess_{nli/sent}_en_hi_2.py`, `datasets/Data/Preprocess_Scripts/to_translate_{nli/sent}.py`, `datasets/Data/Preprocess_Scripts/translate_mbart.sh`, `datasets/Data/Preprocess_Scripts/after_translate_{nli/sent}.py` in order.

Install the dependencies for the classification models and run (after changing paths in the code) using:

```bash
conda env create --file environment.yml
conda activate cm_nli
python3 code_mixed_nli.py -n <experiment name> | tee training_log # to train and evaluate NLI
python3 code_mixed_sa.py -n <experiment name> | tee training_log # to train and evaluate Sentiment Analysis
```
