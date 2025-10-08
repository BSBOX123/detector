# E:\workspace\model\media\media_judger.py

import pandas as pd
import os
import glob

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEIGHTS_FOLDER = os.path.join(BASE_DIR, 'weights_history')
AUTHOR_WEIGHTS_FILE = os.path.join(WEIGHTS_FOLDER, "author_weights.csv")
INITIAL_WEIGHTS_FILE = os.path.join(BASE_DIR, 'source_initial_weights.csv')

source_weights = None
author_weights = None
etc_source_score = 0.5

def _load_media_weights():
    global source_weights, author_weights, etc_source_score
    
    weight_files = glob.glob(os.path.join(WEIGHTS_FOLDER, 'weights_*.csv'))
    load_path = INITIAL_WEIGHTS_FILE
    if weight_files:
        latest_file = max(weight_files, key=os.path.getctime)
        if os.path.exists(latest_file):
            load_path = latest_file
            
    try:
        source_weights = pd.read_csv(load_path).set_index('source')
        if 'final_weight' not in source_weights.columns and 'initial_weight' in source_weights.columns:
             source_weights['final_weight'] = source_weights['initial_weight']
        if 'etc' in source_weights.index:
            etc_source_score = source_weights.loc['etc', 'final_weight']
        print(f"--- Media 가중치 로드 완료: {os.path.basename(load_path)} ---")
    except FileNotFoundError:
        print(f"[오류] 언론사 가중치 파일을 찾을 수 없습니다: {load_path}")
        source_weights = pd.DataFrame()

    if os.path.exists(AUTHOR_WEIGHTS_FILE):
        try:
            author_weights = pd.read_csv(AUTHOR_WEIGHTS_FILE).set_index('author')
            print(f"--- 기자 가중치 로드 완료: {os.path.basename(AUTHOR_WEIGHTS_FILE)} ---")
        except Exception:
             author_weights = pd.DataFrame()
    else:
        author_weights = pd.DataFrame()

def judge_media_score(source_name, author_name):
    if source_weights is None or author_weights is None:
        _load_media_weights()

    source_score = etc_source_score
    if not source_weights.empty and source_name in source_weights.index:
        source_score = source_weights.loc[source_name, 'final_weight']

    author_score = 0.5
    if not author_weights.empty and author_name in author_weights.index:
        author_score = author_weights.loc[author_name, 'credibility_score']
        
    final_media_score = (source_score + author_score) / 2 * 100

    return {
        "score": round(final_media_score, 2),
        "source_score": round(source_score, 4),
        "author_score": round(author_score, 4)
    }