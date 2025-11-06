# E:\workspace\model\tokken\news_judger.py

import pickle
# from konlpy.tag import Okt # Okt 임포트 제거
import os
import numpy as np
import warnings

# --- (핵심 수정 3) ---
# pickle.load()가 'okt_tokenizer'의 정의를 찾을 수 있도록
# model_trainer.py와 동일한 tokenizer를 import합니다.
# 이 코드를 직접 사용하지는 않지만, import 자체로 pickle이 함수를 찾는 데 사용됩니다.
from .tokenizer import okt_tokenizer

# KoNLPy의 경고 메시지 무시 (선택 사항)
warnings.filterwarnings("ignore", category=UserWarning, module='konlpy')

# --- 설정 ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_FILE = os.path.join(BASE_DIR, 'tokken_model_pipeline.pkl')
FAKE_NEWS_THRESHOLD = 50 

# --- 전역 변수 초기화 ---
model_pipeline = None
fake_class_index = -1 

# --- 함수 정의 ---
def load_weights():
    """학습된 모델 파이프라인을 불러와 전역 변수에 저장합니다."""
    global model_pipeline, fake_class_index
    
    if not os.path.exists(MODEL_FILE):
        raise FileNotFoundError(f"[오류] 학습된 모델 파일('{MODEL_FILE}')을 찾을 수 없습니다. 'model_trainer.py'를 먼저 실행하여 모델을 학습시켜주세요.")
    
    print(f"--- Tokken 2.0 모델 파일('{os.path.basename(MODEL_FILE)}') 로드 중... ---")
    with open(MODEL_FILE, 'rb') as f:
        model_pipeline = pickle.load(f)
        
    try:
        fake_class_index = np.where(model_pipeline.classes_ == 0)[0][0]
    except (AttributeError, IndexError):
        print("[경고] 모델에서 '0' 라벨의 인덱스를 찾을 수 없습니다.")
        fake_class_index = 0 

    print(f"--- Tokken 2.0 모델 로드 완료 ---")

def judge_article(news_text):
    """뉴스 텍스트를 받아 '가짜일 확률' 점수를 계산하고 결과를 반환합니다."""
    global model_pipeline, fake_class_index
    if model_pipeline is None:
        load_weights()

    probabilities = model_pipeline.predict_proba([news_text])[0]
    
    fake_probability = probabilities[fake_class_index]
    
    final_score = fake_probability * 100
    
    judgement = "가짜 뉴스일 가능성 높음" if final_score >= FAKE_NEWS_THRESHOLD else "진짜 뉴스일 가능성 높음"

    return {
        "score": round(final_score, 2),
        "judgement": judgement,
        "threshold": FAKE_NEWS_THRESHOLD,
        "found_keywords": ["(모델 2.0: 확률 기반)"]
    }