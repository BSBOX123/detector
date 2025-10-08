# E:\workspace\News_API\crawler.py

import requests
from bs4 import BeautifulSoup
import logging
from urllib.parse import urlparse # URL 파싱을 위해 추가

# 로깅 설정 (News_API/main.py 또는 config에서 한번 설정되어도, 각 모듈에 설정하는 것이 안전)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- 사이트별 맞춤 선택자 정의 ---
# 도메인을 key로, 해당 도메인에서 기사 본문을 찾을 수 있는 CSS 선택자 리스트를 value로.
# 우선순위가 높은(더 정확한) 선택자를 앞에 배치하는 것이 좋다.
SITE_SPECIFIC_SELECTORS = {
    # 포털 사이트 
    'news.naver.com': ['#dic_area', '#artice_body', '#articleBodyContents'], # 네이버 뉴스
    'v.daum.net': ['.article_view', '#harmonyContainer'],                     # 다음 뉴스
    'news.daum.net': ['.article_view', '#harmonyContainer'],                  # 다음 뉴스 (구 버전)
    
    # 주요 언론사
    'www.chosun.com': ['.news_body_area', '.article-body'],                   # 조선일보
    'joongang.joins.com': ['#article_body'],                                  # 중앙일보
    'www.donga.com': ['#article_content'],                                    # 동아일보
    'www.hani.co.kr': ['.article-text', '#article_text'],                     # 한겨레
    'www.khan.co.kr': ['div.art_body'],                                       # 경향신문
    'www.mk.co.kr': ['#art_txt'],                                             # 매일경제
    'www.hankyung.com': ['#articletxt'],                                      # 한국경제
    'www.ytn.co.kr': ['div.article__content'],                                # YTN
    'www.sbs.co.kr': ['.article_content', 'div.text_area'],                   # SBS 뉴스
    'imnews.imbc.com': ['.news_content'],                                     # MBC 뉴스
    'kbs.co.kr': ['div.article-body'],                                        # KBS 뉴스
    'newsis.com': ['div.article_content'],                                    # 뉴시스
    'yonhapnews.co.kr': ['#articleBody'],                                     # 연합뉴스
    'zdnet.co.kr': ['#bodyLayer'],                                            # ZDNet Korea
    'bloter.net': ['div.article-content'],                                    # 블로터
    'techcrunch.com': ['.article-content'],                                   # TechCrunch (영문이지만 참고용)
    'www.etnews.com': ['#articleBody'],                                       # 전자신문
    'www.fnnews.com': ['.ar_txt'],                                            # 파이낸셜뉴스
    'www.nocutnews.co.kr': ['div.article_body'],                              # 노컷뉴스
    'www.pressian.com': ['article.article-body'],                             # 프레시안

    # 기타 일반적인 본문 선택자 (어떤 언론사에도 통할 수 있는 범용적인 선택자)
    'default': [
        'article',
        'div#article-body', 'div#article_body', 'div.article_body',
        'div.article-veiw-body', 'div#newsct_article', 'div.text',
        'div.story-news', 'div.contents_area', 'div.view_content',
        'div.news_content', 'div.entry-content', 'div.post-content',
        'div.post_content_area', 'div[itemprop="articleBody"]',
        'p' # 최후의 수단으로 모든 p 태그를 합침
    ]
}


def crawl_article_text(url):
    """
    URL을 통해 뉴스 기사를 크롤링하고 본문 텍스트를 반환.
    다양한 언론사의 구조에 대응하기 위해 CSS 선택자를 활용.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        # URL에서 도메인 추출
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        
        # 해당 도메인에 특화된 선택자를 가져오고, 없으면 기본 선택자를 사용
        selectors_to_try = SITE_SPECIFIC_SELECTORS.get(domain, []) + SITE_SPECIFIC_SELECTORS['default']
        
        page = requests.get(url, headers=headers, timeout=10)
        page.raise_for_status() # HTTP 오류가 발생하면 예외 발생
        soup = BeautifulSoup(page.text, 'html.parser')

        content_body = None
        for selector in selectors_to_try:
            # 'p'는 특별하게 처리 (최후의 수단)
            if selector == 'p':
                if not content_body: # 다른 선택자로 찾지 못했을 때만 p 태그 시도
                    paragraphs = soup.find_all('p')
                    text_parts = [p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)]
                    text = ' '.join(text_parts)
                    if text:
                        logging.debug(f"크롤링 성공 (p 태그 fallback): {url}")
                        return text
                continue # 'p' 태그는 여기서 처리했으므로 다음 선택자로 넘어감

            content_body = soup.select_one(selector)
            if content_body:
                # 불필요한 요소 제거 (예: 광고, 기자 이름, 관련 기사 링크 등)
                for useless_tag in content_body.find_all(['script', 'style', 'ins', 'blockquote', 'figure', 'figcaption', '.journalist_info', '.related_articles']):
                    useless_tag.decompose() # 태그와 내용을 제거
                
                text = content_body.get_text(strip=True, separator=' ')
                if text:
                    logging.debug(f"크롤링 성공: {url} (selector: {selector})")
                    return text

        logging.warning(f"크롤링 실패: {url} (모든 선택자로 본문 내용 찾을 수 없음)")
        return '[본문 없음]'
    
    except requests.exceptions.RequestException as e:
        logging.error(f"[Error] 본문 크롤링 요청 실패 - URL: {url} / 오류: {e}")
        return "[본문 없음]"
    except Exception as e:
        logging.error(f"[Error] 본문 파싱 실패 - URL: {url} / 오류: {e}", exc_info=True)
        return "[본문 없음]"