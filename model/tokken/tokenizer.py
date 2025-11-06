# E:\workspace\model\tokken\tokenizer.py

from konlpy.tag import Okt

# Okt 객체는 생성 시 시간이 걸리므로, 전역 변수로 한 번만 생성합니다.
okt = Okt()

def okt_tokenizer(text):
    """KoNLPy Okt 형태소 분석기를 사용한 토크나저 (명사만 추출)"""
    if not isinstance(text, str):
        return []
    nouns = okt.nouns(text)
    # 두 글자 이상 명사만 반환
    return [noun for noun in nouns if len(noun) > 1]