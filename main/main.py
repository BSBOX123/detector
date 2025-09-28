# E:\workspace\main\main.py

# ... (기존 상단 import 및 함수 정의들은 그대로 유지) ...

# ==========================================================
#  가짜뉴스 판별 모듈 통합
# ==========================================================
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed # for run_data_collection
import time #
import os
import pandas as pd

# 'tokken' 패키지가 있는 부모 디렉토리를 파이썬 경로에 추가
# 이 경로를 정확하게 확인하고 수정해주세요.
MODEL_BASE_PATH = r'E:\workspace\model' 
sys.path.append(MODEL_BASE_PATH)

# 경로 추가 후, tokken 패키지 안의 news_judger 모듈에서 judge_article 함수를 가져옵니다.
try:
    from tokken.news_judger import judge_article
    judger_available = True
except ImportError as e:
    print(f"\n[경고] 'tokken' 패키지 또는 'news_judger' 모듈을 불러올 수 없습니다. 경로('{MODEL_BASE_PATH}')와 파일 존재 여부를 확인해주세요. 오류: {e}")
    judger_available = False
except FileNotFoundError as e:
    print(f"\n[경고] {e}") # 가중치 파일이 없을 때의 오류 메시지 출력
    judger_available = False
except Exception as e:
    print(f"\n[경고] 판별 모듈 초기화 중 예기치 않은 오류 발생: {e}")
    judger_available = False

def run_interactive_judgement():
    """
    사용자로부터 뉴스 기사 본문을 입력받아 가짜뉴스 점수를 판별하는 함수.
    """
    if not judger_available:
        print("판별 기능을 사용할 수 없습니다. 경로 또는 가중치 파일을 확인해주세요.")
        return

    print("\n--- 📰 가짜뉴스 판별기를 시작합니다 ---")
    print("분석할 뉴스 기사 본문을 입력해주세요 (종료하려면 'exit' 입력)")

    while True:
        print("\n" + "="*50)
        # 여러 줄 입력을 받을 수 있도록 개선
        print(">>> 기사 본문 입력 (입력 완료 후 엔터를 두 번 누르세요):")
        lines = []
        while True:
            line = input()
            if not line:
                break
            lines.append(line)
        news_text = "\n".join(lines)
        
        if news_text.strip().lower() == 'exit':
            print("프로그램을 종료합니다.")
            break
        
        if not news_text.strip():
            print("내용이 없습니다. 다시 입력해주세요.")
            continue
            
        try:
            result = judge_article(news_text)
            
            print("\n--- 📝 뉴스 판별 결과 ---")
            print(f"가짜뉴스 점수: {result['score']} / 100")
            print(f"판단: {result['judgement']} (기준 점수: {result['threshold']}점)")
            
            if result['found_keywords']:
                print(f"발견된 주요 키워드: {', '.join(result['found_keywords'])}")
            else:
                print("발견된 주요 키워드: 없음")
                
        except Exception as e:
            print(f"판별 중 오류가 발생했습니다: {e}")


# ==========================================================
#  기존의 run_data_collection 함수와 if __name__ == '__main__': 부분은 그대로 유지
#    (이 부분은 제공해 주신 main.py 파일에서 가져온 것입니다.)
# ==========================================================

# 주의: 아래 run_data_collection 함수는 이전 대화에서 main.py에 추가해야 했던
# News API 데이터 수집 및 가공 로직입니다. 이 함수는 실제 main.py에 이미
# 정의되어 있어야 합니다. 여기서는 편의상 다시 포함했습니다.
# 만약 main.py의 원래 내용 중 fetch_articles, process_article, save_articles_to_csv, config 등이
# 정의되어 있지 않다면 해당 정의들을 main.py에 추가해야 합니다.
# (이전에 main.py의 전체 내용을 보여주시지 않아 정확한 통합은 어려우므로,
# 여러분의 main.py 원본에 아래 내용을 잘 통합해야 합니다.)

# (이 부분은 여러분의 main.py 파일에 이미 정의되어 있는 것으로 가정합니다.)
# from src.news_collector import NewsCollector
# from src.news_processor import NewsProcessor
# from config import Config # config 모듈을 임포트했다고 가정

# 임시 config 및 함수 정의 (여러분의 실제 main.py 내용에 맞춰주세요)
class TempConfig:
    QUERY = "가짜뉴스"
    LANGUAGE = 'ko'
    SOURCES = None
    SORT_BY = 'relevancy'
    PAGE_SIZE = 10
    BATCH_SIZE = 5
    SAVE_FOLDER_PATH = r'E:\workspace\News_API\articles' # CSV 저장 경로
    
config = TempConfig() # 임시 설정 객체


def process_article(article):
    # 실제로는 LLM으로 요약하고 가짜뉴스를 생성하는 로직이 들어갑니다.
    real_record = {
        'source_name': article['source']['name'],
        'title': article['title'],
        'description': article['description'],
        '기사본문': article['description'], # 이 컬럼명이 CSV에 있어야 합니다.
        'label': 1, # 진짜 뉴스
        'keywords': '키워드1,키워드2',
        'sentiment': '긍정'
    }
    fake_record = {
        'source_name': article['source']['name'],
        'title': f"[가짜뉴스] {article['title']}",
        'description': f"충격적인 {article['description']}에 대한 가짜 주장입니다. 속보! 경악할 소식! 단독입수!",
        '기사본문': f"충격적인 {article['description']}에 대한 가짜 주장입니다. 속보! 경악할 소식! 단독입수!", # 이 컬럼명이 CSV에 있어야 합니다.
        'label': 0, # 가짜 뉴스
        'keywords': '가짜,뉴스,루머',
        'sentiment': '부정'
    }
    return [real_record, fake_record]

def save_articles_to_csv(articles, query, save_path):
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = os.path.join(save_path, f"dataset_{timestamp}.csv")
    df = pd.DataFrame(articles)
    df.to_csv(filename, index=False, encoding='utf-8-sig')
    print(f"--- CSV 파일 저장 완료: {filename} ---")


if __name__ == '__main__':
    while True:
        print("\n" + "#"*60)
        print("실행할 작업을 선택해주세요:")
        print("  1: 뉴스 데이터 수집 및 가공 (CSV 생성)")
        print("  2: 가짜뉴스 판별기 실행")
        print("  q: 종료")
        choice = input("선택 (1, 2, q): ")
        print("#"*60)
        
        if choice == '1':
            run_interactive_judgement()
            break
        elif choice.lower() == 'q':
            print("프로그램을 종료합니다.")
            break
        else:
            print("잘못된 입력입니다. 다시 선택해주세요.")