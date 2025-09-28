# config.py

# API Keys
NEWS_API_KEY = 'a86133a2e6ca476cb12a1c3021ed5f60'  # News API키 입력.
GEMINI_API_KEY = 'AIzaSyDg7i_gIs8kx25CFYQn00DDcrLGKohCtHk' # Google AI Studio키 입력.

# News API Parameters
QUERY = '정부 OR 경제 OR 사회 OR IT OR 과학 OR 문화'
LANGUAGE = 'ko'
SOURCES = None
SORT_BY = 'publishedAt'
PAGE_SIZE = 100

# File Paths
SAVE_FOLDER_PATH = r'E:\workspace\News_API\articles' # 저장할 폴더 경로

BATCH_SIZE = 30  # 한 번에 처리할 기사 수