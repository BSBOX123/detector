# E:\workspace\News_API\config.py

import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

# --- .env 파일 로드 ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.join(CURRENT_DIR, '..')
DOTENV_PATH = os.path.join(ROOT_DIR, '.env')

if os.path.exists(DOTENV_PATH):
    load_dotenv(dotenv_path=DOTENV_PATH)
else:
    print(f"[경고] .env 파일을 찾을 수 없습니다: {DOTENV_PATH}")

# --- 날짜 범위 동적 생성 ---
# News API는 30일 전까지만 지원합니다.
# 4주간의 데이터를 1주 단위로 나눕니다.
today = datetime.now() # 현재 시간 기준
DATE_RANGES_TO_SCAN = [
    # 1주차 (오늘 ~ 7일 전)
    {
        "from_date": (today - timedelta(days=7)).strftime('%Y-%m-%dT%H:%M:%S'),
        "to_date": today.strftime('%Y-%m-%dT%H:%M:%S')
    },
    # 2주차 (8일 전 ~ 14일 전)
    {
        "from_date": (today - timedelta(days=14)).strftime('%Y-%m-%dT%H:%M:%S'),
        "to_date": (today - timedelta(days=8)).strftime('%Y-%m-%dT%H:%M:%S')
    },
    # 3주차 (15일 전 ~ 21일 전)
    {
        "from_date": (today - timedelta(days=21)).strftime('%Y-%m-%dT%H:%M:%S'),
        "to_date": (today - timedelta(days=15)).strftime('%Y-%m-%dT%H:%M:%S')
    },
    # 4주차 (22일 전 ~ 28일 전)
    {
        "from_date": (today - timedelta(days=28)).strftime('%Y-%m-%dT%H:%M:%S'),
        "to_date": (today - timedelta(days=22)).strftime('%Y-%m-%dT%H:%M:%S')
    }
]

class Config:
    NEWS_API_KEY = os.getenv('NEWS_API_KEY', 'YOUR_NEWS_API_KEY_DEFAULT')
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'YOUR_GEMINI_API_KEY_DEFAULT')

    # News API Parameters
    QUERIES = [
        '정치', '선거', '국회',             # 정치
        '경제', '금리', '부동산', '주식',   # 경제
        '사회', '사건사고', '노동',         # 사회
        'IT', 'AI', '반도체', '플랫폼',    # IT/기술
        '과학', '우주', '기후변화',         # 과학
        '문화', '영화', '음악', '미술'      # 문화
    ]
    LANGUAGE = os.getenv('NEWS_LANGUAGE', 'ko')
    
    _sources_from_env = os.getenv('NEWS_SOURCES')
    SOURCES = _sources_from_env if _sources_from_env and _sources_from_env.lower() != 'none' else None

    SORT_BY = os.getenv('NEWS_SORT_BY', 'publishedAt')
    PAGE_SIZE = int(os.getenv('NEWS_PAGE_SIZE', 100))
    PAGE_LIMIT = int(os.getenv('PAGE_LIMIT', 2)) # 각 쿼리+날짜 범위당 최대 2페이지까지 수집

    # File Paths
    SAVE_FOLDER_PATH = os.path.join(CURRENT_DIR, 'articles')

    BATCH_SIZE = int(os.getenv('BATCH_SIZE', 30))
    BATCH_DELAY_SECONDS = int(os.getenv('BATCH_DELAY_SECONDS', 61))

# 다른 모듈에서 'from .config import config'로 접근할 수 있도록 인스턴스화
config = Config()