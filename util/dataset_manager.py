# E:\workspace\util\dataset_manager.py

import os
import pandas as pd
from datetime import datetime

# 데이터셋이 저장된 articles 폴더의 절대 경로
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARTICLES_PATH = os.path.join(BASE_DIR, '..', 'News_API', 'articles')

def get_datasets():
    """articles 폴더에 있는 모든 CSV 파일 목록 가져오기."""
    if not os.path.exists(ARTICLES_PATH):
        print(f"[경고] 데이터셋 폴더를 찾을 수 없습니다: {ARTICLES_PATH}")
        return []
    
    # .csv로 끝나는 파일만 필터링
    files = [f for f in os.listdir(ARTICLES_PATH) if f.endswith('.csv')]
    # 최신 파일이 위로 오도록 정렬
    files.sort(reverse=True)
    return files

def display_datasets(file_list):
    """파일 목록을 번호와 함께 보기 좋게 출력."""
    if not file_list:
        print("사용 가능한 데이터셋이 없습니다.")
        return
    
    print("\n--- 사용 가능한 데이터셋 목록 ---")
    for i, filename in enumerate(file_list):
        print(f"  [{i+1}] {filename}")
    print("-" * 35)

def merge_datasets(selected_indices, file_list):
    """선택된 여러 데이터셋을 하나로 병합."""
    if not selected_indices:
        print("선택된 데이터셋이 없습니다.")
        return

    dataframes = []
    for i in selected_indices:
        if 0 <= i < len(file_list):
            file_path = os.path.join(ARTICLES_PATH, file_list[i])
            print(f"'{file_list[i]}' 파일 로드 중...")
            try:
                df = pd.read_csv(file_path)
                dataframes.append(df)
            except Exception as e:
                print(f"[오류] '{file_list[i]}' 파일 로드 실패: {e}")
                return
        else:
            print(f"[경고] 잘못된 번호({i+1})는 건너뜁니다.")
    
    if not dataframes:
        print("병합할 데이터프레임이 없습니다.")
        return

    # 모든 데이터프레임을 하나로 합침
    merged_df = pd.concat(dataframes, ignore_index=True)
    # 중복된 기사(URL 기준)가 있다면 제거
    merged_df.drop_duplicates(subset=['URL'], inplace=True, keep='first')
    
    # 병합된 파일 저장
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    new_filename = f"dataset_merged_{timestamp}.csv"
    new_filepath = os.path.join(ARTICLES_PATH, new_filename)
    
    try:
        merged_df.to_csv(new_filepath, index=False, encoding='utf-8-sig')
        print(f"\n--- 병합 완료 ---")
        print(f"총 {len(merged_df)}개의 기사가 '{new_filename}' 파일로 저장되었습니다.")
    except Exception as e:
        print(f"[오류] 병합된 파일 저장 실패: {e}")

def delete_datasets(selected_indices, file_list):
    """선택된 데이터셋 파일을 삭제합니다."""
    if not selected_indices:
        print("선택된 데이터셋이 없습니다.")
        return
        
    for i in selected_indices:
        if 0 <= i < len(file_list):
            file_to_delete = os.path.join(ARTICLES_PATH, file_list[i])
            try:
                os.remove(file_to_delete)
                print(f"'{file_list[i]}' 파일이 삭제되었습니다.")
            except Exception as e:
                print(f"[오류] '{file_list[i]}' 파일 삭제 실패: {e}")
        else:
            print(f"[경고] 잘못된 번호({i+1})는 건너뜁니다.")