# E:\workspace\model\tokken\export_weights_to_csv.py

import pickle
import os
import pandas as pd

# 불러올 .pkl 파일 이름
INPUT_FILENAME = 'fake_news_keyword_weights.pkl'
# 저장할 .csv 파일 이름
OUTPUT_FILENAME = 'fake_news_keyword_weights_parameters.csv'

def save_weights_to_csv():
    """
    .pkl 파일에 저장된 딕셔너리 형태의 파라미터를 읽어와
    CSV 파일로 저장합니다.
    """
    # 이 스크립트가 실행되는 폴더(model/tokken)를 기준으로 경로 설정
    base_dir = os.path.dirname(os.path.abspath(__file__))
    pkl_file_path = os.path.join(base_dir, INPUT_FILENAME)
    csv_file_path = os.path.join(base_dir, OUTPUT_FILENAME)
    
    if not os.path.exists(pkl_file_path):
        print(f"[오류] 파라미터 파일을 찾을 수 없습니다: {pkl_file_path}")
        print("먼저 'model_trainer.py'를 실행하여 모델을 학습시켜야 합니다.")
        return

    try:
        # .pkl 파일을 바이너리 읽기 모드로 열기
        with open(pkl_file_path, 'rb') as f:
            # pickle.load()를 사용하여 파일 안의 파이썬 객체(딕셔너리)를 불러옵니다.
            data = pickle.load(f)

        print(f"\n--- 📖 '{INPUT_FILENAME}' 파일 로드 완료 ---")
        
        if isinstance(data, dict):
            print(f"총 {len(data)}개의 키워드 파라미터를 CSV로 변환합니다.")
            
            # 딕셔너리를 (키워드, 가중치) 튜플의 리스트로 변환
            keyword_list = list(data.items())
            
            # pandas DataFrame으로 변환
            df = pd.DataFrame(keyword_list, columns=['Keyword', 'Weight (Score)'])
            
            # 가중치(Weight) 기준으로 내림차순 정렬
            df_sorted = df.sort_values(by='Weight (Score)', ascending=False)
            
            # CSV 파일로 저장 (인덱스 제외, 한글 깨짐 방지 인코딩)
            df_sorted.to_csv(csv_file_path, index=False, encoding='utf-8-sig')
            
            print(f"\n--- ✅ 성공 ---")
            print(f"파라미터가 '{OUTPUT_FILENAME}' 파일로 성공적으로 저장되었습니다.")
            print(f"저장 위치: {csv_file_path}")

        else:
            print("[오류] .pkl 파일에 딕셔너리가 아닌 다른 형태의 데이터가 저장되어 있습니다.")

    except Exception as e:
        print(f"파일 처리 중 오류가 발생했습니다: {e}")

if __name__ == '__main__':
    save_weights_to_csv()