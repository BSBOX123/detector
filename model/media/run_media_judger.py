# E:\workspace\model\media\run_media_judger.py

import sys
sys.path.append('.') 
from media_judger import judge_media_score

def main():
    print("--- 📰 출처 신뢰도(Media) 판별기를 시작합니다 ---")
    print("분석할 뉴스 정보를 입력해주세요 (종료하려면 'exit' 입력)")

    try:
        judge_media_score(" ", " ") 
    except FileNotFoundError as e:
        print(f"\n[오류] {e}")
        return
        
    while True:
        print("\n" + "="*50)
        source_name = input(">>> 언론사 입력: ")
        if source_name.lower() == 'exit': break
        
        author_name = input(">>> 기자 이름 입력 (모르면 '모름'): ")
        if author_name.lower() == 'exit': break

        if not all([source_name.strip(), author_name.strip()]):
            print("언론사와 기자 이름을 모두 입력해야 합니다.")
            continue
            
        try:
            result = judge_media_score(source_name, author_name)
            
            print("\n--- 📝 출처 신뢰도 분석 결과 ---")
            print(f"  - 신뢰도 점수: {result['score']} / 100")
            print(f"  - (참고) 언론사 점수: {result['source_score']:.4f}, 기자 점수: {result['author_score']:.4f}")

        except Exception as e:
            print(f"\n[오류] 판별 중 오류가 발생했습니다: {e}")

if __name__ == '__main__':
    main()