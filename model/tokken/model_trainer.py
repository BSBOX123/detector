# E:\workspace\model\tokken\model_trainer.py

import pandas as pd
from konlpy.tag import Okt
from sklearn.feature_extraction.text import TfidfVectorizer
import os
import pickle

# --- 설정 ---
# 이 파일(model_trainer.py)이 있는 디렉토리 경로
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 학습에 사용할 CSV 파일의 전체 경로 
CSV_FILE_PATH = r'E:\workspace\News_API\articles\dataset_2025-09-28_16-07-47.csv' 

# 분석할 텍스트가 담긴 열(column)의 이름
TEXT_COLUMN_NAME = '기사본문'
# 진위여부 라벨이 담긴 열(column)의 이름 (1:진짜, 0:가짜)
LABEL_COLUMN_NAME = '진위여부(1:진짜, 0:가짜)' 
# 학습된 가중치를 저장할 파일명 (tokken 폴더 안에 저장)
OUTPUT_WEIGHTS_FILE = os.path.join(BASE_DIR, 'fake_news_keyword_weights.pkl')
# 추출할 상위 키워드 개수
TOP_N_KEYWORDS = 100

# --- 텍스트 전처리 및 토큰화 함수 ---
okt = Okt()
def preprocess_and_extract_nouns(text):
    if not isinstance(text, str):
        return []
    nouns = okt.nouns(text)
    return [noun for noun in nouns if len(noun) > 1]

def train_and_save_weights():
    """
    CSV 데이터를 로드하여 TF-IDF 모델학습,
    가짜뉴스 키워드 가중치를 파일로 저장.
    """
    print(f"--- 1. 학습 데이터 로드: '{CSV_FILE_PATH}' ---")
    if not os.path.exists(CSV_FILE_PATH):
        print(f"[오류] 파일을 찾을 수 없습니다: {CSV_FILE_PATH}")
        return

    try:
        df = pd.read_csv(CSV_FILE_PATH, encoding='utf-8-sig')
        print(f"총 {len(df)}개의 기사 데이터 로드 완료.")
    except Exception as e:
        print(f"[오류] CSV 파일 로드 실패: {e}")
        return

    # 필수 컬럼 확인
    if TEXT_COLUMN_NAME not in df.columns or LABEL_COLUMN_NAME not in df.columns:
        print(f"[오류] 필요한 컬럼('{TEXT_COLUMN_NAME}', '{LABEL_COLUMN_NAME}')이 없습니다.")
        return

    print("\n--- 2. TF-IDF 기반 가짜뉴스 키워드 가중치 학습 시작 ---")
    
    fake_news_df = df[df[LABEL_COLUMN_NAME] == 0].copy() # 0이 가짜 뉴스 라벨
    if fake_news_df.empty:
        print("[경고] 가짜 뉴스 데이터가 없어 학습을 진행할 수 없습니다.")
        return

    fake_news_corpus = [" ".join(preprocess_and_extract_nouns(str(text))) 
                        for text in fake_news_df[TEXT_COLUMN_NAME]]
    fake_news_corpus = [doc for doc in fake_news_corpus if doc.strip()]

    if not fake_news_corpus:
        print("[경고] 전처리 후 가짜 뉴스 데이터에 유효한 문서가 없습니다.")
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
    
    print(f"\n--- 3. 가중치 저장 완료 ({OUTPUT_WEIGHTS_FILE}) ---")
    print(f"총 {len(fake_news_weights)}개의 가짜뉴스 특징 키워드가 저장되었습니다.")

if __name__ == '__main__':
    train_and_save_weights()