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
    from util import dataset_manager
except ImportError:
    print(f"[오류] util.dataset_manager 모듈을 찾을 수 없습니다.")
    dataset_manager = None

# 각 스크립트의 절대 경로
COLLECTOR_SCRIPT = os.path.join(BASE_DIR, 'News_API', 'main.py')
TOKKEN_TRAINER_SCRIPT = os.path.join(BASE_DIR, 'model', 'tokken', 'model_trainer.py')
MEDIA_TRAINER_SCRIPT = os.path.join(BASE_DIR, 'model', 'media', 'media_score.py')
TOKKEN_JUDGER_SCRIPT = os.path.join(BASE_DIR, 'model', 'tokken', 'run_judgement.py')
MEDIA_JUDGER_SCRIPT = os.path.join(BASE_DIR, 'model', 'media', 'run_media_judger.py')
INTEGRATED_JUDGER_SCRIPT = os.path.join(BASE_DIR, 'model', 'tokken', 'integrated_judger.py')
ARTICLES_PATH = os.path.join(BASE_DIR, 'News_API', 'articles')
FEEDBACK_PATH = os.path.join(BASE_DIR, 'model', 'media', 'feedback_data')

# ==========================================================
#  헬퍼 함수 정의
# ==========================================================
def run_module_as_script(module_path, script_name):
    """지정된 모듈을 스크립트처럼 실행합니다 (e.g., python -m News_API.main)"""
    print(f"\n--- 🚀 '{script_name}' 작업을 시작합니다 ---")
    try:
        subprocess.run([sys.executable, '-m', module_path], check=True, text=True, cwd=BASE_DIR)
        print(f"--- ✅ '{script_name}' 작업이 성공적으로 완료되었습니다 ---")
    except (subprocess.CalledProcessError, Exception) as e:
        print(f"\n[오류] '{script_name}' 작업 실행 중 오류가 발생했습니다: {e}")

def run_simple_script(script_path, script_name):
    """독립적인 스크립트를 실행합니다."""
    if not os.path.exists(script_path):
        print(f"\n[오류] 스크립트 파일을 찾을 수 없습니다: {script_path}")
        return
    print(f"\n--- 🚀 '{script_name}' 작업을 시작합니다 ---")
    try:
        script_dir = os.path.dirname(script_path)
        script_filename = os.path.basename(script_path)
        subprocess.run([sys.executable, script_filename], check=True, text=True, cwd=script_dir)
        print(f"--- ✅ '{script_name}' 작업이 성공적으로 완료되었습니다 ---")
    except (subprocess.CalledProcessError, Exception) as e:
        print(f"\n[오류] '{script_name}' 작업 실행 중 오류가 발생했습니다: {e}")

def run_tokken_trainer():
    """Tokken 모델 학습을 실행합니다."""
    if not dataset_manager: return
    datasets = [f for f in dataset_manager.get_datasets() if not f.startswith('feedback_template')]
    if not datasets:
        print("\n[알림] 학습할 데이터셋이 없습니다.")
        return
    dataset_manager.display_datasets(datasets)
    try:
        choice_str = input("학습에 사용할 데이터셋 번호를 입력하세요 (취소: Enter): ")
        if not choice_str: return
        choice_idx = int(choice_str) - 1
        if 0 <= choice_idx < len(datasets):
            selected_filepath = os.path.join(ARTICLES_PATH, datasets[choice_idx])
            print(f"\n--- 🚀 'Tokken 모델 학습' 작업을 시작합니다 ({datasets[choice_idx]}) ---")
            subprocess.run([sys.executable, TOKKEN_TRAINER_SCRIPT, '--file', selected_filepath], check=True, text=True)
            print(f"--- ✅ 'Tokken 모델 학습' 작업이 성공적으로 완료되었습니다 ---")
        else:
            print("[오류] 잘못된 번호를 입력했습니다.")
    except (ValueError, subprocess.CalledProcessError, Exception) as e:
        print(f"\n[오류] 작업 실행 중 오류가 발생했습니다: {e}")

