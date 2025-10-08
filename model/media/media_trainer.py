# E:\workspace\model\media\media_trainer.py

import pandas as pd
import numpy as np
import os
import argparse
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 학습 데이터 CSV에 있는 컬럼명과 일치해야 합니다.
SOURCE_COLUMN_NAME = '출처'
AUTHOR_COLUMN_NAME = '기자'
LABEL_COLUMN_NAME = '진위여부(1:진짜, 0:가짜)'

INITIAL_WEIGHTS_FILE = os.path.join(BASE_DIR, "source_initial_weights.csv")
WEIGHTS_FOLDER = os.path.join(BASE_DIR, "weights_history")
AUTHOR_WEIGHTS_FILE = os.path.join(WEIGHTS_FOLDER, "author_weights.csv")

MIN_ARTICLES_SOURCE = 3
MIN_ARTICLES_AUTHOR = 3
ALPHA = 0.7 # 기본 알파값

def train(csv_file_path):
    print(f"--- [Media] 학습 데이터 로드: '{os.path.basename(csv_file_path)}' ---")
    if not os.path.exists(csv_file_path):
        print(f"파일을 찾을 수 없습니다: {csv_file_path}")
        return
        
    try:
        df = pd.read_csv(csv_file_path, encoding='utf-8-sig')
    except Exception as e:
        print(f"CSV 파일 로드 실패: {e}")
        return

    if not all(col in df.columns for col in [SOURCE_COLUMN_NAME, AUTHOR_COLUMN_NAME, LABEL_COLUMN_NAME]):
        print(f"필요한 컬럼('{SOURCE_COLUMN_NAME}', '{AUTHOR_COLUMN_NAME}', '{LABEL_COLUMN_NAME}')이 없습니다.")
        return

    print("--- [Media] 언론사/기자 신뢰도 가중치 학습 시작 ---")
    df['score'] = df[LABEL_COLUMN_NAME].apply(lambda x: 1 if x == 1 else -1)

    # 기자 신뢰도
    author_scores = df.groupby(AUTHOR_COLUMN_NAME).agg(
        article_count=('score', 'count'),
        avg_score=('score', 'mean')
    ).reset_index()
    author_scores = author_scores[author_scores[AUTHOR_COLUMN_NAME] != '[기자 정보 없음]']
    author_scores['credibility_score'] = (author_scores['avg_score'] + 1) / 2
    final_author_weights = author_scores[author_scores['article_count'] >= MIN_ARTICLES_AUTHOR]
    
    # 언론사 신뢰도
    try:
        initial_weights = pd.read_csv(INITIAL_WEIGHTS_FILE).set_index('source')
    except FileNotFoundError:
        print(f"초기 가중치 파일({INITIAL_WEIGHTS_FILE})을 찾을 수 없습니다.")
        return
        
    source_scores = df.groupby(SOURCE_COLUMN_NAME).agg(
        article_count=('score', 'count'),
        avg_score=('score', 'mean')
    ).reset_index()
    source_scores['observed_score'] = (source_scores['avg_score'] + 1) / 2
    
    df_merged = initial_weights.merge(source_scores, left_on='source', right_on=SOURCE_COLUMN_NAME, how='left')
    df_merged['article_count'] = df_merged['article_count'].fillna(0).astype(int)
    df_merged['observed_score'] = df_merged['observed_score'].fillna(df_merged['initial_weight'])
    
    df_merged['final_weight'] = np.where(
        df_merged['article_count'] >= MIN_ARTICLES_SOURCE,
        (df_merged['initial_weight'] * ALPHA) + (df_merged['observed_score'] * (1 - ALPHA)),
        df_merged['initial_weight']
    )
    final_source_weights = df_merged.set_index('source')
    
    # 결과 저장
    os.makedirs(WEIGHTS_FOLDER, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    source_output_filename = os.path.join(WEIGHTS_FOLDER, f'weights_{timestamp}.csv')
    
    final_source_weights[['initial_weight', 'final_weight', 'article_count']].to_csv(source_output_filename, encoding='utf-8-sig')
    print(f"--- [Media] 언론사 가중치 저장 완료: {os.path.basename(source_output_filename)} ---")
    
    if not final_author_weights.empty:
        final_author_weights.to_csv(AUTHOR_WEIGHTS_FILE, index=False, encoding='utf-8-sig')
        print(f"--- [Media] 기자 가중치 저장 완료: {os.path.basename(AUTHOR_WEIGHTS_FILE)} ---")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="[Media] 출처 신뢰도 모델을 학습합니다.")
    parser.add_argument('--file', type=str, required=True, help='학습에 사용할 CSV 파일의 전체 경로')
    args = parser.parse_args()
    train(args.file)