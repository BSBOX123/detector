import pandas as pd
from konlpy.tag import Okt
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle # 키워드 딕셔너리를 저장하고 불러오기 위해 추가

# --- 설정 ---
# 불용어 리스트 (필요에 따라 추가/수정)
# 한국어에서 의미 없이 자주 쓰이는 단어들을 정의합니다.
STOPWORDS = ['의','가','이','은','들','는','좀','잘','걍','과','도','를','으로','자','에','와','한','하다',
             '이다', '있다', '없다', '되다', '않다', '그렇다', '아니다', '보다', '같다', '싶다', '주다', '받다',
             '이다', '되다', '않다', '없다', '있다', '주다', '것', '수', '고', '때문', '위해', '통해']

# 가짜 뉴스 키워드 딕셔너리를 저장할 파일명
KEYWORDS_FILE = 'fake_news_keywords.pkl'

# --- 1. 텍스트 전처리 함수 정의 ---
okt = Okt() # 형태소 분석기 초기화

def preprocess_text(text):
    """
    형태소 분석 및 불용어 제거를 수행하는 함수
    - 명사, 동사, 형용사만 추출하고 어간(stem) 처리
    - 정의된 불용어 제거
    """
    if not isinstance(text, str): # 텍스트가 문자열이 아닌 경우 처리
        return ""
        
    morphs = okt.pos(text, stem=True) # 어간 추출 (예: '달리고' -> '달리다')
    words = []
    for word, tag in morphs:
        # 명사, 동사, 형용사만 추출 (더 넓은 범위의 품사를 원하면 리스트에 추가)
        if tag in ['Noun', 'Verb', 'Adjective'] and word not in STOPWORDS and len(word) > 1: # 한 글자 단어 제외
            words.append(word)
    return ' '.join(words)

# --- 2. 가짜 뉴스 키워드 학습 및 저장 함수 ---
def train_and_save_keywords(dataframe, keywords_file=KEYWORDS_FILE, top_n=50):
    """
    가짜 뉴스 데이터를 기반으로 TF-IDF 키워드를 학습하고 파일로 저장하는 함수.
    :param dataframe: 'text' 컬럼과 'label' 컬럼(1:가짜, 0:진짜)을 포함하는 DataFrame.
    :param keywords_file: 키워드 딕셔너리를 저장할 파일 경로.
    :param top_n: TF-IDF 점수가 높은 상위 N개의 키워드를 추출.
    :return: 추출된 키워드 딕셔너리.
    """
    print("--- 2. 가짜 뉴스 키워드 학습 시작 ---")
    fake_news_df = dataframe[dataframe['label'] == 1]
    if fake_news_df.empty:
        print("가짜 뉴스 데이터가 없습니다. 키워드를 추출할 수 없습니다.")
        return {}

    # 가짜 뉴스 텍스트에 전처리 적용
    fake_news_corpus = [preprocess_text(text) for text in fake_news_df['text']]
    
    # 빈 문자열 제거 (전처리 후 아무 단어도 남지 않은 경우)
    fake_news_corpus = [doc for doc in fake_news_corpus if doc.strip()]

    if not fake_news_corpus:
        print("전처리 후 가짜 뉴스 데이터에 유효한 문서가 없습니다. 키워드를 추출할 수 없습니다.")
        return {}

    # TF-IDF 벡터화 객체 생성
    # min_df=2: 최소 2개 문서에 등장하는 단어만 포함 (너무 희귀한 단어 제외)
    # ngram_range=(1, 2): 단어 1개(unigram) 또는 2개(bigram)를 한 묶음으로 고려
    tfidf_vectorizer = TfidfVectorizer(min_df=2, ngram_range=(1, 2))

    # 가짜 뉴스 코퍼스를 기반으로 TF-IDF 행렬 계산
    tfidf_matrix = tfidf_vectorizer.fit_transform(fake_news_corpus)

    # 단어(피처)와 TF-IDF 점수 매핑
    feature_names = tfidf_vectorizer.get_feature_names_out()
    # 각 단어의 총 TF-IDF 점수 합계 (가짜 뉴스 문서 전체에서의 중요도)
    word_scores = tfidf_matrix.sum(axis=0).tolist()[0]
    
    # 단어와 점수를 딕셔너리로 만듦
    # 점수가 너무 낮은 키워드는 제외할 수 있도록 필터링 (선택 사항)
    raw_keywords_with_scores = {word: score for word, score in zip(feature_names, word_scores) if score > 0.1}

    # 점수가 높은 순으로 정렬하여 상위 N개 키워드 추출
    sorted_keywords = sorted(raw_keywords_with_scores.items(), key=lambda x: x[1], reverse=True)
    fake_news_keywords = {word: score for word, score in sorted_keywords[:top_n]}

    # 추출된 키워드를 파일로 저장
    with open(keywords_file, 'wb') as f:
        pickle.dump(fake_news_keywords, f)
    print(f"--- 가짜 뉴스 핵심 키워드 {len(fake_news_keywords)}개 저장 완료 ({keywords_file}) ---")
    print(fake_news_keywords)
    return fake_news_keywords

