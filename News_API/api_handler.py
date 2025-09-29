# E:\workspace\News_API\api_handler.py

import requests
import google.generativeai as genai
from .config import config # config 객체를 상대 경로로 import
import logging
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type, RetryError

# Gemini 모델 초기화
try:
    if config.GEMINI_API_KEY and config.GEMINI_API_KEY != 'YOUR_GEMINI_API_KEY_DEFAULT':
        genai.configure(api_key=config.GEMINI_API_KEY)
        model = genai.GenerativeModel(model_name="gemini-2.5-pro")
    else:
        model = None
except Exception as e:
    logging.error(f"Gemini 모델 설정 중 오류 발생: {e}")
    model = None

@retry(
    wait=wait_exponential(multiplier=1, min=2, max=8),
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type(requests.exceptions.RequestException),
    before_sleep=lambda retry_state: logging.info(f"Retrying News API call in {retry_state.next_action.sleep:.1f}s as it raised {retry_state.outcome.exception()}...")
)
def _fetch_articles_with_retry_logic(params):
    url = 'https://newsapi.org/v2/everything'
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def fetch_articles(query, language, sources, sort_by, page_size):
    params = {
        'q': query, 'language': language, 'sortBy': sort_by,
        'pageSize': page_size, 'apiKey': config.NEWS_API_KEY
    }
    if sources:
        params['sources'] = sources

    try:
        data = _fetch_articles_with_retry_logic(params)
        return data.get('articles', [])
    except RetryError as e:
        underlying_exception = e.last_attempt.exception
        if isinstance(underlying_exception, requests.exceptions.HTTPError):
            logging.error(f"[News API 오류] HTTPError 발생. Status: {underlying_exception.response.status_code}. 서버 응답: {underlying_exception.response.text}")
        logging.error(f"[News API 오류] News API 호출 최종 실패: {e}")
        return []
    except Exception as e:
        logging.error(f"[News API 오류] News API 호출 중 예기치 않은 오류: {e}", exc_info=True)
        return []

def generate_fake_version(real_text):
    if not model:
        logging.warning("Gemini 모델이 준비되지 않아 가짜뉴스 생성을 건너뜁니다.")
        return '[가짜뉴스 생성 실패: 모델 미설정]'
    if not real_text or real_text == '[본문 없음]':
        return '[가짜뉴스 생성 실패: 원본 본문 없음]'

    try:
        prompt = f"""
        당신은 사실과 허구를 교묘하게 섞어, 서론-본론-결론 구조를 갖춘 그럴듯한 가짜뉴스를 작성하는 AI 저널리스트입니다.
        아래 원본 기사의 핵심 인물, 장소, 기관명, 사건을 사용하되, 사건의 경과나 결과, 숨겨진 동기 등을 왜곡하고 과장하여 
        사람들이 진짜 기사로 착각할 만한 가짜뉴스를 '최소 3문단 이상'으로 구성된 하나의 완성된 기사 형태로 작성해주세요.

        --- 원본 기사 ---
        {real_text}
        """
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.8, max_output_tokens=3072
            )
        )
        if response.parts:
            return response.text.strip()
        else:
            return f"[가짜뉴스 생성 실패] Finish Reason: {response.candidates[0].finish_reason.name if response.candidates else 'Unknown'}"
    except Exception as e:
        logging.error(f"가짜뉴스 생성 API 호출 실패: {e}", exc_info=True)
        return '[가짜뉴스 생성 실패]'