def run_media_trainer():
    """Media 모델 학습을 실행합니다."""
    if not dataset_manager: return
    feedback_files = [f for f in os.listdir(FEEDBACK_PATH) if f.endswith('.csv') and not f.startswith('feedback_template')]
    if not feedback_files:
        print(f"\n[알림] 학습할 피드백 데이터가 없습니다. '{FEEDBACK_PATH}' 폴더에 라벨링된 CSV 파일을 넣어주세요.")
        return
    print("\n--- 💾 사용 가능한 피드백 데이터 목록 ---")
    for i, filename in enumerate(feedback_files): print(f"  [{i+1}] {filename}")
    print("-" * 35)
    
    try:
        choice_str = input("학습에 사용할 피드백 파일 번호를 입력하세요 (최신 파일: Enter): ")
        alpha_str = input("ALPHA 값을 입력하세요 (0.0~1.0, 기본값 0.7: Enter): ")
        alpha_val = float(alpha_str) if alpha_str else 0.7

        cmd = [sys.executable, MEDIA_TRAINER_SCRIPT, '--alpha', str(alpha_val)]
        
        selected_file = "최신 파일"
        if choice_str:
            choice_idx = int(choice_str) - 1
            if 0 <= choice_idx < len(feedback_files):
                selected_filepath = os.path.join(FEEDBACK_PATH, feedback_files[choice_idx])
                cmd.extend(['--file', selected_filepath])
                selected_file = feedback_files[choice_idx]
            else:
                print("[오류] 잘못된 번호를 입력했습니다.")
                return
        
        print(f"\n--- 🚀 'Media 모델 학습' 작업을 시작합니다 ({selected_file}, ALPHA={alpha_val}) ---")
        subprocess.run(cmd, check=True, text=True)
        print(f"--- ✅ 'Media 모델 학습' 작업이 성공적으로 완료되었습니다 ---")
    except (ValueError, subprocess.CalledProcessError, Exception) as e:
        print(f"\n[오류] 작업 실행 중 오류가 발생했습니다: {e}")

def manage_datasets():
    """데이터셋 관리 메뉴를 실행합니다."""
    if not dataset_manager: return
    while True:
        datasets = dataset_manager.get_datasets()
        dataset_manager.display_datasets(datasets)
        
        print("\n--- 🛠️ 데이터셋 관리 메뉴 ---")
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


def run_splitter_with_selection():
    """데이터셋 분할 기능을 실행합니다."""
    if not dataset_manager: return

    datasets = dataset_manager.get_datasets()
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
            subprocess.run([sys.executable, os.path.join(BASE_DIR, 'util', 'data_splitter.py'), '--file', selected_filepath], check=True, text=True)
            print(f"--- ✅ '데이터셋 분할' 작업이 성공적으로 완료되었습니다 ---")
        else:
            print("[오류] 잘못된 번호를 입력했습니다.")
    except (ValueError, subprocess.CalledProcessError, Exception) as e:
        print(f"\n[오류] 작업 실행 중 오류가 발생했습니다: {e}")

# ==========================================================
#  메인 실행 로직
# ==========================================================
if __name__ == '__main__':
    while True:
        print("\n" + "#"*60)
        print("실행할 작업을 선택해주세요:")
        print("  1: 뉴스 데이터 수집 및 가공")
        print("\n--- 모델 학습 ---")
        print("  2: [Tokken] 텍스트 분석 모델 학습")
        print("  3: [Media] 출처 신뢰도 모델 학습")
        print("\n--- 가짜뉴스 판별 ---")
        print("  4: [Tokken] 텍스트 기반 판별")
        print("  5: [Media] 출처 기반 판별")
        print("  6: [통합] 최종 판별기 실행")
        print("\n--- 데이터 관리 ---")
        print("  7: 데이터셋 관리 (병합/삭제 등)")
        print("  8: 데이터셋 분할 (학습/평가용)")
        print("\n  q: 종료")
        choice = input("선택: ")
        print("#"*60)
        
        if choice == '1':
            run_module_as_script('News_API.main', "뉴스 데이터 수집 및 가공")
        elif choice == '2':
            run_tokken_trainer()
        elif choice == '3':
            run_media_trainer()
        elif choice == '4':
            run_simple_script(TOKKEN_JUDGER_SCRIPT, "[Tokken] 텍스트 판별")
        elif choice == '5':
            run_simple_script(MEDIA_JUDGER_SCRIPT, "[Media] 출처 판별")
        elif choice == '6':
            run_simple_script(INTEGRATED_JUDGER_SCRIPT, "[통합] 최종 판별기")
        elif choice == '7':
            manage_datasets()
        elif choice == '8':
            run_splitter_with_selection()
        elif choice.lower() == 'q':
            print("프로그램을 종료합니다.")
            break
        else:
            print("잘못된 입력입니다. 다시 선택해주세요.")