# E:\workspace\model\tokken\model_trainer.py

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import os
import pickle
import argparse
import sys

# --- (핵심 수정 1) ---
# 이 파일이 모듈(-m)로 실행되므로, 현재 폴더(tokken)를 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# tokenizer.py 파일에서 okt_tokenizer 함수를 가져옵니다.
from tokenizer import okt_tokenizer 

# --- 설정 ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_MODEL_FILE = os.path.join(BASE_DIR, 'tokken_model_pipeline.pkl')
TEXT_COLUMN_NAME = '기사본문'
LABEL_COLUMN_NAME = '진위여부(1:진짜, 0:가짜)'

def train(csv_file_path):
    """
    주어진 CSV 데이터를 로드하여 TF-IDF + 로지스틱 회귀 모델을 학습하고,
    모델 파이프라인 전체를 .pkl 파일로 저장합니다.
    """
    print(f"--- [Tokken 2.0] 학습 데이터 로드: '{os.path.basename(csv_file_path)}' ---")
    if not os.path.exists(csv_file_path):
        print(f"[오류] 파일을 찾을 수 없습니다: {csv_file_path}")
        return

    try:
        df = pd.read_csv(csv_file_path, encoding='utf-8-sig')
        df.dropna(subset=[TEXT_COLUMN_NAME, LABEL_COLUMN_NAME], inplace=True)
        print(f"총 {len(df)}개의 (진짜/가짜) 기사 데이터 로드 완료.")
    except Exception as e:
        print(f"[오류] CSV 파일 로드 실패: {e}")
        return

    if TEXT_COLUMN_NAME not in df.columns or LABEL_COLUMN_NAME not in df.columns:
        print(f"[오류] 필요한 컬럼('{TEXT_COLUMN_NAME}', '{LABEL_COLUMN_NAME}')이 없습니다.")
        return
    
    if len(df) < 10:
        print(f"[오류] 데이터가 10개 미만({len(df)}개)입니다. 학습을 진행할 수 없습니다.")
        return
        
    X = df[TEXT_COLUMN_NAME]
    y = df[LABEL_COLUMN_NAME]
    
    # 90:10 비율로 분할 (test_size=0.1)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.1, random_state=42, stratify=y
    )
    print(f"데이터 분리 완료: 학습용 {len(X_train)}개 (90%), 평가용 {len(X_test)}개 (10%)")

    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(
            tokenizer=okt_tokenizer, 
            min_df=5,
            max_features=10000,
            ngram_range=(1, 2)
        )),
        ('clf', LogisticRegression(
            random_state=42,
            solver='liblinear',
            class_weight='balanced'
        ))
    ])

    print("\n--- [Tokken 2.0] 모델 학습 시작 (TF-IDF + 로지스틱 회귀) ---")
    pipeline.fit(X_train, y_train)
    print("모델 학습 완료.")

    y_pred = pipeline.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_pred, average='binary', pos_label=0, zero_division=0) 
    
    print(f"\n--- [Tokken 2.0] 모델 성능 평가 (Test Set 10% 기준) ---")
    print(f"  > 전체 정확도 (Accuracy): {accuracy * 100:.2f}%")
    print(f"  --- '가짜 뉴스(0)' 판별 성능 ---")
    print(f"  > 정밀도 (Precision): {precision * 100:.2f}%")
    print(f"  > 재현율 (Recall): {recall * 100:.2f}%")
    print(f"  > F1-점수 (F1-Score): {f1 * 100:.2f}%")

    with open(OUTPUT_MODEL_FILE, 'wb') as f:
        pickle.dump(pipeline, f)
    
    print(f"\n--- [Tokken 2.0] 학습된 모델 저장 완료 ---")
    print(f"  > 저장 위치: {OUTPUT_MODEL_FILE}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="[Tokken 2.0] 텍스트 분류 모델을 학습합니다.")
    parser.add_argument('--file', type=str, required=True, help='학습에 사용할 CSV 파일의 전체 경로')
    args = parser.parse_args()
    train(args.file)