# E:\workspace\main\main.py

import sys
import os
import subprocess

# --- 설정 ---
# 현재 main.py 파일의 부모 디렉토리 (E:\workspace)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 프로젝트의 최상위 폴더(workspace)를 파이썬 경로에 추가
sys.path.append(BASE_DIR)

# --- 모듈 임포트 ---
try:
    # 'util'은 workspace 폴더 아래의 패키지로 인식됩니다.
    from util import dataset_manager
except ImportError:
    print(f"[오류] util.dataset_manager 모듈을 찾을 수 없습니다. E:\\workspace\\util\\dataset_manager.py 파일과 E:\\workspace\\util\\__init__.py 파일이 있는지 확인해주세요.")
    dataset_manager = None

# 각 스크립트의 절대 경로
COLLECTOR_SCRIPT = os.path.join(BASE_DIR, 'News_API', 'main.py')
TRAINER_SCRIPT = os.path.join(BASE_DIR, 'model', 'tokken', 'model_trainer.py')
JUDGER_RUNNER_SCRIPT = os.path.join(BASE_DIR, 'model', 'tokken', 'run_judgement.py')
ARTICLES_PATH = os.path.join(BASE_DIR, 'News_API', 'articles')
SPLITTER_SCRIPT = os.path.join(BASE_DIR, 'util', 'data_splitter.py')

# ==========================================================
#  헬퍼 함수 정의 (if __name__ == '__main__' 보다 위에 위치)
# ==========================================================

def run_splitter_with_selection():
    """사용자에게 데이터셋을 선택받아 분할 스크립트를 실행합니다."""
    if not dataset_manager: return

    datasets = dataset_manager.get_datasets()
    # 이미 분할된 _train.csv, _test.csv 파일은 목록에서 제외
    datasets = [f for f in datasets if '_train.csv' not in f and '_test.csv' not in f]
    
    if not datasets:
        print("\n[알림] 분할할 데이터셋이 없습니다.")
        return
        
    dataset_manager.display_datasets(datasets)
    
    try:
        choice_str = input("분할할 데이터셋 번호를 입력하세요 (취소: Enter): ")
        if not choice_str:
            print("데이터셋 분할을 취소했습니다.")
            return
        choice_idx = int(choice_str) - 1
        
        if 0 <= choice_idx < len(datasets):
            selected_file = datasets[choice_idx]
            selected_filepath = os.path.join(ARTICLES_PATH, selected_file)
            
            print(f"\n--- 🚀 '데이터셋 분할' 작업을 시작합니다 ({selected_file}) ---")
            subprocess.run([sys.executable, SPLITTER_SCRIPT, '--file', selected_filepath], check=True, text=True)
            print(f"--- ✅ '데이터셋 분할' 작업이 성공적으로 완료되었습니다 ---")
        else:
            print("[오류] 잘못된 번호를 입력했습니다.")
    except (ValueError, subprocess.CalledProcessError, Exception) as e:
        print(f"\n[오류] 작업 실행 중 오류가 발생했습니다: {e}")

def run_module_as_script(module_path, script_name):
    """지정된 모듈을 스크립트처럼 실행하는 헬퍼 함수 (e.g., python -m News_API.main)"""
    print(f"\n--- '{script_name}' 작업을 시작합니다 ---")
    try:
        # cwd를 프로젝트의 최상위 폴더(workspace)로 설정하여 모듈 경로를 찾을 수 있도록 함
        subprocess.run([sys.executable, '-m', module_path], check=True, text=True, cwd=BASE_DIR)
        print(f"--- '{script_name}' 작업이 성공적으로 완료되었습니다 ---")
    except subprocess.CalledProcessError as e:
        print(f"\n[오류] '{script_name}' 작업 실행 중 오류가 발생했습니다: {e}")
    except Exception as e:
        print(f"\n[오류] 예기치 않은 예외가 발생했습니다: {e}")

def run_simple_script(script_path, script_name):
    """독립적인 스크립트를 실행하는 헬퍼 함수."""
    if not os.path.exists(script_path):
        print(f"\n[오류] 스크립트 파일을 찾을 수 없습니다: {script_path}")
        return
        
    print(f"\n--- '{script_name}' 작업을 시작합니다 ---")
    try:
        script_dir = os.path.dirname(script_path)
        script_filename = os.path.basename(script_path)
        subprocess.run([sys.executable, script_filename], check=True, text=True, cwd=script_dir)
        print(f"--- '{script_name}' 작업이 성공적으로 완료되었습니다 ---")
    except subprocess.CalledProcessError as e:
        print(f"\n[오류] '{script_name}' 작업 실행 중 오류가 발생했습니다: {e}")
    except Exception as e:
        print(f"\n[오류] 예기치 않은 예외가 발생했습니다: {e}")

