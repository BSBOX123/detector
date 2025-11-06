# E:\workspace\News_API\api_handler.py

import requests
import google.generativeai as genai
# config.py에서 'config' 객체를 상대 경로로 import 합니다.
from .config import config
import logging
import re # 정규표현식(줄바꿈 제거)을 위해 추가

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
    
    if sources:
        params['sources'] = sources
    if from_date:
        params['from'] = from_date
    if to_date:
        params['to'] = to_date

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json().get('articles', [])
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 426 or e.response.status_code == 400:
             logging.warning(f"[News API 경고] {e.response.status_code} - {e.response.json().get('message')}")
        else:
             logging.error(f"[News API 오류] HTTPError 발생. Status: {e.response.status_code}. 서버 응답: {e.response.text}")
        return []
    except requests.exceptions.RequestException as e:
        logging.error(f"[News API 오류] News API 호출 실패: {e}")
        return []


"'진짜 뉴스를 기반으로 가짜 뉴스 생성 (제목과 본문 분리)"
def generate_fake_version(real_text):
    if not model:
        logging.warning("Gemini 모델이 준비되지 않아 가짜뉴스 생성을 건너뜁니다.")
        return '[가짜뉴스 생성 실패: 모델 미설정]', '[가짜뉴스 생성 실패: 모델 미설정]'
    if not real_text or real_text == '[본문 없음]':
        return '[가짜뉴스 생성 실패: 원본 본문 없음]', '[가짜뉴스 생성 실패: 원본 본문 없음]'

    try:
        # --- (핵심 수정 1) 프롬프트 수정 ---
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
        
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.8,
                max_output_tokens=3072
            ),
            request_options={"timeout": 30} # 30초 타임아웃
        )
        
        # --- (핵심 수정 2) 응답 파싱 로직 ---
        if response.parts:
            raw_text = response.text.strip()
            fake_title = "[가짜생성] (제목 파싱 실패)" # 기본값
            fake_body = raw_text # 기본값
            
            # 제목과 본문 분리 시도
            if '## ' in raw_text:
                try:
                    # '## '로 시작하는 제목 줄과 나머지 본문으로 분리
                    parts = raw_text.split('\n', 1) # 첫 번째 줄바꿈에서만 분리
                    title_line = parts[0].strip()
                    
                    if title_line.startswith('## '):
                        fake_title = title_line.replace('## ', '').strip() # '## ' 제거
                        fake_body = parts[1].strip() if len(parts) > 1 else "[본문 생성 실패]"
                    else:
                        # '## '가 첫 줄에 없으면, 그냥 전체를 본문으로
                        fake_body = raw_text
                        
                except Exception as e:
                    logging.warning(f"Gemini 응답 파싱 실패 (제목/본문 분리): {e}")
                    fake_body = raw_text # 실패 시 전체를 본문으로
            else:
                # '## ' 마커가 없는 경우 (LLM이 지시를 따르지 않음)
                logging.warning("Gemini 응답에 '## ' 제목 마커가 없습니다.")
                fake_body = raw_text
            
            # 본문 클린업 (혹시 모를 마커 제거, 줄바꿈을 공백으로)
            markers_to_remove = ['[서론]', '[본론]', '[결론]', '**[서론]**', '**[본론]**', '**[결론]**', '## ']
            for marker in markers_to_remove:
                fake_body = fake_body.replace(marker, '')
            
            # 여러 줄바꿈(단락 구분)을 공백 한 칸으로 변경
            fake_body = re.sub(r'\n+', ' ', fake_body).strip()
            
            return fake_title, fake_body
        
        else:
            fail_reason = f"[가짜뉴스 생성 실패] Finish Reason: {response.candidates[0].finish_reason.name if response.candidates else 'Unknown'}"
            return f"[가짜생성] ({fail_reason})", fail_reason
            
    except Exception as e:
        logging.error(f"가짜뉴스 생성 API 호출 실패: {e}", exc_info=True)
        fail_reason = f"[가짜뉴스 생성 실패: {e.__class__.__name__}]"
        return f"[가짜생성] ({fail_reason})", fail_reason