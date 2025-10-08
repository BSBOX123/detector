# E:\workspace\News_API\config.py

import os
from dotenv import load_dotenv

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.join(CURRENT_DIR, '..')
DOTENV_PATH = os.path.join(ROOT_DIR, '.env')

if os.path.exists(DOTENV_PATH):
    load_dotenv(dotenv_path=DOTENV_PATH)
else:
    print(f"[경고] .env 파일을 찾을 수 없습니다: {DOTENV_PATH}")

class Config:
    NEWS_API_KEY = os.getenv('NEWS_API_KEY', 'YOUR_NEWS_API_KEY_DEFAULT')
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'YOUR_GEMINI_API_KEY_DEFAULT')

    QUERIES = [
        '정치', '선거', '국회', '경제', '금리', '부동산', '주식', 
        '사회', '사건사고', '노동', 'IT', 'AI', '반도체', '플랫폼',
        '과학', '우주', '기후변화', '문화', '영화', '음악', '미술'
    ]
    LANGUAGE = os.getenv('NEWS_LANGUAGE', 'ko')
    
    _sources_from_env = os.getenv('NEWS_SOURCES')
    SOURCES = _sources_from_env if _sources_from_env and _sources_from_env.lower() != 'none' else None

    SORT_BY = os.getenv('NEWS_SORT_BY', 'publishedAt')
    PAGE_SIZE = int(os.getenv('NEWS_PAGE_SIZE', 100))

    _default_save_path = os.path.join(CURRENT_DIR, 'articles')
    SAVE_FOLDER_PATH = os.getenv('SAVE_FOLDER_PATH', _default_save_path)

    BATCH_SIZE = int(os.getenv('BATCH_SIZE', 30))
    BATCH_DELAY_SECONDS = int(os.getenv('BATCH_DELAY_SECONDS', 61))

config = Config()