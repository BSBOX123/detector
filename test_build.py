from konlpy.tag import Okt
from collections import Counter

# --- 설정 ---
# 불용어 리스트 (필요에 따라 추가/수정)
# 한국어에서 의미 없이 자주 쓰이는 단어들을 정의합니다.
STOPWORDS = ['의','가','이','은','들','는','좀','잘','걍','과','도','를','으로','자','에','와','한','하다',
             '이다', '있다', '없다', '되다', '않다', '그렇다', '아니다', '보다', '같다', '싶다', '주다', '받다',
             '이다', '되다', '않다', '없다', '있다', '주다', '것', '수', '고', '때문', '위해', '통해', '이번', '지난', '말', '명']

# --- 1. 텍스트 전처리 및 토큰화 함수 정의 ---
okt = Okt() # 형태소 분석기 초기화

def tokenize_and_count_words(text):
    """
    주어진 텍스트를 형태소 분석하여 명사, 동사, 형용사만 추출하고
    불용어를 제거한 뒤, 각 단어의 빈도를 계산하여 반환하는 함수.
    """
    if not isinstance(text, str): # 텍스트가 문자열이 아닌 경우 처리
        print(f"경고: 유효하지 않은 텍스트 타입입니다. ({type(text)})")
        return Counter() # 빈 Counter 객체 반환
        
    # 명사, 동사, 형용사만 추출하고 어간(stem) 처리
    morphs = okt.pos(text, stem=True) # 어간 추출 (예: '달리고' -> '달리다')
    
    words = []
    for word, tag in morphs:
        # 명사, 동사, 형용사만 추출 (더 넓은 범위의 품사를 원하면 리스트에 추가)
        # 한 글자 단어 중 의미 없는 것들을 제외하기 위해 len(word) > 1 조건 추가
        if tag in ['Noun', 'Verb', 'Adjective'] and word not in STOPWORDS and len(word) > 1:
            words.append(word)
            
    # 단어들의 빈도 계산
    word_counts = Counter(words)
    
    return word_counts

# ======================================================================
# --- 메인 실행 로직 ---
# ======================================================================
if __name__ == "__main__":
    # --- 1. 샘플 뉴스 기사 정의 ---
    sample_news_article_1 = "정부가 오늘 새로운 부동산 정책을 발표했다. 시민들의 반응은 엇갈리고 있으며, 전문가들은 신중한 접근이 필요하다고 조언했다."
    sample_news_article_2 = "충격적인 소식! 유명 연예인의 비밀이 폭로되었다. 이는 사회 전반에 큰 파장을 불러올 것으로 예상된다."
    sample_news_article_3 = "최근 연구에 따르면, 인공지능 기술이 빠르게 발전하면서 우리의 일상에 큰 변화를 가져올 것이라는 전망이 나왔다."
    
    print("--- 뉴스 기사 1 분석 ---")
    counts1 = tokenize_and_count_words(sample_news_article_1)
    print(f"총 단어 수: {sum(counts1.values())}")
    print("가장 많이 사용된 단어들:")
    # 상위 10개 단어와 빈도 출력
    for word, count in counts1.most_common(10):
        print(f"  - {word}: {count}회")

    print("\n--- 뉴스 기사 2 분석 ---")
    counts2 = tokenize_and_count_words(sample_news_article_2)
    print(f"총 단어 수: {sum(counts2.values())}")
    print("가장 많이 사용된 단어들:")
    for word, count in counts2.most_common(10):
        print(f"  - {word}: {count}회")

    print("\n--- 뉴스 기사 3 분석 ---")
    counts3 = tokenize_and_count_words(sample_news_article_3)
    print(f"총 단어 수: {sum(counts3.values())}")
    print("가장 많이 사용된 단어들:")
    for word, count in counts3.most_common(10):
        print(f"  - {word}: {count}회")

    # 모든 샘플 기사들을 합쳐서 분석할 수도 있습니다.
    all_articles_text = sample_news_article_1 + " " + sample_news_article_2 + " " + sample_news_article_3
    print("\n--- 모든 뉴스 기사 통합 분석 ---")
    all_counts = tokenize_and_count_words(all_articles_text)
    print(f"총 단어 수: {sum(all_counts.values())}")
    print("가장 많이 사용된 단어들:")
    for word, count in all_counts.most_common(20): # 상위 20개 단어 출력
        print(f"  - {word}: {count}회")