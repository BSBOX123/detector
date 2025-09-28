# E:\workspace\model\tokken\news_judger.py

import pickle
from konlpy.tag import Okt
import os

# --- 설정 ---
# 이 파일(news_judger.py)이 있는 디렉토리 경로
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 학습된 가중치 파일명 (tokken 폴더 안에 저장됩니다)
WEIGHTS_FILE = os.path.join(BASE_DIR, 'fake_news_keyword_weights.pkl')

# 가짜뉴스 판단 임계값 (이 점수 이상이면 '가짜 뉴스'로 판단)
FAKE_NEWS_THRESHOLD = 60 

# --- 전역 변수 초기화 ---
okt = Okt()
fake_news_weights = None

# --- 함수 정의 ---
def load_weights():
    """
    저장된 가중치 파일을 불러와 전역 변수에 저장합니다.
    """
    global fake_news_weights
    if not os.path.exists(WEIGHTS_FILE):
        raise FileNotFoundError(f"[오류] 가중치 파일('{WEIGHTS_FILE}')을 찾을 수 없습니다. 'E:\\workspace\\model\\tokken' 폴더에서 model_trainer.py를 먼저 실행하여 모델을 학습시켜주세요.")
    
    with open(WEIGHTS_FILE, 'rb') as f:
        fake_news_weights = pickle.load(f)
    print(f"--- 가중치 파일('{WEIGHTS_FILE}') 로드 완료 ---")

def _preprocess(text):
    """
    텍스트 전처리 내부 함수 (명사 추출)
    """
    if not isinstance(text, str):
        return []
    nouns = okt.nouns(text)
    return [noun for noun in nouns if len(noun) > 1]

def judge_article(news_text):
    """
    새로운 뉴스 텍스트를 받아 가짜뉴스 점수를 계산하고 판단 결과를 반환합니다.
    """
    global fake_news_weights # 전역 변수임을 명시
    if fake_news_weights is None:
        load_weights() # 가중치가 로드되지 않았다면 자동으로 로드

    processed_nouns = _preprocess(news_text)
    processed_text_str = " ".join(processed_nouns)
    
    total_weighted_score = 0.0
    found_keywords = []
    
    for keyword, weight in fake_news_weights.items():
        # 키워드가 전처리된 텍스트(문자열 형태)에 포함되어 있는지 확인
        # f' {keyword} ' 로 감싸는 이유는 '핵심'이 '핵심적' 같은 다른 단어의 일부로 인식되는 것을 방지하기 위함
        if f' {keyword} ' in f' {processed_text_str} ':
            total_weighted_score += weight
            found_keywords.append(keyword)
            
    max_score = sum(fake_news_weights.values())
    normalized_score = (total_weighted_score / max_score) * 100 if max_score > 0 else 0
    
    judgement = "가짜 뉴스일 가능성 높음" if normalized_score >= FAKE_NEWS_THRESHOLD else "진짜 뉴스일 가능성 높음"

    # 결과값을 딕셔너리 형태로 반환
    return {
        "score": round(normalized_score, 2),
        "judgement": judgement,
        "threshold": FAKE_NEWS_THRESHOLD,
        "found_keywords": found_keywords
    }