# E:\workspace\News_API\file_saver.py

import os
import csv
from datetime import datetime
import logging

log = logging.getLogger(__name__)

def save_raw_real_news(collected_articles, folder_path):
    """(1. 수집 단계) 크롤링한 '진짜 뉴스' 원본을 저장합니다."""
    if not collected_articles:
        log.warning("저장할 원본 기사가 없습니다 (Raw Data).")
        return
    
    os.makedirs(folder_path, exist_ok=True)
    today = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = os.path.join(folder_path, f"raw_real_news_{today}.csv")

    fieldnames = ['번호', '제목', '출처', '기자', 'URL', '게시일', '기사본문']

    try:
        with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for i, article in enumerate(collected_articles, 1):
                writer.writerow({
                    '번호': i, '제목': article.get('title', ''), '출처': article.get('source', ''),
                    '기자': article.get('author', ''), 'URL': article.get('url', ''),
                    '게시일': article.get('publishedAt', ''), '기사본문': article.get('text', ''),
                })
        log.info(f"총 {len(collected_articles)}개의 원본 기사 저장 완료: {filename}")
        return filename
    except Exception as e:
        log.error(f"원본 기사 CSV 파일 저장 중 오류 발생: {e}", exc_info=True)
        return None

def save_labeled_dataset(processed_articles, folder_path):
    """(2. 가공 단계) '진짜/가짜'로 라벨링된 최종 학습용 데이터셋을 저장합니다."""
    if not processed_articles:
        log.warning("저장할 기사가 없습니다 (학습용 데이터셋).")
        return

    os.makedirs(folder_path, exist_ok=True)
    today = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = os.path.join(folder_path, f"dataset_{today}.csv")

    fieldnames = ['번호', '제목', '출처', '기자', 'URL', '게시일', '기사본문', '진위여부(1:진짜, 0:가짜)']

    try:
        with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for i, article in enumerate(processed_articles, 1):
                writer.writerow({
                    '번호': i, '제목': article.get('title', ''), '출처': article.get('source', ''),
                    '기자': article.get('author', ''), 'URL': article.get('url', ''),
                    '게시일': article.get('publishedAt', ''), '기사본문': article.get('text', ''),
                    '진위여부(1:진짜, 0:가짜)': article.get('label', '')
                })
        log.info(f"총 {len(processed_articles)}개의 최종 학습 데이터 저장 완료: {filename}")
    except Exception as e:
        log.error(f"최종 학습용 CSV 파일 저장 중 오류 발생: {e}", exc_info=True)

def save_feedback_template_csv(original_articles, folder_path):
    """Media 모델 학습을 위한 피드백용 템플릿 CSV 파일을 저장합니다."""
    if not original_articles:
        log.warning("저장할 기사가 없습니다 (피드백용 템플릿).")
        return

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    feedback_folder = os.path.join(project_root, 'model', 'media', 'feedback_data')
    os.makedirs(feedback_folder, exist_ok=True)
    
    today = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = os.path.join(feedback_folder, f"feedback_template_{today}.csv")

    fieldnames = ['source', 'author', 'title', 'url', 'publishedAt', 'content', 'label', 'reason']

    try:
        with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for article in original_articles:
                writer.writerow({
                    'source': article.get('source', {}).get('name', ''),
                    'author': article.get('author', '기자 정보 없음'),
                    'title': article.get('title', ''), 'url': article.get('url', ''),
                    'publishedAt': article.get('publishedAt', ''), 'content': article.get('description', ''),
                    'label': '', 'reason': ''
                })
        log.info(f"총 {len(original_articles)}개 기사의 피드백 템플릿 저장 완료: {filename}")
    except Exception as e:
        log.error(f"피드백 템플릿 CSV 파일 저장 중 오류 발생: {e}", exc_info=True)