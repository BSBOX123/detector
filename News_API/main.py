# main.py

import time
import config
from concurrent.futures import ThreadPoolExecutor, as_completed
from api_handler import fetch_articles, generate_fake_version 
from crawler import crawl_article_text
from file_saver import save_articles_to_csv

def process_article(article):
    "하나의 진짜 기사로 '진짜'와 '가짜' 데이터 쌍(2개) 생성"
    url = article.get('url', '')
    original_title = article.get('title', '')
    source_name = article.get('source', {}).get('name', '')
    published_at = article.get('publishedAt', '')

    real_text = crawl_article_text(url)
    
    # '진짜' 데이터 레코드 (라벨 1)
    record_real = {
        'title': original_title,
        'source': source_name,
        'url': url,
        'publishedAt': published_at,
        'text': real_text,
        'label': 1  # 진짜 뉴스는 1
    }

    # '가짜' 데이터 레코드 생성 (라벨 0)
    fake_text = generate_fake_version(real_text)
    record_fake = {
        'title': "[가짜생성] " + original_title, # 제목으로 구분
        'source': source_name,
        'url': url,
        'publishedAt': published_at,
        'text': fake_text,
        'label': 0  # 가짜 뉴스는 0
    }
    
    # 두 개의 레코드를 리스트로 반환
    return [record_real, record_fake]

def main():
    """메인 실행 함수"""
    print("학습용 뉴스 데이터셋 구축을 시작합니다...")
    try:
        articles = fetch_articles(
            config.QUERY, config.LANGUAGE, config.SOURCES, config.SORT_BY, config.PAGE_SIZE
        )
        print(f"총 {len(articles)}개의 원본 기사를 가져왔습니다. (데이터 2배 생성 예정)")

        processed_articles = []
        batches = [articles[i:i + config.BATCH_SIZE] for i in range(0, len(articles), config.BATCH_SIZE)]

        for i, batch in enumerate(batches):
            print(f"\n--- 배치 {i+1}/{len(batches)} 처리 시작 ({len(batch)}개) ---")
            
            with ThreadPoolExecutor(max_workers=10) as executor:
                future_to_article = {executor.submit(process_article, article): article for article in batch}
                
                for future in as_completed(future_to_article):
                    try:
                        # [record_real, record_fake] 리스트를 한 번에 추가
                        processed_articles.extend(future.result()) 
                        print(f"  - 진짜/가짜 쌍 처리 완료: {future.result()[0]['title'][:30]}...")
                    except Exception as e:
                        print(f"[Error] 기사 처리 중 예외 발생: {e}")

            if i < len(batches) - 1:
                print(f"--- 배치 {i+1} 처리 완료. 61초간 대기합니다... ---")
                time.sleep(61)

        processed_articles.sort(key=lambda x: x['publishedAt'], reverse=True)
        save_articles_to_csv(processed_articles, config.QUERY, config.SAVE_FOLDER_PATH)

    except Exception as e:
        print(f"프로세스 실행 중 심각한 오류 발생: {e}")

if __name__ == '__main__':
    main()