def run_trainer_with_selection():
    """사용자에게 데이터셋을 선택받아 모델 학습 스크립트를 실행합니다."""
    if not dataset_manager: return

    datasets = dataset_manager.get_datasets()
    if not datasets:
        print("\n[알림] 학습할 데이터셋이 없습니다. 먼저 뉴스 데이터를 수집해주세요.")
        return
        
    dataset_manager.display_datasets(datasets)
    
    try:
        choice_str = input("학습에 사용할 데이터셋 번호를 입력하세요 (취소: Enter): ")
        if not choice_str:
            print("모델 학습을 취소했습니다.")
            return
        choice_idx = int(choice_str) - 1
        
        if 0 <= choice_idx < len(datasets):
            selected_file = datasets[choice_idx]
            selected_filepath = os.path.join(ARTICLES_PATH, selected_file)
            
            print(f"\n--- '모델 학습' 작업을 시작합니다 ({selected_file}) ---")
            # trainer 스크립트에 '--file' 인자로 선택된 파일 경로를 전달
            subprocess.run([sys.executable, TRAINER_SCRIPT, '--file', selected_filepath], check=True, text=True)
            print(f"--- '모델 학습' 작업이 성공적으로 완료되었습니다 ---")
        else:
            print("[오류] 잘못된 번호를 입력했습니다.")
    except ValueError:
        print("[오류] 숫자만 입력해주세요.")
    except subprocess.CalledProcessError as e:
        print(f"\n[오류] '모델 학습' 작업 실행 중 오류가 발생했습니다: {e}")
    except Exception as e:
        print(f"\n[오류] 예기치 않은 예외가 발생했습니다: {e}")

def manage_datasets():
    """데이터셋 관리 메뉴를 표시하고 관련 기능을 실행합니다."""
    if not dataset_manager: return

    while True:
        datasets = dataset_manager.get_datasets()
        dataset_manager.display_datasets(datasets)
        
        print("\n--- 데이터셋 관리 메뉴 ---")
        print("  1: 데이터셋 병합 (Merge)")
        print("  2: 데이터셋 삭제 (Delete)")
        print("  b: 이전 메뉴로 돌아가기")
        choice = input("선택: ")
        
        if choice == '1':
            selection_str = input("병합할 데이터셋 번호를 쉼표(,)로 구분하여 입력하세요 (예: 1,3,4): ")
            try:
                selected_indices = [int(i.strip()) - 1 for i in selection_str.split(',')]
                dataset_manager.merge_datasets(selected_indices, datasets)
            except ValueError:
                print("[오류] 숫자와 쉼표만 사용하여 올바르게 입력해주세요.")
        elif choice == '2':
            selection_str = input("삭제할 데이터셋 번호를 쉼표(,)로 구분하여 입력하세요 (예: 2,5): ")
            try:
                selected_indices = [int(i.strip()) - 1 for i in selection_str.split(',')]
                confirm = input(f"정말로 선택한 {len(selected_indices)}개 파일을 삭제하시겠습니까? (y/N): ")
                if confirm.lower() == 'y':
                    dataset_manager.delete_datasets(selected_indices, datasets)
                else:
                    print("삭제를 취소했습니다.")
            except ValueError:
                print("[오류] 숫자와 쉼표만 사용하여 올바르게 입력해주세요.")
        elif choice.lower() == 'b':
            break
        else:
            print("잘못된 입력입니다.")

# ==========================================================
#  메인 실행 로직
# ==========================================================
if __name__ == '__main__':
    while True:
        print("\n" + "#"*60)
        print("실행할 작업을 선택해주세요:")
        print("  1: 뉴스 데이터 수집 및 가공")
        print("  2: 모델 학습")
        print("  3: 가짜뉴스 판별기 실행")
        print("  4: 데이터셋 관리 (병합/삭제)")
        print("  5: 데이터셋 분할 (학습/평가용)") # 메뉴 추가
        print("  q: 종료")
        choice = input("선택 (1, 2, 3, 4, 5, q): ")
        print("#"*60)
        
        if choice == '1':
            run_module_as_script('News_API.main', "뉴스 데이터 수집 및 가공")
        elif choice == '2':
            run_trainer_with_selection()
        elif choice == '3':
            run_simple_script(JUDGER_RUNNER_SCRIPT, "가짜뉴스 판별기")
        elif choice == '4':
            manage_datasets()
        elif choice == '5': # 메뉴 연결
            run_splitter_with_selection()
        elif choice.lower() == 'q':
            print("프로그램을 종료합니다.")
            break
        else:
            print("잘못된 입력입니다.")
