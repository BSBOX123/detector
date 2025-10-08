# E:\workspace\News_API\main.py

import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

# 상대 경로로 모듈 임포트
from .config import config
from .api_handler import fetch_articles, generate_fake_version
from .crawler import crawl_article_text
from .file_saver import save_articles_to_csv

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_article(article):
    """하나의 진짜 기사로 '진짜'와 '가짜' 데이터 쌍(2개) 생성"""
    url = article.get('url', '')
    original_title = article.get('title', '')
    source_name = article.get('source', {}).get('name', '')
    published_at = article.get('publishedAt', '')

    real_text = crawl_article_text(url)
    
    record_real = {
        'title': original_title,
        'source': source_name,
        'url': url,
        'publishedAt': published_at,
        'text': real_text,
        'label': 1  # 진짜 뉴스는 1
    }

    fake_text = generate_fake_version(real_text)
    record_fake = {
        'title': "[가짜생성] " + original_title,
        'source': source_name,
        'url': url,
        'publishedAt': published_at,
        'text': fake_text,
        'label': 0  # 가짜 뉴스는 0
    }
    
    return [record_real, record_fake]

def main():
    """메인 실행 함수"""
    logging.info("학습용 뉴스 데이터셋 구축을 시작합니다...")
    
    if not config.NEWS_API_KEY or config.NEWS_API_KEY == 'YOUR_NEWS_API_KEY_DEFAULT':
        logging.critical("NEWS_API_KEY가 설정되지 않았습니다. .env 또는 config.py 파일을 확인하세요.")
        return
    if not config.GEMINI_API_KEY or config.GEMINI_API_KEY == 'YOUR_GEMINI_API_KEY_DEFAULT':
        logging.critical("GEMINI_API_KEY가 설정되지 않았습니다. .env 또는 config.py 파일을 확인하세요.")
        return

    try:
        all_articles = []
        # config.py의 QUERIES 리스트를 순회하며 다양한 카테고리의 뉴스 수집
        for query in tqdm(config.QUERIES, desc="카테고리별 뉴스 수집 중"):
            logging.info(f"'{query}' 카테고리 뉴스 수집 시작...")
            
            articles_per_query = fetch_articles(
                query, config.LANGUAGE, config.SOURCES, config.SORT_BY, config.PAGE_SIZE
            )
            
            if articles_per_query:
                all_articles.extend(articles_per_query)
                logging.info(f"'{query}' 카테고리에서 {len(articles_per_query)}개의 기사 수집 완료.")
            else:
                logging.warning(f"'{query}' 카테고리에서 가져온 기사가 없습니다.")
            
            # News API의 분당 요청 제한(rate limit)을 피하기 위해 각 쿼리 사이에 지연 시간 추가
            time.sleep(2)

        # URL 기준으로 중복된 기사 제거
        unique_articles = list({article['url']: article for article in all_articles}.values())
        logging.info(f"총 {len(unique_articles)}개의 고유한 원본 기사를 가져왔습니다. (데이터 2배 생성 예정)")

        if not unique_articles:
            logging.warning("처리할 고유 기사가 없습니다. 수집을 종료합니다.")
            return

        processed_articles = []
        batches = [unique_articles[i:i + config.BATCH_SIZE] for i in range(0, len(unique_articles), config.BATCH_SIZE)]

        for i, batch in enumerate(tqdm(batches, desc="뉴스 배치 처리 중", unit="batch")):
            logging.info(f"--- 배치 {i+1}/{len(batches)} 처리 시작 ({len(batch)}개) ---")
            
            with ThreadPoolExecutor(max_workers=10) as executor:
                future_to_article = {executor.submit(process_article, article): article for article in batch}
                
                for future in as_completed(future_to_article):
                    try:
                        processed_articles.extend(future.result())
                    except Exception as e:
                        logging.error(f"[Error] 기사 처리 중 예외 발생: {e}", exc_info=True)

            if i < len(batches) - 1:
                logging.info(f"--- 배치 {i+1} 처리 완료. {config.BATCH_DELAY_SECONDS}초간 대기...")
                time.sleep(config.BATCH_DELAY_SECONDS)

        processed_articles.sort(key=lambda x: x.get('publishedAt', ''), reverse=True)
        
        if processed_articles:
            save_articles_to_csv(processed_articles, "merged_queries", config.SAVE_FOLDER_PATH)
        else:
            logging.warning("최종 처리된 기사가 없어 CSV 파일을 저장하지 않습니다.")

        logging.info("학습용 뉴스 데이터셋 구축이 성공적으로 완료되었습니다.")

    except Exception as e:
        logging.critical(f"프로세스 실행 중 치명적인 오류 발생: {e}", exc_info=True)

if __name__ == '__main__':
    main()