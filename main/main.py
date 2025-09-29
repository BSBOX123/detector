# E:\workspace\main\main.py

import sys
import os
import subprocess

# --- 설정: 각 기능별 모듈 및 스크립트 경로 ---
# 현재 main.py 파일이 있는 디렉토리의 부모 디렉토리 (E:\workspace)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 각 스크립트의 절대 경로
TRAINER_SCRIPT = os.path.join(BASE_DIR, 'model', 'tokken', 'model_trainer.py')
JUDGER_RUNNER_SCRIPT = os.path.join(BASE_DIR, 'model', 'tokken', 'run_judgement.py')

def run_module_as_script(module_path, script_name):
    """지정된 모듈을 스크립트처럼 실행하는 헬퍼 함수 (e.g., python -m News_API.main)"""
    print(f"\n--- 🚀 '{script_name}' 작업을 시작합니다 ---")
    try:
        # sys.executable은 현재 파이썬 인터프리터 경로
        # '-m' 플래그는 모듈을 스크립트로 실행
        # cwd를 프로젝트의 최상위 폴더(workspace)로 설정하여 모듈 경로를 찾을 수 있도록 함
        subprocess.run([sys.executable, '-m', module_path], check=True, text=True, cwd=BASE_DIR)
        print(f"--- ✅ '{script_name}' 작업이 성공적으로 완료되었습니다 ---")
    except subprocess.CalledProcessError as e:
        print(f"\n[오류] '{script_name}' 작업 실행 중 오류가 발생했습니다: {e}")
    except Exception as e:
        print(f"\n[오류] '{script_name}' 작업 실행 중 예기치 않은 예외가 발생했습니다: {e}")

def run_simple_script(script_path, script_name):
    """독립적인 스크립트를 실행하는 헬퍼 함수."""
    if not os.path.exists(script_path):
        print(f"\n[오류] 스크립트 파일을 찾을 수 없습니다: {script_path}")
        return
    print(f"\n--- 🚀 '{script_name}' 작업을 시작합니다 ---")
    try:
        script_dir = os.path.dirname(script_path)
        subprocess.run([sys.executable, script_path], check=True, text=True, cwd=script_dir)
        print(f"--- ✅ '{script_name}' 작업이 성공적으로 완료되었습니다 ---")
    except subprocess.CalledProcessError as e:
        print(f"\n[오류] '{script_name}' 작업 실행 중 오류가 발생했습니다: {e}")
    except Exception as e:
        print(f"\n[오류] '{script_name}' 작업 실행 중 예기치 않은 예외가 발생했습니다: {e}")

if __name__ == '__main__':
    while True:
        print("\n" + "#"*60)
        print("실행할 작업을 선택해주세요:")
        print("  1: 뉴스 데이터 수집 및 가공 (from News_API)")
        print("  2: 모델 학습 (from model/tokken)")
        print("  3: 가짜뉴스 판별기 실행 (from model/tokken)")
        print("  q: 종료")
        choice = input("선택 (1, 2, 3, q): ")
        print("#"*60)
        
        if choice == '1':
            # 'News_API' 패키지 안의 'main' 모듈을 실행
            run_module_as_script('News_API.main', "뉴스 데이터 수집 및 가공")
        elif choice == '2':
            # 이 스크립트들은 독립적이므로 간단히 실행
            run_simple_script(TRAINER_SCRIPT, "모델 학습")
        elif choice == '3':
            # 이 스크립트들은 독립적이므로 간단히 실행
            run_simple_script(JUDGER_RUNNER_SCRIPT, "가짜뉴스 판별기")
        elif choice.lower() == 'q':
            print("프로그램을 종료합니다.")
            break
        else:
            print("잘못된 입력입니다. 다시 선택해주세요.")