# --- 3. 저장된 키워드를 불러오는 함수 ---
def load_keywords(keywords_file=KEYWORDS_FILE):
    """
    파일에서 가짜 뉴스 키워드 딕셔너리를 불러오는 함수.
    """
    try:
        with open(keywords_file, 'rb') as f:
            keywords = pickle.load(f)
        print(f"--- 키워드 딕셔너리 불러오기 성공 ({keywords_file}) ---")
        return keywords
    except FileNotFoundError:
        print(f"--- 오류: 키워드 파일 '{keywords_file}'을 찾을 수 없습니다. 학습을 먼저 진행해주세요. ---")
        return None
    except Exception as e:
        print(f"--- 오류: 키워드 파일 불러오기 실패: {e} ---")
        return None

# --- 4. 새로운 뉴스에 대한 점수화 함수 ---
def calculate_fake_news_score(news_text, keywords_dict):
    """
    새로운 뉴스 텍스트와 키워드 딕셔너리를 받아 가짜뉴스 점수를 계산하는 함수.
    :param news_text: 분석할 뉴스 기사 텍스트.
    :param keywords_dict: '가짜 뉴스'를 대표하는 키워드와 그 가중치 딕셔너리.
    :return: 0점에서 100점 사이의 가짜뉴스 점수 (높을수록 가짜 뉴스일 가능성 높음).
    """
    if not keywords_dict:
        print("경고: 키워드 딕셔너리가 비어 있습니다. 0점을 반환합니다.")
        return 0.0

    # 입력된 뉴스 텍스트 전처리
    processed_text = preprocess_text(news_text)
    
    # 점수 계산: 기사에 포함된 키워드의 가중치 합산
    total_score = 0.0
    found_keywords = []
    
    # 키워드 딕셔너리의 모든 키워드에 대해 확인
    for keyword, weight in keywords_dict.items():
        # 키워드가 전처리된 텍스트에 포함되어 있는지 확인
        # f' {keyword} ' 로 감싸는 이유는 '핵심'이 '핵심적' 같은 다른 단어의 일부로 인식되는 것을 방지하기 위함
        if f' {keyword} ' in f' {processed_text} ':
            total_score += weight
            found_keywords.append(keyword)
            
    # 점수 정규화 (0~100점 사이로 변환)
    # 모든 키워드의 최대 가중치 합을 구하여 정규화 기준으로 사용
    max_possible_score = sum(keywords_dict.values())
    
    normalized_score = 0.0
    if max_possible_score > 0:
        normalized_score = (total_score / max_possible_score) * 100
        # 점수가 100점을 넘지 않도록 상한선 설정 (예외 케이스 방지)
        if normalized_score > 100:
            normalized_score = 100.0
    
    print(f"\n--- 뉴스 분석 결과 ---")
    print(f"원문: {news_text[:50]}...") # 긴 텍스트의 경우 앞부분만 표시
    print(f"전처리 후: {processed_text[:50]}...")
    print(f"발견된 가짜 뉴스 키워드: {', '.join(found_keywords) if found_keywords else '없음'}")
    print(f"최종 가짜 뉴스 점수: {normalized_score:.2f} / 100 점")
    
    return normalized_score

