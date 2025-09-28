# run_judgement.py

from news_judger import judge_article

def main():
    print("--- 📰 가짜뉴스 판별기를 시작합니다 ---")
    print("분석할 뉴스 기사 본문을 입력해주세요 (종료하려면 'exit' 입력)")

    while True:
        print("\n" + "="*50)
        news_text = input(">>> 기사 본문 입력: ")
        
        if news_text.lower() == 'exit':
            print("프로그램을 종료합니다.")
            break
        
        if not news_text.strip():
            print("내용이 없습니다. 다시 입력해주세요.")
            continue
            
        try:
            result = judge_article(news_text)
            
            print("\n--- 📝 뉴스 판별 결과 ---")
            print(f"가짜뉴스 점수: {result['score']} / 100")
            print(f"판단: {result['judgement']} (기준 점수: {result['threshold']}점)")
            
            if result['found_keywords']:
                print(f"발견된 주요 키워드: {', '.join(result['found_keywords'])}")
            else:
                print("발견된 주요 키워드: 없음")
                
        except FileNotFoundError as e:
            print(e)
            print("프로그램을 종료합니다.")
            break
        except Exception as e:
            print(f"판별 중 오류가 발생했습니다: {e}")


if __name__ == '__main__':
    main()