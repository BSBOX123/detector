# E:\workspace\model\tokken\model_trainer.py

import pandas as pd
from konlpy.tag import Okt
from sklearn.feature_extraction.text import TfidfVectorizer
import os
import pickle
import argparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 학습 데이터 CSV에 있는 컬럼명과 일치해야 합니다.
TEXT_COLUMN_NAME = '기사본문'
LABEL_COLUMN_NAME = '진위여부(1:진짜, 0:가짜)'
OUTPUT_WEIGHTS_FILE = os.path.join(BASE_DIR, 'fake_news_keyword_weights.pkl')
TOP_N_KEYWORDS = 100

okt = Okt()
def preprocess_and_extract_nouns(text):
    if not isinstance(text, str): return []
    nouns = okt.nouns(text)
    return [noun for noun in nouns if len(noun) > 1]

def train(csv_file_path):
    print(f"--- [Tokken] 학습 데이터 로드: '{os.path.basename(csv_file_path)}' ---")
    if not os.path.exists(csv_file_path):
        print(f"파일을 찾을 수 없습니다: {csv_file_path}")
        return

    try:
        df = pd.read_csv(csv_file_path, encoding='utf-8-sig')
    except Exception as e:
        print(f"CSV 파일 로드 실패: {e}")
        return

    if TEXT_COLUMN_NAME not in df.columns or LABEL_COLUMN_NAME not in df.columns:
        print(f"필요한 컬럼('{TEXT_COLUMN_NAME}', '{LABEL_COLUMN_NAME}')이 없습니다.")
        return

    print("--- [Tokken] TF-IDF 가중치 학습 시작 ---")
    fake_news_df = df[df[LABEL_COLUMN_NAME] == 0].copy()
    if fake_news_df.empty:
        print("가짜 뉴스 데이터가 없어 학습을 진행할 수 없습니다.")
        return

    fake_news_corpus = [" ".join(preprocess_and_extract_nouns(str(text))) for text in fake_news_df[TEXT_COLUMN_NAME]]
    fake_news_corpus = [doc for doc in fake_news_corpus if doc.strip()]

    if not fake_news_corpus:
        print("전처리 후 유효한 문서가 없습니다.")
        return

    tfidf_vectorizer = TfidfVectorizer(min_df=2, ngram_range=(1, 2))
    tfidf_matrix = tfidf_vectorizer.fit_transform(fake_news_corpus)

    feature_names = tfidf_vectorizer.get_feature_names_out()
    word_scores = tfidf_matrix.sum(axis=0).tolist()[0]
    raw_weights = {word: score for word, score in zip(feature_names, word_scores) if score > 0.01}
    sorted_weights = sorted(raw_weights.items(), key=lambda x: x[1], reverse=True)
    fake_news_weights = {word: score for word, score in sorted_weights[:TOP_N_KEYWORDS]}

    with open(OUTPUT_WEIGHTS_FILE, 'wb') as f:
        pickle.dump(fake_news_weights, f)
    
    print(f"--- [Tokken] 가중치 저장 완료: {os.path.basename(OUTPUT_WEIGHTS_FILE)} ---")
    print(f"총 {len(fake_news_weights)}개의 특징 키워드가 저장되었습니다.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="[Tokken] 텍스트 분석 모델을 학습합니다.")
    parser.add_argument('--file', type=str, required=True, help='학습에 사용할 CSV 파일의 전체 경로')
    args = parser.parse_args()
    train(args.file)