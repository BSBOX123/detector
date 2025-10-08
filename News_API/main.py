# E:\workspace\News_API\main.py (디버깅용)

import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

# 상대 경로로 모듈 임포트
from .config import config
from .api_handler import fetch_articles, generate_fake_version
from .crawler import crawl_article
from .file_saver import save_articles_to_csv, save_feedback_template_csv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_article(article):
    """하나의 진짜 기사로 '진짜'와 '가짜' 데이터 쌍(2개) 생성"""
    url = article.get('url', '')
    original_title = article.get('title', '')
    source_name = article.get('source', {}).get('name', '')
    published_at = article.get('publishedAt', '')
    author_name_from_api = article.get('author', None)

    # --- 디버깅 로그 추가 ---
    print(f"\n[DEBUG] 1. 크롤링 시작: {url}")
    real_text, author_name_from_crawl = crawl_article(url)
    print(f"[DEBUG] 2. 크롤링 완료. (본문 길이: {len(real_text)}, 기자: {author_name_from_crawl})")
    
    final_author_name = author_name_from_crawl
    if author_name_from_crawl == '[기자 정보 없음]' and author_name_from_api:
        final_author_name = author_name_from_api

    record_real = {
        'title': original_title, 'source': source_name, 'url': url, 'publishedAt': published_at,
        'text': real_text, 'label': 1, 'author': final_author_name
    }

    # --- 디버깅 로그 추가 ---
    print(f"[DEBUG] 3. Gemini API로 가짜뉴스 생성 시작...")
    fake_text = generate_fake_version(real_text)
    print(f"[DEBUG] 4. Gemini API 호출 완료. (가짜뉴스 길이: {len(fake_text)})")

    record_fake = {
        'title': "[가짜생성] " + original_title, 'source': source_name, 'url': url, 'publishedAt': published_at,
        'text': fake_text, 'label': 0, 'author': final_author_name
    }
    
    return [record_real, record_fake]

def main():
    """메인 실행 함수"""
    logging.info("학습용 뉴스 데이터셋 구축을 시작합니다...")
    
    if not config.NEWS_API_KEY or config.NEWS_API_KEY == 'YOUR_NEWS_API_KEY_DEFAULT' or \
       not config.GEMINI_API_KEY or config.GEMINI_API_KEY == 'YOUR_GEMINI_API_KEY_DEFAULT':
        logging.critical("API 키가 설정되지 않았습니다. .env 파일을 확인하세요.")
        return

    try:
        all_articles = []
        for query in tqdm(config.QUERIES, desc="카테고리별 뉴스 수집 중"):
            articles_per_query = fetch_articles(
                query, config.LANGUAGE, config.SOURCES, config.SORT_BY, config.PAGE_SIZE
            )
            if articles_per_query:
                all_articles.extend(articles_per_query)
            time.sleep(1)

        unique_articles = list({article['url']: article for article in all_articles}.values())
        logging.info(f"총 {len(unique_articles)}개의 고유한 원본 기사를 가져왔습니다.")

        if not unique_articles:
            logging.warning("처리할 고유 기사가 없습니다.")
            return

        save_feedback_template_csv(unique_articles, config.SAVE_FOLDER_PATH)
        logging.info("이제 Gemini API를 통해 가짜뉴스를 생성합니다.")

        processed_articles = []
        
        # *** 핵심 수정: 병렬 처리(ThreadPoolExecutor)를 임시로 비활성화하고 순차 처리로 변경 ***
        print("\n--- [디버그 모드] 기사를 하나씩 순서대로 처리합니다. ---")
        for article in tqdm(unique_articles, desc="뉴스 순차 처리 중"):
            try:
                result = process_article(article)
                processed_articles.extend(result)
                print(f"[DEBUG] 5. 기사 처리 성공: {article.get('title', '')[:30]}...")
            except Exception as e:
                logging.error(f"[Error] 기사 처리 중 예외 발생: {article.get('url', '')} / 오류: {e}", exc_info=True)

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