# ======================================================================
# --- 메인 실행 로직 ---
# ======================================================================
if __name__ == "__main__":
    # --- 1. 예시 데이터 준비 (실제 데이터셋으로 대체 필요) ---
    data = {
        'text': [
            '정부, 내년도 예산안 전격 발표... 경제 성장률 3% 전망', # 진짜 뉴스 (0)
            '국내 연구진, 암 치료하는 신물질 개발 성공', # 진짜 뉴스 (0)
            '대한민국 정치권 비상!! 대통령의 충격적인 비밀 자금 발견돼...', # 가짜 뉴스 (1)
            '속보) 유명 아이돌 그룹 멤버, 사실은 외계인이었다는 충격적인 소식!', # 가짜 뉴스 (1)
            '주식 시장, 알려지지 않은 세력의 개입으로 곧 붕괴 예정이라는 소문 확산', # 가짜 뉴스 (1)
            '세계은행, 한국 경제 안정적으로 평가... 물가 관리가 관건', # 진짜 뉴스 (0)
            '놀라운 일이 벌어졌다! 전 세계가 주목하는 최신 기술의 등장!', # 가짜 뉴스 (1)
            '단독입수) 충격! 비트코인 투자자들 돈 잃고 울고 있다! 긴급 사태 발생!', # 가짜 뉴스 (1)
            '미국 연방준비제도, 기준금리 0.25% 인상 결정', # 진짜 뉴스 (0)
            '알파고, 바둑 챔피언 이세돌 9단에게 4:1 승리 거둬', # 진짜 뉴스 (0)
            '경악! 인공지능이 인간 지배할 날이 머지 않았다... 충격적인 미래 예측 공개', # 가짜 뉴스 (1)
            '루머 확산, 정부 고위 관계자 긴급 체포 임박! 진실은 무엇인가?', # 가짜 뉴스 (1)
        ],
        'label': [0, 0, 1, 1, 1, 0, 1, 1, 0, 0, 1, 1]
    }
    df = pd.DataFrame(data)

    print("\n---------- 초기 데이터 ----------")
    for idx, row in df.iterrows():
        print(f"[{'가짜' if row['label']==1 else '진짜'}] {row['text'][:30]}...")

    # --- 2. 가짜 뉴스 키워드 학습 및 저장 ---
    # 데이터셋의 가짜 뉴스(label=1)를 사용하여 키워드를 학습하고 저장합니다.
    # 이 과정은 한 번만 실행하면 됩니다.
    learned_keywords = train_and_save_keywords(df, top_n=30) # 상위 30개 키워드 추출

    # --- 3. (옵션) 저장된 키워드를 다시 불러와서 사용 ---
    # 실제 애플리케이션에서는 학습된 키워드 파일을 불러와서 사용합니다.
    # 만약 위에서 학습 과정을 이미 실행했다면, 이 부분을 주석 처리하거나
    # `if learned_keywords is None:`과 같이 조건부로 실행할 수 있습니다.
    loaded_keywords = load_keywords()

    if loaded_keywords: # 키워드를 성공적으로 불러왔다면
        print("\n--- 4. 새로운 뉴스 기사에 대한 점수 계산 테스트 ---")

        test_article_1 = "대통령의 숨겨진 비밀 자금이 발견되었다는 충격적인 소식이 전해졌다. 이는 곧 긴급 사태로 이어질 수 있다."
        test_article_2 = "오늘 오후, 서울시청에서 새로운 복지 정책에 대한 설명회가 열렸다. 시민들의 삶의 질 향상에 기여할 것으로 보인다."
        test_article_3 = "속보! 놀라운 사건 발생! 유명 연예인의 재산이 전부 몰수되었다는 루머가 확산되고 있다!"
        test_article_4 = "최신 연구에 따르면, 꾸준한 운동이 심혈관 질환 예방에 효과적이다."
        test_article_5 = "경악할 만한 사실! 정부의 은밀한 계획이 폭로되다. 과연 진실은 무엇인가?"

        print("\n\n=== 테스트 기사 1 ===")
        calculate_fake_news_score(test_article_1, loaded_keywords)

        print("\n\n=== 테스트 기사 2 ===")
        calculate_fake_news_score(test_article_2, loaded_keywords)
        
        print("\n\n=== 테스트 기사 3 ===")
        calculate_fake_news_score(test_article_3, loaded_keywords)

        print("\n\n=== 테스트 기사 4 ===")
        calculate_fake_news_score(test_article_4, loaded_keywords)

        print("\n\n=== 테스트 기사 5 ===")
        calculate_fake_news_score(test_article_5, loaded_keywords)
    else:
        print("\n--- 키워드를 불러오지 못하여 점수 계산 테스트를 건너뜝니다. ---")