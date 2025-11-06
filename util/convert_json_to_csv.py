# E:\workspace\util\convert_json_to_csv.py

import os
import json
import pandas as pd
from datetime import datetime
import csv # csv 모듈 import

# --- 설정 ---
# 원본 JSON 파일들이 들어있는 폴더 경로 (수정 필요)
JSON_SOURCE_FOLDER = r'E:\workspace\Data_Set\News_JSONs' 
# 변환된 CSV 파일을 저장할 경로
OUTPUT_FOLDER = r'E:\workspace\Data_Set\articles'
OUTPUT_FILENAME = f"raw_real_news_from_json_{datetime.now().strftime('%Y-%m-%d')}.csv"

def convert_json_to_csv():
    """
    지정된 폴더(JSON_SOURCE_FOLDER)의 모든 JSON 파일을 읽어
    'raw_real_news...' CSV 파일로 변환합니다.
    """
    print(f"---  JSON 데이터 변환 시작 ---")
    print(f"원본 폴더: {JSON_SOURCE_FOLDER}")
    
    if not os.path.exists(JSON_SOURCE_FOLDER):
        print(f"[오류] 원본 폴더를 찾을 수 없습니다: {JSON_SOURCE_FOLDER}")
        print("스크립트 상단의 JSON_SOURCE_FOLDER 변수 경로를 수정해주세요.")
        return

    all_articles = []
    
    for filename in os.listdir(JSON_SOURCE_FOLDER):
        if filename.endswith('.json'):
            file_path = os.path.join(JSON_SOURCE_FOLDER, filename)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 보여주신 JSON 구조에 맞게 데이터 추출
                info = data.get('sourceDataInfo', {})
                
                # 기사 본문 추출
                content = info.get('newsContent', '')
                if not content:
                    # newsContent가 비어있으면 sentenceInfo를 합칩니다.
                    sentences = [s.get('sentenceContent', '') for s in info.get('sentenceInfo', [])]
                    content = "\n".join(sentences)
                    
                if not content.strip():
                    print(f"[경고] {filename} 파일에 기사 본문이 없습니다. 건너뜁니다.")
                    continue
                    
                article = {
                    'title': info.get('newsTitle', '제목 없음'),
                    'source': info.get('newsCategory', 'JSON 데이터'), # 출처 대신 카테고리
                    'author': '[정보 없음]', # JSON에 기자 정보가 없음
                    'url': f"json://{info.get('newsID', filename)}",
                    'publishedAt': datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'), # 임시로 현재 시간
                    'text': content
                }
                all_articles.append(article)
                
            except Exception as e:
                print(f"[오류] {filename} 파일 처리 중 오류 발생: {e}")

    if not all_articles:
        print("변환할 기사가 없습니다.")
        return

    # --- CSV 파일로 저장 ---
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    output_path = os.path.join(OUTPUT_FOLDER, OUTPUT_FILENAME)
    
    # file_saver.py의 save_raw_real_news 함수와 동일한 헤더 사용
    fieldnames = ['번호', '제목', '출처', '기자', 'URL', '게시일', '기사본문']
    
    try:
        with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for i, article in enumerate(all_articles, 1):
                writer.writerow({
                    '번호': i,
                    '제목': article.get('title', ''),
                    '출처': article.get('source', ''),
                    '기자': article.get('author', ''),
                    'URL': article.get('url', ''),
                    '게시일': article.get('publishedAt', ''),
                    '기사본문': article.get('text', '')
                })
        print(f"\n--- ✅ 변환 완료 ---")
        print(f"총 {len(all_articles)}개의 '진짜 뉴스' 원본이 아래 파일로 저장되었습니다:")
        print(output_path)
    except Exception as e:
        print(f"CSV 파일 저장 중 오류 발생: {e}")

if __name__ == '__main__':
    # JSON_SOURCE_FOLDER 경로를 실제 JSON 파일들이 있는 폴더로 수정하고 실행하세요.
    convert_json_to_csv()