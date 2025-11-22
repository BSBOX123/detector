# E:\workspace\model\tokken\run_judgement.py

import pickle
import os
import numpy as np
import warnings
import sys

# 이 파일이 직접 실행되므로, 'tokken' 폴더를 sys.path에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    # '.'(점) 없이 'tokenizer'에서 import
    from tokenizer import okt_tokenizer
except ImportError:
    # 만약 'tokenizer.py'가 상위 폴더(model)에 있다면
    MODEL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(MODEL_DIR)
    from tokken.tokenizer import okt_tokenizer


warnings.filterwarnings("ignore", category=UserWarning, module='konlpy')

# --- 설정 ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_FILE = os.path.join(BASE_DIR, 'tokken_model_pipeline.pkl')
FAKE_NEWS_THRESHOLD = 50 

model_pipeline = None
fake_class_index = -1 

def load_weights():
    global model_pipeline, fake_class_index
    if not os.path.exists(MODEL_FILE):
        raise FileNotFoundError(f"[오류] 모델 파일('{MODEL_FILE}') 없음. 'model_trainer.py'를 먼저 실행하세요.")
    
    print(f"--- Tokken 2.0 모델 파일('{os.path.basename(MODEL_FILE)}') 로드 중... ---")
    with open(MODEL_FILE, 'rb') as f:
        model_pipeline = pickle.load(f)
        
    try:
        fake_class_index = np.where(model_pipeline.classes_ == 0)[0][0]
    except (AttributeError, IndexError):
        fake_class_index = 0 
    print(f"--- Tokken 2.0 모델 로드 완료 ---")

def judge_article(news_text):
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

def main():
    print("--- [Tokken] 텍스트 기반 판별기 시작 ---")
    print("분석할 뉴스 본문을 입력해주세요 (입력 완료 후 엔터를 두 번 누르세요)")
    
    try:
        # 프로그램 시작 시 모델 로드 시도
        load_weights()
    except FileNotFoundError as e:
        print(f"\n[오류] {e}")
        return

    while True:
        print("\n" + "="*50)
        print(">>> 기사 본문 입력:")
        
        # --- (핵심 수정) ---
        lines = []
        while True:
            line = input()
            if not line:
                # 'lines' 리스트에 내용이 이미 있으면, "입력 종료"로 간주
                if lines:
                    break
                # 'lines' 리스트가 비어있으면, 첫 줄의 빈 줄은 무시
                else:
                    continue
            lines.append(line)
        news_text = "\n".join(lines)
        # --- (수정 끝) ---
        
        if news_text.strip().lower() == 'exit':
            print("프로그램을 종료합니다.")
            break
        
        if not news_text.strip():
            print("내용이 없습니다. 다시 입력해주세요.")
            continue
            
        try:
            result = judge_article(news_text)
            print("\n--- 📝 텍스트 분석 결과 ---")
            print(f"  - 가짜뉴스 점수: {result['score']} / 100")
            print(f"  - 판단: {result['judgement']} (기준 점수: {result['threshold']}점)")

        except Exception as e:
            print(f"\n[오류] 판별 중 오류가 발생했습니다: {e}")

if __name__ == '__main__':
    main()