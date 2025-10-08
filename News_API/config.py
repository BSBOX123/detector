# E:\workspace\News_API\config.py

import os
from dotenv import load_dotenv

# 현재 config.py 파일이 있는 디렉토리
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# News_API 폴더의 부모 디렉토리
ROOT_DIR = os.path.join(CURRENT_DIR, '..')
# .env 파일의 절대 경로
DOTENV_PATH = os.path.join(ROOT_DIR, '.env')

# .env 파일을 로드할 때 정확한 경로를 명시
if os.path.exists(DOTENV_PATH):
    load_dotenv(dotenv_path=DOTENV_PATH)
else:
    print(f"[경고] .env 파일을 찾을 수 없습니다: {DOTENV_PATH}")

class Config:
    # 환경 변수에서 API 키를 로드합니다. 없으면 기본값을 사용합니다.
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

    # .env의 'None' 문자열을 실제 None 객체로 변환 ***
    _sources_from_env = os.getenv('NEWS_SOURCES')
    SOURCES = _sources_from_env if _sources_from_env and _sources_from_env.lower() != 'none' else None

    SORT_BY = os.getenv('NEWS_SORT_BY', 'publishedAt')
    PAGE_SIZE = int(os.getenv('NEWS_PAGE_SIZE', 100))

    # File Paths
    _default_save_path = os.path.join(CURRENT_DIR, 'articles')
    SAVE_FOLDER_PATH = os.getenv('SAVE_FOLDER_PATH', _default_save_path)

    BATCH_SIZE = int(os.getenv('BATCH_SIZE', 30))
    BATCH_DELAY_SECONDS = int(os.getenv('BATCH_DELAY_SECONDS', 61))

# 다른 모듈에서 'from .config import config'로 접근할 수 있도록 인스턴스화
config = Config()