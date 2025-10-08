# E:\workspace\model\media\media_score.py

import pandas as pd
import numpy as np
import os
import glob
from datetime import datetime
import argparse

LABEL_SCORE_MAP = {0: 1.0, 1: 0.6, 2: -0.15, 3: -0.85}
MIN_ARTICLES_SOURCE = 3
MIN_ARTICLES_AUTHOR = 3
INITIAL_WEIGHTS_FILE = "source_initial_weights.csv"
FEEDBACK_FOLDER = "feedback_data"
WEIGHTS_FOLDER = "weights_history"
AUTHOR_WEIGHTS_FILE = "author_weights.csv"

class CredibilityModel:
    def __init__(self, initial_weights_csv_path):
        weight_files = glob.glob(os.path.join(WEIGHTS_FOLDER, 'weights_*.csv'))
        load_path = initial_weights_csv_path
        if weight_files:
            latest_file = max(weight_files, key=os.path.getctime)
            if os.path.exists(latest_file):
                load_path = latest_file
        print(f"[INFO] 가중치 파일 로드: '{load_path}'")
        try:
            self.source_weights = pd.read_csv(load_path).set_index('source')
            if 'final_weight' not in self.source_weights.columns:
                self.source_weights['final_weight'] = self.source_weights['initial_weight']
        except FileNotFoundError:
            print(f"[ERROR] 가중치 파일을 찾을 수 없습니다: '{load_path}'")
            self.source_weights = pd.DataFrame()
        self.author_weights = pd.DataFrame()

    def update_with_feedback(self, feedback_data: pd.DataFrame, alpha_value: float):
        print(f"\n[INFO] 피드백 데이터로 가중치 업데이트 시작... (ALPHA={alpha_value})")
        df_clean = feedback_data.dropna(subset=['label', 'author', 'source'])
        df_clean = df_clean[df_clean['label'].isin([0, 1, 2, 3])]
        df_clean['label'] = pd.to_numeric(df_clean['label'])
        df_clean['article_score'] = df_clean['label'].map(LABEL_SCORE_MAP)

        author_scores = df_clean.groupby('author').agg(
            article_count=('label', 'count'),
            avg_article_score=('article_score', 'mean')
        ).reset_index()
        author_scores['credibility_score'] = (author_scores['avg_article_score'] + 1) / 2
        self.author_weights = author_scores[author_scores['article_count'] >= MIN_ARTICLES_AUTHOR]
        print("[INFO] 기자 신뢰도 업데이트 완료.")

        df_current_weights = self.source_weights[['final_weight']].reset_index()
        df_current_weights.rename(columns={'final_weight': 'initial_weight'}, inplace=True)

        source_scores = df_clean.groupby('source').agg(
            article_count=('label', 'count'),
            avg_article_score=('article_score', 'mean')
        ).reset_index()
        source_scores['observed_score'] = (source_scores['avg_article_score'] + 1) / 2
        
        df_merged = df_current_weights.merge(source_scores, on='source', how='outer')
        etc_weight = df_current_weights[df_current_weights['source'] == 'etc']['initial_weight'].iloc[0] if 'etc' in df_current_weights['source'].values else 0.5
        df_merged['initial_weight'] = df_merged['initial_weight'].fillna(etc_weight)
        df_merged['article_count'] = df_merged['article_count'].fillna(0).astype(int)
        
        fill_values = df_merged.set_index('source')['initial_weight'].to_dict()
        df_merged['observed_score'] = df_merged['observed_score'].fillna(df_merged['source'].map(fill_values))
        
        df_merged['final_weight'] = np.where(
            df_merged['article_count'] >= MIN_ARTICLES_SOURCE,
            (df_merged['initial_weight'] * alpha_value) + (df_merged['observed_score'] * (1 - alpha_value)),
            df_merged['initial_weight']
        )
        self.source_weights = df_merged.set_index('source')
        print("[INFO] 언론사 신뢰도 업데이트 완료.")

    def get_rankings(self):
        cols_to_show = [col for col in ['initial_weight', 'final_weight', 'article_count'] if col in self.source_weights.columns]
        source_ranking = self.source_weights[cols_to_show].sort_values(by='final_weight', ascending=False)
        if not self.author_weights.empty:
            author_ranking = self.author_weights[['author', 'article_count', 'credibility_score']].sort_values(by='credibility_score', ascending=False)
        else:
            author_ranking = self.author_weights
        return source_ranking, author_ranking

    def save_weights_to_csv(self):
        os.makedirs(WEIGHTS_FOLDER, exist_ok=True)
        today_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = os.path.join(WEIGHTS_FOLDER, f'weights_{today_str}.csv')
        df_to_save = self.source_weights.copy()
        cols_to_save = [col for col in ['initial_weight', 'final_weight', 'article_count'] if col in df_to_save.columns]
        df_to_save[cols_to_save].to_csv(output_filename, encoding='utf-8-sig')
        print(f"\n[SUCCESS] 언론사 가중치를 '{output_filename}' 파일로 저장했습니다.")
        
        if not self.author_weights.empty:
            author_output_filename = os.path.join(WEIGHTS_FOLDER, AUTHOR_WEIGHTS_FILE)
            self.author_weights.to_csv(author_output_filename, index=False, encoding='utf-8-sig')
            print(f"[SUCCESS] 기자 가중치를 '{author_output_filename}' 파일로 저장했습니다.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Media 신뢰도 모델을 학습합니다.")
    parser.add_argument('--alpha', type=float, default=0.7, help='반영 비율 (0.0 ~ 1.0)')
    parser.add_argument('--file', type=str, help='학습에 사용할 피드백 CSV 파일 경로')
    args = parser.parse_args()

    model = CredibilityModel(INITIAL_WEIGHTS_FILE)
    
    feedback_file_to_use = args.file
    if not feedback_file_to_use:
        feedback_files = glob.glob(os.path.join(FEEDBACK_FOLDER, '*.csv'))
        if feedback_files:
            feedback_file_to_use = max(feedback_files, key=os.path.getctime)
    
    if feedback_file_to_use and os.path.exists(feedback_file_to_use):
        print(f"\n[INFO] 피드백 파일 '{feedback_file_to_use}'로 업데이트 시작.")
        try:
            new_labeled_data = pd.read_csv(feedback_file_to_use)
            model.update_with_feedback(new_labeled_data, args.alpha)
            print("\n--- 최종 언론사 가중치 ---")
            final_source_ranking, final_author_ranking = model.get_rankings()
            print(final_source_ranking)
            print("\n\n--- 최종 기자별 가중치 ---")
            print(final_author_ranking)
            model.save_weights_to_csv()
        except Exception as e:
            print(f"피드백 데이터 처리 중 오류: {e}")
    else:
        print(f"\n[INFO] 학습할 피드백 데이터가 없습니다. '{FEEDBACK_FOLDER}' 폴더를 확인해주세요.")