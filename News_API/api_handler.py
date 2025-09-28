# api_handler.py

import requests
import google.generativeai as genai
from config import GEMINI_API_KEY, NEWS_API_KEY

try:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(model_name="gemini-2.5-pro") 
    print("Gemini 모델이 성공적으로 준비되었습니다.")
except Exception as e:
    print(f"모델 설정 중 오류 발생: {e}")
    model = None


"기사 가져오기"
def fetch_articles(query, language, sources, sort_by, page_size):
    url = 'https://newsapi.org/v2/everything'
    params = {'q': query, 'language': language, 'sources': sources, 'sortBy': sort_by, 'pageSize': page_size, 'apiKey': NEWS_API_KEY}
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json().get('articles', [])


"'진짜 뉴스를 기반으로 가짜 뉴스 생성"
def generate_fake_version(real_text):
    if not model or not real_text or real_text == '[본문 없음]':
        return '[가짜뉴스 생성 실패]'

    try:
        "gemini에게 넘길 프롬포트"
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
                temperature=0.8,
                max_output_tokens=3072
            )
        )
        
        if response.parts:
            return response.text.strip()
        else:
            return f"[가짜뉴스 생성 실패] Finish Reason: {response.candidates[0].finish_reason.name}"
            
    except Exception as e:
        print(f"가짜뉴스 생성 API 호출 실패: {e}")
        return '[가짜뉴스 생성 실패]'