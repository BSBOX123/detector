# E:\workspace\News_API\crawler.py

import requests
from bs4 import BeautifulSoup
import logging
from urllib.parse import urlparse
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

SITE_SPECIFIC_SELECTORS = {
    'news.naver.com': ['#dic_area', '#artice_body', '#articleBodyContents'],
    'v.daum.net': ['.article_view', '#harmonyContainer'], 'news.daum.net': ['.article_view', '#harmonyContainer'],
    'www.chosun.com': ['.news_body_area', '.article-body'], 'joongang.joins.com': ['#article_body'],
    'www.donga.com': ['#article_content'], 'www.hani.co.kr': ['.article-text', '#article_text'],
    'www.khan.co.kr': ['div.art_body'], 'www.mk.co.kr': ['#art_txt'], 'www.hankyung.com': ['#articletxt'],
    'www.ytn.co.kr': ['div.article__content'], 'www.sbs.co.kr': ['.article_content', 'div.text_area'],
    'imnews.imbc.com': ['.news_content'], 'kbs.co.kr': ['div.article-body'], 'newsis.com': ['div.article_content'],
    'yonhapnews.co.kr': ['#articleBody'], 'zdnet.co.kr': ['#bodyLayer'], 'bloter.net': ['div.article-content'],
    'www.etnews.com': ['#articleBody'], 'www.fnnews.com': ['.ar_txt'], 'www.nocutnews.co.kr': ['div.article_body'],
    'www.pressian.com': ['article.article-body'],
}

GENERAL_SELECTORS = [
    'article', 'div#article-body', 'div#article_body', 'div.article_body', 'div.article-veiw-body',
    'div#newsct_article', 'div.text', 'div.story-news', 'div.contents_area', 'div.view_content',
    'div.news_content', 'div.entry-content', 'div.post-content', 'div.post_content_area',
    'div[itemprop="articleBody"]'
]

AUTHOR_SELECTORS = [
    '.reporter_info .name', '.journalist_name', '.byline_area', 
    '.author', '.writer', 'span.name', '.j_info'
]

def crawl_article(url):
    """URL을 통해 뉴스 기사 본문과 기자 이름을 크롤링합니다."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        page = requests.get(url, headers=headers, timeout=10)
        page.raise_for_status()
        soup = BeautifulSoup(page.text, 'html.parser')

        # --- 1. 본문 찾기 ---
        domain = urlparse(url).netloc
        selectors_to_try = SITE_SPECIFIC_SELECTORS.get(domain, []) + GENERAL_SELECTORS
        
        content_body = None
        for selector in selectors_to_try:
            content_body = soup.select_one(selector)
            if content_body:
                break
        
        article_text = '[본문 없음]'
        if content_body:
            for tag in content_body.find_all(['script', 'style', 'ins', 'blockquote', 'figure', 'figcaption', '.journalist_info', '.related_articles']):
                tag.decompose()
            article_text = content_body.get_text(strip=True, separator=' ')
        else:
            # 최후의 수단으로 p 태그 합치기
            paragraphs = soup.find_all('p')
            article_text = ' '.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])

        # --- 2. 기자 이름 찾기 ---
        author_name = '[기자 정보 없음]'
        for selector in AUTHOR_SELECTORS:
            author_element = soup.select_one(selector)
            if author_element:
                full_name = author_element.get_text(strip=True)
                match = re.search(r'([가-힣]{2,5})\s*(기자|특파원|논설위원|앵커|객원기자)', full_name)
                if match:
                    author_name = match.group(1).strip()
                    break
        
        if not article_text.strip():
            article_text = '[본문 없음]'
            
        return article_text, author_name

    except requests.RequestException as e:
        logging.error(f"본문 크롤링 요청 실패 - URL: {url} / 오류: {e}")
        return "[본문 없음]", "[기자 정보 없음]"
    except Exception as e:
        logging.error(f"본문 파싱 실패 - URL: {url} / 오류: {e}", exc_info=True)
        return "[본문 없음]", "[기자 정보 없음]"