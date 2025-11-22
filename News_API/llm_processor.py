# E:\workspace\News_API\llm_processor.py

import pandas as pd
import os
import glob
import logging
import time
# from concurrent.futures import ThreadPoolExecutor, as_completed # 더 이상 사용하지 않음
from tqdm import tqdm

# 상대 경로로 모듈 임포트
from .config import config
from .api_handler import generate_fake_version
from .file_saver import save_labeled_dataset

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_row_to_labeled_pair(row):
    """
    DataFrame의 한 행(Row)을 받아 '진짜'/'가짜' 데이터 쌍을 생성합니다.
    """
    real_text = row['기사본문']
    
    # '진짜' 데이터 레코드 (라벨 1)
    record_real = {
        'title': row['제목'],
        'source': row['출처'],
        'author': row['기자'],
        'url': row['URL'],
        'publishedAt': row['게시일'],
        'text': real_text,
        'label': 1  # 진짜 뉴스는 1
    }

    # '가짜' 데이터 레코드 생성 (라벨 0)
    fake_title, fake_text = generate_fake_version(real_text)
    record_fake = {
        'title': fake_title, # Gemini가 생성한 제목
        'source': row['출처'],
        'author': row['기자'],
        'url': row['URL'],
        'publishedAt': row['게시일'],
        'text': fake_text, # 클린업된 본문
        'label': 0  # 가짜 뉴스는 0
    }
    
    return [record_real, record_fake]

def main():
    """
    'raw_real_news...' CSV 파일을 읽어 LLM으로 가공하고
    최종 'dataset_...' CSV 파일을 생성합니다.
    """
    logging.info("LLM을 이용한 가짜뉴스 생성(가공) 작업을 시작합니다...")
    
    if not config.GEMINI_API_KEY or config.GEMINI_API_KEY == 'YOUR_GEMINI_API_KEY_DEFAULT':
        logging.critical("GEMINI_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요.")
        return

    # 1. 최신 'raw_real_news_...' 파일 찾기
    raw_files_path = os.path.join(config.SAVE_FOLDER_PATH, 'raw_real_news_*.csv')
    list_of_raw_files = glob.glob(raw_files_path)
    if not list_of_raw_files:
        logging.warning(f"가공할 원본 뉴스 파일이 없습니다. '{raw_files_path}' 경로를 확인하세요.")
        logging.warning("먼저 '1: 뉴스 데이터 수집'을 실행하세요.")
        return

    latest_raw_file = max(list_of_raw_files, key=os.path.getctime)
    logging.info(f"가공할 대상 파일을 찾았습니다: {latest_raw_file}")

    try:
        df = pd.read_csv(latest_raw_file)
        df.dropna(subset=['기사본문'], inplace=True) # 기사 본문이 없는 행은 제거
        df = df[df['기사본문'] != '[본문 없음]'] # 크롤링 실패한 기사 제거
    except Exception as e:
        logging.error(f"원본 CSV 파일 로드 실패: {e}")
        return

    processed_articles = []
    
    # 2. DataFrame의 각 행을 병렬 처리 (ThreadPoolExecutor) 대신 순차 처리로 변경
    rows_to_process = df.to_dict('records')
    
    logging.info(f"총 {len(rows_to_process)}개의 기사를 1개씩 순차적으로 처리합니다 (1분/2개 한도 준수).")
    
    # *** (핵심 수정!) ***
    # ThreadPoolExecutor를 제거하고, tqdm이 적용된 단순 for 반복문으로 변경
    for row in tqdm(rows_to_process, desc="LLM 가공 처리 중"):
        try:
            # 1분에 2개 한도를 준수하기 위해, 각 기사 처리 후 31초 대기
            # (2개 처리 시 약 62초 소요)
            processed_articles.extend(process_row_to_labeled_pair(row))
            time.sleep(31) # 1분에 2개 한도를 위한 31초 대기
        except Exception as e:
            row_title = row.get('title', '알 수 없음')
            logging.error(f"'{row_title}' 기사 가공 중 예외 발생: {e}", exc_info=True)
            # 한 기사에서 오류가 나도 다음 기사로 넘어가도록 continue
            continue
    # *** (수정 끝) ***

    processed_articles.sort(key=lambda x: x.get('publishedAt', ''), reverse=True)
    
    # 3. 최종 라벨링된 데이터셋 저장
    if processed_articles:
        save_labeled_dataset(processed_articles, config.SAVE_FOLDER_PATH)
    else:
        logging.warning("최종 처리된 기사가 없어 CSV 파일을 저장하지 않습니다.")

    logging.info("LLM을 이용한 가공 작업이 성공적으로 완료되었습니다.")

if __name__ == '__main__':
    main()