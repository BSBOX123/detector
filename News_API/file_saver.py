# E:\workspace\News_API\file_saver.py

import os
import csv
from datetime import datetime
import logging # 로깅 모듈 추가

log = logging.getLogger(__name__) # 모듈별 로거 생성

def save_articles_to_csv(processed_articles, query, folder_path):
    """기사 데이터를 CSV 파일로 저장합니다."""
    if not processed_articles:
        log.warning("저장할 기사가 없습니다.")
        return

    os.makedirs(folder_path, exist_ok=True)
    today = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = os.path.join(folder_path, f"dataset_{today}.csv")

    # 데이터셋에 맞는 헤더
    fieldnames = ['번호', '제목', '출처', 'URL', '게시일', '기사본문', '진위여부(1:진짜, 0:가짜)']

    try:
        with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for i, article in enumerate(processed_articles, 1):
                writer.writerow({
                    '번호': i,
                    '제목': article.get('title', ''),
                    '출처': article.get('source', ''),
                    'URL': article.get('url', ''),
                    '게시일': article.get('publishedAt', ''),
                    '기사본문': article.get('text', ''),
                    '진위여부(1:진짜, 0:가짜)': article.get('label', '')
                })
                
        log.info(f"총 {len(processed_articles)}개 데이터 저장 완료: {filename}")
    except Exception as e:
        log.error(f"CSV 파일 저장 중 오류 발생: {e}", exc_info=True)