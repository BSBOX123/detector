# crawler.py

import requests
from bs4 import BeautifulSoup

def crawl_article_text(url):
    "URL을 통해 뉴스 기사 크롤링 "
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        page = requests.get(url, headers=headers, timeout=10)
        page.raise_for_status()
        soup = BeautifulSoup(page.text, 'html.parser')

        # 한국 주요 언론사들의 기사 본문 영역에 대한 CSS 선택자 리스트
        selectors = [
            'article',
            'div#article-body',
            'div#article_body',
            'div.article_body',
            'div.article-veiw-body',
            'div#newsct_article',
            'div.text',
            'div.story-news'
        ]
        
        content_body = None
        for selector in selectors:
            content_body = soup.select_one(selector)
            if content_body:
                break
        
        if not content_body:
            paragraphs = soup.find_all('p')
            text = ' '.join([p.get_text(strip=True) for p in paragraphs])
        else:
            text = content_body.get_text(strip=True, separator=' ')

        return text if text else '[본문 없음]'
    
    except requests.RequestException as e:
        print(f"[Error] 본문 크롤링 요청 실패 - URL: {url} / 오류: {e}")
        return "[본문 없음]"
    except Exception as e:
        print(f"[Error] 본문 파싱 실패 - URL: {url} / 오류: {e}")
        return "[본문 없음]"