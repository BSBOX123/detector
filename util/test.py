import pandas as pd
from konlpy.tag import Okt
from collections import Counter
import os

# --- 설정 ---
# 뉴스 데이터가 저장된 CSV 파일의 전체 경로
CSV_FILE_PATH = r'E:\workspace\News_API\articles\dataset_2025-09-28_16-07-47.csv' 

# 분석할 텍스트가 담긴 열(column)의 이름
TEXT_COLUMN_NAME = '기사본문'

# 진위여부 라벨이 담긴 열(column)의 이름
LABEL_COLUMN_NAME = '진위여부(1:진짜, 0:가짜)' 

# 각 그룹별 상위 몇 개의 단어를 출력할지 결정
TOP_N_WORDS_PER_GROUP = 30

# --- 1. 텍스트 전처리 및 토큰화 함수 정의 (명사만 추출) ---
okt = Okt() # 형태소 분석기 초기화

def preprocess_and_extract_nouns(text):
    """
    주어진 텍스트를 형태소 분석하여 명사만 추출하고
    두 글자 이상인 단어만 필터링하여 반환하는 함수.
    """
    if not isinstance(text, str):
        return []
        
    nouns = okt.nouns(text) # 명사만 추출
    # 두 글자 이상인 명사만 필터링
    filtered_nouns = [noun for noun in nouns if len(noun) > 1]
            
    return filtered_nouns

# ======================================================================
# --- 메인 실행 로직 ---
# ======================================================================
if __name__ == "__main__":
    print(f"--- 1. 지정된 CSV 파일 로드: '{CSV_FILE_PATH}' ---")
    
    # CSV 파일 존재 여부 확인
    if not os.path.exists(CSV_FILE_PATH):
        print(f"[오류] 파일을 찾을 수 없습니다. 경로를 확인해주세요: {CSV_FILE_PATH}")
        exit()
        
    try:
        df = pd.read_csv(CSV_FILE_PATH, encoding='utf-8-sig') # 한글 인코딩 고려
        print(f"총 {len(df)}개의 기사 데이터 로드 완료.")
        print("로드된 데이터 미리보기 (상위 5줄):")
        print(df.head())
    except Exception as e:
        print(f"[오류] CSV 파일 로드 중 문제가 발생했습니다: {e}")
        exit()

    # 필수 컬럼 존재 여부 확인
    if TEXT_COLUMN_NAME not in df.columns:
        print(f"[오류] '{TEXT_COLUMN_NAME}' 컬럼을 데이터프레임에서 찾을 수 없습니다.")
        print(f"사용 가능한 컬럼: {df.columns.tolist()}")
        exit()
    if LABEL_COLUMN_NAME not in df.columns:
        print(f"[오류] '{LABEL_COLUMN_NAME}' 컬럼을 데이터프레임에서 찾을 수 없습니다.")
        print(f"사용 가능한 컬럼: {df.columns.tolist()}")
        exit()

    print(f"\n--- 2. '{LABEL_COLUMN_NAME}' 라벨 기반 그룹별 단어 빈도 분석 시작 ---")
    
    # --- 2-1. '진짜 뉴스' (라벨 1) 그룹 분석 ---
    true_news_df = df[df[LABEL_COLUMN_NAME] == 1].copy() # 원본 데이터에 영향 없도록 .copy() 사용
    all_nouns_true = []
    
    print("\n[진짜 뉴스] 기사에서 명사 추출 중...")
    for text in true_news_df[TEXT_COLUMN_NAME]:
        all_nouns_true.extend(preprocess_and_extract_nouns(str(text))) # str()로 NaN 처리

    if not all_nouns_true:
        print("[경고] '진짜 뉴스' 그룹에서 추출된 단어가 없습니다.")
    else:
        true_word_counts = Counter(all_nouns_true)
        print(f"[진짜 뉴스] 총 {sum(true_word_counts.values())}개의 명사가 추출되었습니다.")
        print(f"\n--- [진짜 뉴스] 가장 많이 사용된 단어들 (상위 {TOP_N_WORDS_PER_GROUP}개) ---")
        for word, count in true_word_counts.most_common(TOP_N_WORDS_PER_GROUP):
            print(f"  - {word}: {count}회")

    # --- 2-2. '가짜 뉴스' (라벨 0) 그룹 분석 ---
    fake_news_df = df[df[LABEL_COLUMN_NAME] == 0].copy() # 원본 데이터에 영향 없도록 .copy() 사용
    all_nouns_fake = []

    print("\n[가짜 뉴스] 기사에서 명사 추출 중...")
    for text in fake_news_df[TEXT_COLUMN_NAME]:
        all_nouns_fake.extend(preprocess_and_extract_nouns(str(text))) # str()로 NaN 처리

    if not all_nouns_fake:
        print("[경고] '가짜 뉴스' 그룹에서 추출된 단어가 없습니다.")
    else:
        fake_word_counts = Counter(all_nouns_fake)
        print(f"[가짜 뉴스] 총 {sum(fake_word_counts.values())}개의 명사가 추출되었습니다.")
        print(f"\n--- [가짜 뉴스] 가장 많이 사용된 단어들 (상위 {TOP_N_WORDS_PER_GROUP}개) ---")
        for word, count in fake_word_counts.most_common(TOP_N_WORDS_PER_GROUP):
            print(f"  - {word}: {count}회")

    print("\n--- 그룹별 단어 빈도 분석 완료 ---")