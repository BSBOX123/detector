# E:\workspace\News_API\main.py

import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

# 상대 경로로 모듈 임포트
# --- (핵심 수정 3) config 객체 하나만 임포트 ---
from .config import config 
from .api_handler import fetch_articles, generate_fake_version
from .crawler import crawl_article
from .file_saver import save_raw_real_news, save_feedback_template_csv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_article(article):
    """(1. 수집 단계) '진짜 뉴스' 기사 1개를 크롤링하고 데이터 정리"""
    url = article.get('url', '')
    original_title = article.get('title', '')
    source_name = article.get('source', {}).get('name', '')
    published_at = article.get('publishedAt', '')
    author_name_from_api = article.get('author', None)

    real_text, author_name_from_crawl = crawl_article(url)
    
    final_author_name = author_name_from_crawl
    if author_name_from_crawl == '[기자 정보 없음]' and author_name_from_api:
        final_author_name = author_name_from_api

    record_real = {
        'title': original_title, 'source': source_name, 'url': url,
        'publishedAt': published_at, 'text': real_text, 'author': final_author_name 
    }
    
    return record_real

def main():
    """메인 실행 함수 (데이터 수집 전용)"""
    logging.info("원본 뉴스 데이터 수집을 시작합니다...")
    
    if not config.NEWS_API_KEY or config.NEWS_API_KEY == 'YOUR_NEWS_API_KEY_DEFAULT':
        logging.critical("NEWS_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요.")
        return

    try:
        all_articles = []
        
        # --- (핵심 수정 4) config.QUERIES, config.DATE_RANGES_TO_SCAN 등으로 접근 ---
        print(f"총 {len(config.QUERIES)}개 검색어, {len(config.DATE_RANGES_TO_SCAN)}개 날짜 범위, 최대 {config.PAGE_LIMIT}페이지 수집을 시작합니다.")
        
        for query in tqdm(config.QUERIES, desc="전체 카테고리 진행", unit="query"):
            logging.info(f"'{query}' 카테고리 뉴스 수집 시작...")
            for date_range in config.DATE_RANGES_TO_SCAN:
                from_date = date_range["from_date"]
                to_date = date_range["to_date"]
                for page_num in range(1, config.PAGE_LIMIT + 1):
                    articles_per_page = fetch_articles(
                        query, config.LANGUAGE, config.SOURCES, config.SORT_BY, config.PAGE_SIZE,
                        from_date=from_date, to_date=to_date, page=page_num
                    )
                    if articles_per_page:
                        all_articles.extend(articles_per_page)
                    else:
                        break 
                    time.sleep(1)
            time.sleep(2)

        unique_articles = list({article['url']: article for article in all_articles}.values())
        logging.info(f"총 {len(unique_articles)}개의 고유한 원본 기사를 가져왔습니다.")

        if not unique_articles:
            logging.warning("처리할 고유 기사가 없습니다.")
            return

        save_feedback_template_csv(unique_articles, config.SAVE_FOLDER_PATH)

        logging.info("이제 각 기사의 본문을 크롤링합니다...")
        collected_articles = []
        batches = [unique_articles[i:i + config.BATCH_SIZE] for i in range(0, len(unique_articles), config.BATCH_SIZE)]

        for i, batch in enumerate(tqdm(batches, desc="뉴스 크롤링 처리 중", unit="batch")):
            with ThreadPoolExecutor(max_workers=10) as executor:
                future_to_article = {executor.submit(process_article, article): article for article in batch}
                for future in as_completed(future_to_article):
                    try:
                        collected_articles.append(future.result())
                    except Exception as e:
                        logging.error(f"기사 크롤링 중 예외 발생: {e}", exc_info=True)

        collected_articles.sort(key=lambda x: x.get('publishedAt', ''), reverse=True)
        
        if collected_articles:
            save_raw_real_news(collected_articles, config.SAVE_FOLDER_PATH)
        else:
            logging.warning("최종 수집된 기사가 없어 CSV 파일을 저장하지 않습니다.")

        logging.info("원본 뉴스 데이터 수집이 성공적으로 완료되었습니다.")

    except Exception as e:
        logging.critical(f"프로세스 실행 중 치명적인 오류 발생: {e}", exc_info=True)

if __name__ == '__main__':
    main()