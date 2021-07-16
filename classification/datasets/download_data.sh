#!/bin/bash
# Copyright (c) Microsoft Corporation. Licensed under the MIT license.

REPO=$PWD
ORIGINAL_DIR="$REPO/Data/Original_Data"
PREPROCESS_DIR="$REPO/Data/Preprocess_Scripts"
PROCESSED_DIR="$REPO/Data/Processed_Data"

function download_nli_en_hi {
    OUTPATH=$ORIGINAL_DIR/NLI_EN_HI/temp
    mkdir -p $OUTPATH
    if [ ! -d $OUTPATH/all_keys_json ]; then
        if [ ! -f $OUTPATH/all_keys_json.zip ]; then
            wget -c https://www.cse.iitb.ac.in/~pjyothi/indiccorpora/all_keys_json.zip -P $OUTPATH -q --show-progress
        fi
        unzip -qq $OUTPATH/all_keys_json.zip -d $OUTPATH
    fi

    if [ ! -f $OUTPATH/all_only_id.json ]; then
        url=$'https://api.onedrive.com/v1.0/drives/85FEAFEE8D8062F3/items/85FEAFEE8D8062F3!28569?select=id%2C%40content.downloadUrl&authkey=!ADungCV7vUzIE_g'
        wget $url -q -O - | python -c "import json, sys; j=json.load(sys.stdin); print(j['@content.downloadUrl'])" | wget -i - -O $OUTPATH/all_only_id.json -q --show-progress
    fi

    python $PREPROCESS_DIR/preprocess_nli_en_hi.py --data_dir $ORIGINAL_DIR --output_dir $PROCESSED_DIR

    #rm -rf $OUTPATH
    echo "Downloaded NLI EN HI"
}

function download_sentiment_en_hi {
    OUTPATH=$ORIGINAL_DIR/Sentiment_EN_HI/temp
    mkdir -p $OUTPATH
    if [ ! -d $OUTPATH/SAIL_2017 ]; then
      if [ ! -f $OUTPATH/SAIL_2017.zip ]; then
        wget -c http://amitavadas.com/SAIL/Data/SAIL_2017.zip -P $OUTPATH -q --show-progress
      fi
      unzip -qq $OUTPATH/SAIL_2017.zip -d $OUTPATH
    fi

    python $PREPROCESS_DIR/preprocess_sent_en_hi.py --data_dir $ORIGINAL_DIR --output_dir $PROCESSED_DIR

    # rm -rf $OUTPATH 
    echo "Downloaded Sentiment EN HI"
}


download_nli_en_hi
download_sentiment_en_hi
