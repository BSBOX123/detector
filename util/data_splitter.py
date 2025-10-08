# E:\workspace\util\data_splitter.py

import pandas as pd
from sklearn.model_selection import train_test_split
import os
import argparse

def split_dataset(file_path, test_size=0.2):
    """
    주어진 CSV 데이터셋을 학습용과 평가용으로 분리합니다.
    '진위여부' 라벨의 비율을 유지하며 분리합니다 (Stratified Split).
    """
    print(f"--- 💾 데이터셋 분리 시작 ---")
    print(f"대상 파일: {file_path}")

    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"[오류] 파일을 찾을 수 없습니다: {file_path}")
        return
    
    # 분리에 필요한 컬럼 확인
    label_column = '진위여부(1:진짜, 0:가짜)'
    if label_column not in df.columns:
        print(f"[오류] '{label_column}' 컬럼을 찾을 수 없습니다.")
        return
        
    # 라벨 비율을 유지하며 데이터 분리
    train_df, test_df = train_test_split(
        df,
        test_size=test_size,       # 평가 데이터 비율 (20%)
        random_state=42,           # 재현성을 위한 시드값
        stratify=df[label_column]  # 이 컬럼의 비율을 유지하며 분리
    )
    
    # 저장될 파일 경로 설정
    directory, filename = os.path.split(file_path)
    base_name, ext = os.path.splitext(filename)
    
    train_filename = os.path.join(directory, f"{base_name}_train.csv")
    test_filename = os.path.join(directory, f"{base_name}_test.csv")
    
    # 파일 저장
    train_df.to_csv(train_filename, index=False, encoding='utf-8-sig')
    test_df.to_csv(test_filename, index=False, encoding='utf-8-sig')
    
    print(f"\n--- ✅ 분리 완료 ---")
    print(f"  - 원본 데이터: {len(df)}개")
    print(f"  - 학습 데이터: {len(train_df)}개 (저장 위치: {train_filename})")
    print(f"  - 평가 데이터: {len(test_df)}개 (저장 위치: {test_filename})")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="데이터셋을 학습용과 평가용으로 분리합니다.")
    parser.add_argument('--file', type=str, required=True, help='분리할 원본 CSV 파일의 전체 경로')
    args = parser.parse_args()
    
    split_dataset(args.file)