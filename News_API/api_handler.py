# E:\workspace\News_API\api_handler.py

import requests
import google.generativeai as genai
from .config import config # config 객체를 상대 경로로 import
import logging
import re # 정규표현식(줄바꿈 제거)을 위해 추가
import time
# tenacity (재시도 라이브러리) import
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type, RetryError
import google.api_core.exceptions

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

# --- News API 호출 ---
@retry(
    wait=wait_exponential(multiplier=1, min=2, max=8),
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type(requests.exceptions.RequestException),
    before_sleep=lambda retry_state: logging.info(f"Retrying News API call in {retry_state.next_action.sleep:.1f}s as it raised {retry_state.outcome.exception()}...")
)
def _fetch_articles_with_retry_logic(params):
    url = 'https://newsapi.org/v2/everything'
    response = requests.get(url, params=params)
    response.raise_for_status() # 4xx, 5xx 에러 발생 시 HTTPError 예외 발생
    return response.json()

"기사 가져오기"
def fetch_articles(query, language, sources, sort_by, page_size, from_date=None, to_date=None, page=1):
    url = 'https://newsapi.org/v2/everything'
    
    params = {
        'q': query,
        'language': language,
        'sortBy': sort_by,
        'pageSize': page_size,
        'apiKey': config.NEWS_API_KEY,
        'page': page
    }
    
    # *** (중요) sources가 유효할 때만 파라미터에 추가 ***
    if sources:
        params['sources'] = sources
    if from_date:
        params['from'] = from_date
    if to_date:
        params['to'] = to_date

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

# --- Gemini API 호출 ---
@retry(
    wait=wait_exponential(multiplier=1, min=2, max=10), 
    stop=stop_after_attempt(3), 
    retry=retry_if_exception_type((google.api_core.exceptions.DeadlineExceeded, 
                                   google.api_core.exceptions.ResourceExhausted,
                                   ValueError)),
    before_sleep=lambda retry_state: logging.warning(f"Retrying Gemini API call in {retry_state.next_action.sleep:.1f}s as it raised {retry_state.outcome.exception()}...")
)
def _generate_fake_version_with_retry(prompt):
    """재시도 로직이 적용된 Gemini API 호출 함수"""
    response = model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(
            temperature=0.8,
            max_output_tokens=3072
        ),
        request_options={"timeout": 120} # 120초(2분) 타임아웃
    )
    
    if not response.parts:
        raise ValueError(f"Gemini 응답 실패: Finish Reason: {response.candidates[0].finish_reason.name if response.candidates else 'Unknown'}")
    
    return response.text.strip()


"'진짜 뉴스를 기반으로 가짜 뉴스 생성 (제목과 본문 분리)"
def generate_fake_version(real_text):
    if not model:
        logging.warning("Gemini 모델이 준비되지 않아 가짜뉴스 생성을 건너뜁니다.")
        return '[가짜뉴스 생성 실패: 모델 미설정]', '[가짜뉴스 생성 실패: 모델 미설정]'
    if not real_text or real_text == '[본문 없음]':
        return '[가짜뉴스 생성 실패: 원본 본문 없음]', '[가짜뉴스 생성 실패: 원본 본문 없음]'

    try:
        prompt = f"""
        당신은 사실과 허구를 교묘하게 섞어, 그럴듯한 가짜뉴스를 작성하는 AI 저널리스트입니다.
        아래 원본 기사를 기반으로, 매우 자극적이고 선정적인 가짜뉴스 '제목'과 '본문'을 생성해주세요.

        [작성 규칙]
        1. 맨 첫 줄에는 반드시 '## ' (띄어쓰기 포함) 기호로 시작하는 '가짜뉴스 제목'을 생성해야 합니다.
        2. 제목 다음 줄부터 '가짜뉴스 본문'을 작성합니다.
        3. 본문은 [서론], [본론], [결론] 같은 표식을 **절대 사용하지 마세요.**
        4. 본문은 단락 구분을 위한 줄바꿈(enter) 없이 **하나의 연속된 통문단으로 작성**해주세요.
        5. 원본 기사의 핵심 인물, 장소, 사건 등을 왜곡하고 과장해야 합니다.

        --- 원본 기사 ---
        {real_text}
        """
        
        # 재시도 로직이 적용된 함수 호출
        raw_text = _generate_fake_version_with_retry(prompt)
        
        fake_title = "[가짜생성] (제목 파싱 실패)"
        fake_body = raw_text
        
        if '## ' in raw_text:
            try:
                parts = raw_text.split('\n', 1)
                title_line = parts[0].strip()
                if title_line.startswith('## '):
                    fake_title = title_line.replace('## ', '').strip()
                    fake_body = parts[1].strip() if len(parts) > 1 else "[본문 생성 실패]"
                else:
                    fake_body = raw_text
            except Exception as e:
                logging.warning(f"Gemini 응답 파싱 실패 (제목/본문 분리): {e}")
                fake_body = raw_text
        else:
            logging.warning("Gemini 응답에 '## ' 제목 마커가 없습니다.")
            fake_body = raw_text
        
        markers_to_remove = ['[서론]', '[본론]', '[결론]', '**[서론]**', '**[본론]**', '**[결론]**', '## ']
        for marker in markers_to_remove:
            fake_body = fake_body.replace(marker, '')
        
        fake_body = re.sub(r'\n+', ' ', fake_body).strip()
        
        return fake_title, fake_body
            
    except (RetryError, Exception) as e:
        logging.error(f"가짜뉴스 생성 API 호출 최종 실패: {e}", exc_info=True)
        fail_reason = f"[가짜뉴스 생성 실패: {e.__class__.__name__}]"
        return f"[가짜생성] ({fail_reason})", fail_reason